"""
DOCX Mailing Address Labels Generator - Main application runner
------------------
Description: Main execution script that defines input/output configurations
             and calls the external labeling engine to process home owner data.

Author: Joseph Adogeri
Version: 1.0.0
Since: 2026-08-03
File: main.py
License: MIT
"""

import os
import sys

from dotenv import load_dotenv

from src.labels_engine import generate_word_labels_engine

# Load the variables from the local .env file
load_dotenv()

csv_file = os.environ.get("SOURCE_CSV_FILE", r"PATH TO PDF FILE")
docx_file = os.environ.get("OUTPUT_DOCX_FILE", r"PATH TO OUTPUT FOLDER/ DIRECTORY")


def main() -> None:
    # Defensive check: Ensure both environment variables exist before running
    if not all([csv_file, docx_file]):
        print("❌ Error: Missing configuration paths in your .env file or fallbacks!")
        return

    print("\nStarting Generating Mailing Address Labels Service...")
    print(f"-> Source CSV: {csv_file}")
    print(f"-> Destination DOCX: {docx_file}\n")
    print("Finished Generating Mailing Address Labels Service...")


    generate_word_labels_engine(csv_file, docx_file)

if __name__ == "__main__":
    main()
    sys.exit(0)
