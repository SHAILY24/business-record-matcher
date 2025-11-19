# Business Record Matcher

Automated fuzzy matching system for business records using RapidFuzz and Playwright.

## Features

- **Data Cleaning**: Normalize business names, addresses, phone numbers
- **Fuzzy Matching**: RapidFuzz-powered matching with configurable thresholds
- **Multiple Strategies**: Phone-based exact matching + token-set name matching
- **Web Scraping**: Playwright-based browser automation for public directories
- **Confidence Scoring**: Transparent scoring based on match quality

## Installation

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Quick Start

```bash
# Run fuzzy matching on sample data
python src/main.py \
  --source data/input/sample_data_source1.csv \
  --target data/input/sample_data_source2.csv \
  --output data/output/matched_results.csv \
  --threshold 80
```

## Project Structure

```
business-matcher/
├── src/
│   ├── data_cleaner.py      # Normalization utilities
│   ├── fuzzy_matcher.py     # Matching engine
│   ├── web_scraper.py       # Browser automation
│   └── main.py              # Workflow orchestration
├── data/
│   ├── input/               # Source CSV files
│   └── output/              # Match results
├── tests/                   # Unit tests
└── pyproject.toml           # Project configuration
```

## Data Cleaning

Normalization handles:
- Legal entity suffixes (Inc, LLC, Corp, Ltd)
- Common abbreviations (& → and, Intl → International)
- Special characters and whitespace
- Phone number formatting (digits only)
- Address standardization (Street → St, Avenue → Ave)
- State abbreviations (California → CA)

## Fuzzy Matching

Uses RapidFuzz with two strategies:

1. **Exact Phone Match** (95% confidence)
   - Fastest, highest confidence
   - Normalized digits-only comparison

2. **Token-Set Name Match** (variable confidence)
   - Handles word order variations
   - "ABC Corp Inc" matches "Inc ABC Corporation"
   - Confidence based on similarity score

## Confidence Scoring

- **High (80-100)**: Strong match, safe to auto-merge
- **Medium (60-79)**: Probable match, review recommended
- **Low (<60)**: Weak match, manual review required

## Web Scraping

Browser automation with Playwright:

```python
from src.web_scraper import BusinessDirectoryScraper

scraper = BusinessDirectoryScraper(headless=True)
results = scraper.scrape_yellowpages(
    search_term="restaurants",
    location="New York, NY",
    max_results=10
)
```

## Output Format

CSV with columns:
- `match_status`: phone | fuzzy_name | unmatched
- `confidence_score`: 0-100
- `name_similarity`: 0-100
- `phone_match`: Yes/No
- `source_*`: Original source record fields
- `target_*`: Matched target record fields

## Example Results

```
MATCH SUMMARY
==============================================================
Total records: 10
Matched: 9 (90.0%)
Unmatched: 1

Match Types:
  Phone matches: 6
  Fuzzy name matches: 3

Confidence Distribution:
  High (80-100): 8
  Medium (60-79): 1
  Low (<60): 1
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Format code
black src/

# Lint
ruff check src/

# Run tests
pytest tests/
```

## Use Cases

- CRM deduplication
- Vendor database consolidation
- Lead enrichment workflows
- Multi-source data merging
- Business directory matching

## Technical Details

- **Language**: Python 3.10+
- **Fuzzy Matching**: RapidFuzz 3.5+ (C++ backend for speed)
- **Web Automation**: Playwright 1.40+
- **Data Processing**: Pandas 2.1+

## License

MIT
