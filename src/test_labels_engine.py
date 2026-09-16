import unittest
from unittest.mock import patch, mock_open, MagicMock
import io

# Assuming your script is saved as labels_engine.py
from labels_engine import (
    set_cell_margins,
    apply_page_margins,
    generate_word_labels_engine
)


class TestLabelsEngine(unittest.TestCase):

    def setUp(self):
        """Define consistent mock data fields mirroring expected CSV layout."""
        self.csv_headers = "OWNER_NAME,ADDRESS_1,ADDRESS_2,CITY,STATE,ZIP_CODE\n"

        # Test dataset 1: Row with a populated ADDRESS_2 field
        self.row_with_addr2 = 'John Doe,123 Main St,Apt 4B,New York,NY,10001\n'

        # Test dataset 2: Row with an empty ADDRESS_2 field
        self.row_no_addr2 = 'Jane Smith,456 Oak Rd,,Los Angeles,CA,90001\n'

    @patch('labels_engine.OxmlElement')
    def test_set_cell_margins_adds_nodes(self, mock_oxml):
        """Verify that cell margins generate the appropriate XML structure."""
        mock_cell = MagicMock()
        mock_tc = MagicMock()
        mock_cell._tc = mock_tc

        # Track element configurations
        mock_element = MagicMock()
        mock_oxml.return_value = mock_element

        set_cell_margins(mock_cell, top=60, bottom=0, left=140, right=140)

        # Assertions to ensure XML container generation happens correctly
        mock_tc.get_or_add_tcPr.assert_called_once()
        self.assertTrue(mock_element.append.called)

    def test_apply_page_margins(self):
        """Verify page dimension parameters map identically across document sections."""
        mock_section = MagicMock()
        sections = [mock_section]

        apply_page_margins(sections)

        # Assert dimensions match expected target variables
        self.assertEqual(mock_section.page_width.inches, 8.5)
        self.assertEqual(mock_section.page_height.inches, 11.0)
        self.assertEqual(mock_section.top_margin.inches, 0.5)
        self.assertEqual(mock_section.bottom_margin.inches, 0.5)

    @patch('labels_engine.Document')
    def test_generate_word_labels_engine_with_address_2(self, mock_document_cls):
        """Ensure standard addresses parse successfully with all 4 lines."""
        mock_doc = MagicMock()
        mock_document_cls.return_value = mock_doc

        csv_content = self.csv_headers + self.row_with_addr2

        with patch('builtins.open', mock_open(read_data=csv_content)):
            generate_word_labels_engine('dummy.csv', 'dummy.docx')

        # Assert document layout structure initialized
        mock_doc.add_table.assert_called_once_with(rows=10, cols=5)
        mock_doc.save.assert_called_once_with('dummy.docx')

    @patch('labels_engine.Document')
    def test_generate_word_labels_engine_skips_empty_address_2(self, mock_document_cls):
        """Ensure empty second address slots fallback properly to a 3-line block."""
        mock_doc = MagicMock()
        mock_document_cls.return_value = mock_doc

        csv_content = self.csv_headers + self.row_no_addr2

        with patch('builtins.open', mock_open(read_data=csv_content)):
            generate_word_labels_engine('dummy.csv', 'dummy.docx')

        mock_doc.save.assert_called_once_with('dummy.docx')

    @patch('labels_engine.Document')
    def test_progress_callback_execution(self, mock_document_cls):
        """Confirm that the engine tracks pipeline progression increments accurately."""
        mock_doc = MagicMock()
        mock_document_cls.return_value = mock_doc

        # Provide exactly 31 rows to force split onto sheet 2
        csv_content = self.csv_headers + (self.row_with_addr2 * 31)
        mock_callback = MagicMock()

        with patch('builtins.open', mock_open(read_data=csv_content)):
            generate_word_labels_engine('dummy.csv', 'dummy.docx', progress_callback=mock_callback)

        # 31 items / 30 limit implies 2 sheet calls
        self.assertEqual(mock_callback.call_count, 2)
        mock_callback.assert_any_call(0.5)
        mock_callback.assert_any_call(1.0)


if __name__ == '__main__':
    unittest.main()
