# Dynamic Website Scraper

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
- Open eyewears_scrapper folder in VSCODE, Navigate to framedirect or glassdata1 folder
- Open `framedirect_pages.py` or `glasses_pag.py` and run in terminal one at a time.
- Each scripts scrape product data from different dynamic websites and save them into a csv and json out put.
- Check created folder for the output data.

## Output
- `output.csv`: Scraped data in CSV format
- `output.json`: Scraped data in JSON format

## Notes
- Output data in the subfolders mark the second phase of this project.
- framedirect_pages.py and glasses_pag.py are able to scrape multiple pages
- For dynamic websites, Selenium or similar tools are used to render JavaScript content.
- Update the target URL and scraping logic in `glasses.py` or `framedirect.py` as  needed for your use case(Thes scripts scrape only the first page).

## License
MIT.
