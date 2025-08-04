#!/usr/bin/env python3
"""
Script to combine all Excel files in data/processed/ into one comprehensive knowledge base.
This script will:
1. Find all .xlsx files in the data/processed/ directory
2. Read each file and combine them into a single DataFrame
3. Remove duplicates based on question content
4. Sort by date and topic
5. Save as a single Excel file named 'knowledge_base.xlsx'
"""

import os
import pandas as pd
import glob
from pathlib import Path
import argparse
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_excel_files(data_dir: str = "data/processed") -> list:
    """
    Find all Excel files in the specified directory.
    
    Args:
        data_dir: Directory to search for Excel files
        
    Returns:
        List of file paths
    """
    pattern = os.path.join(data_dir, "*.xlsx")
    files = glob.glob(pattern)
    files.sort()  # Sort alphabetically for consistent processing order
    return files

def read_excel_file(file_path: str) -> pd.DataFrame:
    """
    Read an Excel file and return a DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        DataFrame containing the Excel data
    """
    try:
        df = pd.read_excel(file_path)
        logger.info(f"✅ Successfully read {file_path} - {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"❌ Error reading {file_path}: {e}")
        return pd.DataFrame()

def combine_excel_files(files: list) -> pd.DataFrame:
    """
    Combine multiple Excel files into a single DataFrame.
    
    Args:
        files: List of file paths to combine
        
    Returns:
        Combined DataFrame
    """
    if not files:
        logger.error("No Excel files found!")
        return pd.DataFrame()
    
    combined_data = []
    total_rows = 0
    
    for file_path in files:
        df = read_excel_file(file_path)
        if not df.empty:
            combined_data.append(df)
            total_rows += len(df)
    
    if not combined_data:
        logger.error("No valid data found in any files!")
        return pd.DataFrame()
    
    # Combine all DataFrames
    combined_df = pd.concat(combined_data, ignore_index=True)
    logger.info(f"📊 Combined {len(files)} files with {total_rows} total rows")
    
    return combined_df

def clean_and_deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the data and remove duplicates.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    initial_count = len(df)
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Remove duplicates based on question content (case-insensitive)
    df['Question_Lower'] = df['Question'].str.lower().str.strip()
    df = df.drop_duplicates(subset=['Question_Lower'], keep='first')
    df = df.drop(columns=['Question_Lower'])
    
    # Fix date formatting and convert to proper datetime
    if 'Date' in df.columns:
        # Convert string dates like "January 1 2023" to proper datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%B %d %Y', errors='coerce')
        # For any dates that failed parsing, try alternative formats
        mask = df['Date'].isna()
        if mask.any():
            df.loc[mask, 'Date'] = pd.to_datetime(df.loc[mask, 'Date'], errors='coerce')
        
        df = df.sort_values(['Date', 'Topic'], na_position='last')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    final_count = len(df)
    removed_count = initial_count - final_count
    
    logger.info(f"🧹 Cleaned data: {removed_count} duplicates removed")
    logger.info(f"📈 Final dataset: {final_count} unique questions")
    
    return df

def save_knowledge_base(df: pd.DataFrame, output_file: str = "knowledge_base.xlsx") -> None:
    """
    Save the combined knowledge base to an Excel file.
    
    Args:
        df: DataFrame to save
        output_file: Output file path
    """
    if df.empty:
        logger.error("No data to save!")
        return
    
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save to Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Knowledge_Base', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Knowledge_Base']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"💾 Knowledge base saved to: {output_file}")
        logger.info(f"📊 Total questions: {len(df)}")
        
        # Print summary statistics
        print_summary(df)
        
    except Exception as e:
        logger.error(f"❌ Error saving knowledge base: {e}")

def print_summary(df: pd.DataFrame) -> None:
    """
    Print summary statistics about the knowledge base.
    
    Args:
        df: DataFrame to analyze
    """
    print("\n" + "="*50)
    print("📊 KNOWLEDGE BASE SUMMARY")
    print("="*50)
    
    print(f"Total Questions: {len(df)}")
    
    if 'Topic' in df.columns:
        print(f"\nTopics Distribution:")
        topic_counts = df['Topic'].value_counts()
        for topic, count in topic_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {topic}: {count} ({percentage:.1f}%)")
    
    if 'Difficulty' in df.columns:
        print(f"\nDifficulty Distribution:")
        difficulty_counts = df['Difficulty'].value_counts()
        for difficulty, count in difficulty_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {difficulty}: {count} ({percentage:.1f}%)")
    
    if 'Date' in df.columns:
        print(f"\nDate Range:")
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        print(f"  From: {min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else 'Unknown'}")
        print(f"  To: {max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else 'Unknown'}")
    

    
    print("="*50)

def main():
    """Main function to orchestrate the knowledge base creation."""
    parser = argparse.ArgumentParser(
        description="Combine all Excel files into a single knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/combine_knowledge_base.py
  python scripts/combine_knowledge_base.py --output data/knowledge_base.xlsx
  python scripts/combine_knowledge_base.py --data-dir data/processed --output knowledge_base.xlsx
        """
    )
    
    parser.add_argument(
        "--data-dir",
        default="data/processed",
        help="Directory containing Excel files (default: data/processed)"
    )
    
    parser.add_argument(
        "--output",
        default="knowledge_base.xlsx",
        help="Output file path (default: knowledge_base.xlsx)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Starting knowledge base creation...")
    logger.info(f"📁 Searching for Excel files in: {args.data_dir}")
    
    # Find Excel files
    excel_files = find_excel_files(args.data_dir)
    
    if not excel_files:
        logger.error(f"No Excel files found in {args.data_dir}")
        return
    
    logger.info(f"📋 Found {len(excel_files)} Excel files")
    
    # Combine files
    combined_df = combine_excel_files(excel_files)
    
    if combined_df.empty:
        logger.error("No data could be combined!")
        return
    
    # Clean and deduplicate
    cleaned_df = clean_and_deduplicate(combined_df)
    
    # Save knowledge base
    save_knowledge_base(cleaned_df, args.output)
    
    logger.info("✅ Knowledge base creation completed successfully!")

if __name__ == "__main__":
    main() 