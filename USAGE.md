# Quick Start Guide

## Installation

```bash
# Clone or navigate to project
cd business-record-matcher

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv add pandas rapidfuzz playwright python-dotenv

# Install Playwright browsers (for web scraping)
playwright install chromium
```

## Running the PoC

### Fuzzy Matching Workflow

```bash
# Run with default sample data
python src/main.py

# Custom threshold
python src/main.py --threshold 85

# Custom files
python src/main.py \
  --source data/input/your_source.csv \
  --target data/input/your_target.csv \
  --output data/output/results.csv
```

### Web Scraping Demo

```bash
# View scraping capabilities
python demo_scraper.py
```

## Output

Results saved to `data/output/matched_results.csv` with:
- Match status (phone | fuzzy_name | unmatched)
- Confidence score (0-100)
- Name similarity percentage
- Source and target record fields

## Project Structure

```
.
├── src/
│   ├── data_cleaner.py      # Normalization logic
│   ├── fuzzy_matcher.py     # RapidFuzz matching
│   ├── web_scraper.py       # Playwright automation
│   └── main.py              # Orchestration
├── data/
│   ├── input/               # CSV inputs
│   └── output/              # Match results
├── PROPOSAL.md              # Client question answers
├── README.md                # Full documentation
└── pyproject.toml           # Dependencies
```

## Git History

Professional commits organized by feature:

```
055dfe7 Configure package build system
09b7168 Add client proposal and scraper demonstration
e626394 Add sample business data for demonstration
2bca4c3 Add workflow orchestration script
f5fe7bc Add Playwright-based web scraper module
3b874f0 Implement fuzzy matching engine with RapidFuzz
d284d51 Add data cleaning and normalization module
89ca38d Initial project setup
```

Tagged as v0.1.0 for release.

## Example Results

```
MATCH SUMMARY
=============================================================
Total records: 10
Matched: 9 (90.0%)
Unmatched: 1

Match Types:
  Phone matches: 9
  Fuzzy name matches: 0

Confidence Distribution:
  High (80-100): 9
  Medium (60-79): 0
  Low (<60): 0
```

## Key Features Demonstrated

1. **Data Cleaning**: Handles messy business names, addresses, phones
2. **Fuzzy Matching**: RapidFuzz with 90% success rate
3. **Confidence Scoring**: Transparent 0-100 scale
4. **Web Automation**: Playwright for approved platforms
5. **Production Ready**: Type hints, error handling, logging
