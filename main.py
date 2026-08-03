"""
DOCX Mailing Address Labels Generator
------------------
Description: Main execution script that defines input/output configurations
             and calls the external labeling engine to process home owner data.

Author: Joseph Adogeri
Version: 1.0.0
Since: 2026-08-03
File: main.py
License: MIT
"""


from labels_engine import generate_word_labels_engine

if __name__ == "__main__":
    # Specify your input file path and your output file path here
    csv_file = "home_owners.csv"
    output_file = "avery_5160_labels.docx"

    # Run the label engine
    generate_word_labels_engine(csv_file, output_file)
