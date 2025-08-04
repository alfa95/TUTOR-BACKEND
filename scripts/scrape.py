import requests
from bs4 import BeautifulSoup
import openpyxl
import re
import time
import random
import json
import os
from datetime import datetime, timedelta
import argparse
from dotenv import load_dotenv
import google.generativeai as genai

# === Load environment variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(GEMINI_API_KEY)
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# === Generate date-based URLs ===
def generate_urls(start_date: str, end_date: str) -> list:
    urls = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    while start <= end:
        day = start.day
        month = start.strftime('%B').lower()
        year = start.year
        url = f"https://www.gktoday.in/daily-current-affairs-quiz-{month}-{day}-{year}/"
        urls.append(url)
        start += timedelta(days=1)
    return urls

# === Extract date from URL ===
def extract_date_from_url(url: str) -> str:
    match = re.search(r'quiz-(.*?)\/?$', url)
    return match.group(1).replace('-', ' ').title() if match else 'Unknown'

# === Use Gemini to classify each question ===
def classify_question_topic_gemini(data_batch):
    prompt = f"""Classify each question into:
1. A topic: Polity, Economy, Geography, Science & Tech, Environment, Current Affairs, Miscellaneous
2. A difficulty level: Easy, Medium, Hard

Return a JSON list of dicts with:
date, question, option1, option2, option3, option4, answer, explanation, topic, difficulty

```json
{json.dumps(data_batch, indent=2)}
```"""

    response = gemini_model.generate_content(prompt)
    json_text = response.text.strip()

    match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
    parsed_json = json.loads(match.group(1)) if match else json.loads(json_text)
    return parsed_json

# === Scrape questions from a single page ===
def scrape_quiz_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Page not found: {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    quiz_blocks = soup.select('div.wp_quiz_question.testclass')
    if not quiz_blocks:
        print(f"⚠️ No quiz questions found on: {url}")
        return []

    quiz_date = extract_date_from_url(url)
    quiz_data = []

    for question_block in quiz_blocks:
        question_text = question_block.get_text(strip=True)
        question_text = re.sub(r'^\d+\.\s*', '', question_text)

        parent = question_block.find_parent('div')
        options_div = parent.find('div', class_='wp_quiz_question_options')
        answer_div = parent.find('div', class_='ques_answer')
        notes_div = parent.find('div', class_='answer_hint')

        options_raw = options_div.decode_contents().split('<br/>') if options_div else []
        options_clean = [re.sub(r'^\[[A-D]\]\s*', '', o.strip()) for o in options_raw]
        options_list = options_clean + [''] * (4 - len(options_clean))

        answer_full = answer_div.get_text(strip=True).replace('Correct Answer:', '') if answer_div else ''
        answer_match = re.search(r'\[(.*?)\]', answer_full)
        clean_answer = answer_match.group(1) if answer_match else answer_full.strip()

        notes_text = notes_div.get_text(strip=True).replace('Notes:', '') if notes_div else ''

        quiz_data.append([quiz_date, question_text] + options_list[:4] + [clean_answer, notes_text])

    # Prepare payload for Gemini classification
    payload = []
    for row in quiz_data:
        payload.append({
            "date": row[0],
            "question": row[1],
            "option1": row[2],
            "option2": row[3],
            "option3": row[4],
            "option4": row[5],
            "answer": row[6],
            "explanation": row[7]
        })

    # Classify topic + difficulty
    try:
        enriched_data = classify_question_topic_gemini(payload)
        final_data = []
        for row, enriched in zip(quiz_data, enriched_data):
            topic = enriched.get("topic", "Unclassified")
            difficulty = enriched.get("difficulty", "Medium")
            row.extend([topic, difficulty])
            final_data.append(row)
        return final_data
    except Exception as e:
        print(f"⚠️ Gemini classification failed for {url}: {e}")
        return [row + ["Unclassified", "Medium"] for row in quiz_data]

# === Save results to Excel ===
def save_to_excel(data: list, filename: str):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'GKToday'
    ws.append([
        'Date', 'Question', 'Option A', 'Option B', 'Option C', 'Option D',
        'Correct Answer', 'Notes', 'Topic', 'Difficulty'
    ])
    for row in data:
        ws.append(row)
    wb.save(filename)
    print(f"\n✅ Saved {len(data)} questions to: {filename}")

# === Main execution ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", default="gktoday_quiz.xlsx", help="Output Excel filename")
    args = parser.parse_args()

    urls = generate_urls(args.start, args.end)
    all_data = []

    for url in urls:
        print(f"🔍 Scraping: {url}")
        quiz_data = scrape_quiz_data(url)
        all_data.extend(quiz_data)
        time.sleep(random.uniform(2, 4))  # polite pause

    if all_data:
        save_to_excel(all_data, args.output)
    else:
        print("❌ No data collected.")

if __name__ == "__main__":
    main()
