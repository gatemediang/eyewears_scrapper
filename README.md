# Demo: Dynamic Website Scraper

This project demonstrates how to scrape data from dynamic websites using Python and save the results into both CSV and JSON formats.

## Features
- Scrapes data from dynamic websites (JavaScript-rendered content)
- Saves scraped data into `csv` and `json` files
- Example workflow provided in `framedirect.ipynb`

## Requirements
- Python 3.7+
- Recommended: Use a virtual environment
- Install required packages (see below)

## Setup
1. **Create a virtual environment** (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
   Or install packages directly in the notebook using:
   ```python
   !pip install requests beautifulsoup4 selenium webdriver-manager
   ```

## Usage
- Open `framedirect.ipynb` in Jupyter Notebook or `framedirect.py` in VS Code.
- Run the cells to scrape data from the target website.
- The notebook will save the results into `output.csv` and `output.json`.

## Output
- `output.csv`: Scraped data in CSV format
- `output.json`: Scraped data in JSON format

## Notes
- For dynamic websites, Selenium or similar tools are used to render JavaScript content.
- Update the target URL and scraping logic in `framedirect.ipynb` or `framedirect.py` as needed for your use case.

## License
MIT.
