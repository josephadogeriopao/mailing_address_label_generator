## Summary
This PR introduces the **Mailing Address Labels Generator**, a Python desktop utility designed to parse bulk homeowner mailing records and generate print-ready Microsoft Word (`.docx`) documents formatted to standard **Avery 5160** (3x10 grid) specifications.

## Key Changes
- **Avery 5160 Matrix Engine (`labels_engine.py`)**: Implemented CSV data extraction and multi-page table generation with low-level OpenXML margin/padding adjustments and defensive line normalization for missing or optional address fields.
- **Desktop GUI (`app.py`)**: Built a modern dark-contrast interface using `CustomTkinter` with background threading callbacks to keep the UI responsive during file processing.
- **CLI & Orchestration (`main.py`)**: Added a standalone command-line entry point for direct execution without launching the GUI.
- **Unit Testing & CI/CD (`test_labels_engine.py`, `.github/workflows/python-app.yml`)**: Added 5 unit test suites covering core engine logic and configured GitHub Actions to run automated checks on pushes and pull requests.
- **Packaging & Documentation**: Configured PyInstaller support for building standalone `.exe` distributions with custom icons (`app_icon.ico`, `app_icon.png`) and added setup/usage documentation.

## Repository Structure Added
- `main.py` — Core entry point & orchestration
- `labels_engine.py` — CSV parsing & OpenXML Word generation engine
- `test_labels_engine.py` — Automated unit test suites
- `app.py` — CustomTkinter desktop application
- `.github/workflows/python-app.yml` — GitHub Actions CI workflow
- `requirements.txt` & `commands.txt` — Dependencies and CLI reference scripts

## How to Test
1. Create and activate a Python 3.12+ virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run unit tests: `python -m unittest discover -s src -p "test_labels_engine.py"`
4. Launch the desktop app (`python app.py`) or CLI script (`python main.py`) to verify `.docx` label output.
