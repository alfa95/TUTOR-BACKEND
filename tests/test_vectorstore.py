import os
import pytest
from src.vector_store.qdrant_utils import load_excel_and_index, search_similar_questions

@pytest.fixture
def sample_file():
    return "tests/fixtures/sample_data.xlsx"

def test_qdrant_indexing(sample_file="tests/fixtures/sample_data.xlsx"):
    load_excel_and_index(sample_file)

    results = search_similar_questions("Krishi Nivesh Portal", filters={"topic": "Polity"})

    # Debug: Print the retrieved results for visual validation
    for r in results:
        print(f"\n🔍 Retrieved → {r['question']} [Topic: {r['topic']}] (Score: {r['score']:.2f})")

    # Assert we got at least one match with topic filter
    assert any(r["topic"] == "Polity" for r in results), "No relevant results returned"

