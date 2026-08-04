"""
DOCX Mailing Address Labels Generator
------------------
Description: Contains the core function to read CSV file, extract
             Owner Name, Address 1, Address 2, City, State and Zip Code and
             bulk create labels in generated .docx file.

Author: Joseph Adogeri
Version: 1.0.4
Since: 2026-08-03
File: labels_engine.py
License: MIT
"""


import csv
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_margins(cell, top=60, bottom=0, left=140, right=140):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def apply_page_margins(sections):
    for section in sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.19)
        section.right_margin = Inches(0.19)


def generate_word_labels_engine(csv_filename, docx_filename, progress_callback=None):
    labels_data = []
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            lines = [row['OWNER_NAME'].strip()]
            lines.append(row['ADDRESS_1'].strip())

            if row.get('ADDRESS_2') and row['ADDRESS_2'].strip():
                lines.append(row['ADDRESS_2'].strip())

            city_state_zip = f"{row['CITY'].strip()}, {row['STATE'].strip()} {row['ZIP_CODE'].strip()}"
            lines.append(city_state_zip)

            labels_data.append(lines)

    total_labels = len(labels_data)
    labels_per_sheet = 30

    if total_labels == 0:
        return

    doc = Document()
    apply_page_margins(doc.sections)

    num_sheets = (total_labels + labels_per_sheet - 1) // labels_per_sheet

    for sheet_idx in range(num_sheets):
        if progress_callback:
            progress_callback((sheet_idx + 1) / num_sheets)

        start_idx = sheet_idx * labels_per_sheet
        end_idx = min(start_idx + labels_per_sheet, total_labels)
        sheet_chunk = labels_data[start_idx:end_idx]

        if sheet_idx > 0:
            new_section = doc.add_section()
            apply_page_margins([new_section])

        table = doc.add_table(rows=10, cols=5)
        table.autofit = False

        col_mapping = {0: 0, 1: 2, 2: 4}
        gap_columns = (1, 3)

        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trHeight = OxmlElement('w:trHeight')
            trHeight.set(qn('w:val'), str(1425))
            trHeight.set(qn('w:hRule'), 'exact')
            trPr.append(trHeight)

            cantSplit = OxmlElement('w:cantSplit')
            trPr.append(cantSplit)

            for c_idx in (0, 2, 4):
                cell = row.cells[c_idx]
                cell.width = Inches(2.63)
                if c_idx == 0:
                    set_cell_margins(cell, top=60, bottom=0, left=280, right=140)
                else:
                    set_cell_margins(cell, top=60, bottom=0, left=140, right=140)

            for c_idx in gap_columns:
                cell = row.cells[c_idx]
                cell.width = Inches(0.12)
                set_cell_margins(cell, top=0, bottom=0, left=0, right=0)

        for index, lines in enumerate(sheet_chunk):
            row_idx = index // 3
            label_col = index % 3
            col_idx = col_mapping[label_col]

            cell = table.cell(row_idx, col_idx)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)

            name_run = p.add_run(lines[0])
            name_run.font.name = 'Aptos'
            name_run.font.size = Pt(10)
            name_run.bold = True

            for line in lines[1:]:
                p.add_run("\n")
                addr_run = p.add_run(line)
                addr_run.font.name = 'Aptos'
                addr_run.font.size = Pt(9)

    # Fix: Safely intercept the absolute trailing layout paragraph mark.
    # We strip its margins and shrink its structural font size down to 1pt.
    # This tricks Word into fitting the trailing empty line onto the sheet boundary.
    if doc.paragraphs:
        final_p = doc.paragraphs[-1]
        final_p.paragraph_format.space_before = Pt(0)
        final_p.paragraph_format.space_after = Pt(0)
        final_p.paragraph_format.line_spacing = Pt(1)

        # Inject an ultra-small text run context to lock the line size down
        micro_run = final_p.add_run()
        micro_run.font.size = Pt(1)

    doc.save(docx_filename)
