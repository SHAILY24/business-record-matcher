"""
Web scraper for extracting business information from public directories.

Uses Playwright for robust browser automation with dynamic content handling.
"""

import json
import time
from typing import Dict, List, Optional

from playwright.sync_api import Page, sync_playwright


class BusinessDirectoryScraper:
    """Scrape business information from public directories."""

    def __init__(self, headless: bool = True):
        """
        Initialize scraper.

        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self.results: List[Dict] = []

    def scrape_yellowpages(
        self, search_term: str, location: str, max_results: int = 10
    ) -> List[Dict]:
        """
        Scrape business listings from Yellow Pages.

        Args:
            search_term: Business category or name
            location: City, state or zip code
            max_results: Maximum number of results to scrape

        Returns:
            List of business records
        """
        businesses = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                # Navigate to Yellow Pages search
                search_url = (
                    f"https://www.yellowpages.com/search?"
                    f"search_terms={search_term.replace(' ', '+')}&"
                    f"geo_location_terms={location.replace(' ', '+')}"
                )

                print(f"Navigating to: {search_url}")
                page.goto(search_url, wait_until="networkidle", timeout=30000)

                # Wait for results to load
                page.wait_for_selector(".result", timeout=10000)

                # Extract business information
                listings = page.locator(".result").all()

                for idx, listing in enumerate(listings[:max_results]):
                    if idx >= max_results:
                        break

                    try:
                        business = self._extract_business_info(listing)
                        if business:
                            businesses.append(business)
                            print(f"Extracted: {business.get('name', 'N/A')}")
                    except Exception as e:
                        print(f"Error extracting business {idx}: {e}")
                        continue

                    # Rate limiting
                    time.sleep(0.5)

            except Exception as e:
                print(f"Scraping error: {e}")

            finally:
                browser.close()

        self.results = businesses
        return businesses

    def _extract_business_info(self, listing) -> Optional[Dict]:
        """
        Extract structured business information from a listing element.

        Args:
            listing: Playwright locator for business listing

        Returns:
            Dictionary with business information
        """
        try:
            # Extract business name
            name_elem = listing.locator(".business-name")
            name = name_elem.text_content().strip() if name_elem.count() > 0 else ""

            # Extract address
            street_elem = listing.locator(".street-address")
            street = street_elem.text_content().strip() if street_elem.count() > 0 else ""

            locality_elem = listing.locator(".locality")
            locality = locality_elem.text_content().strip() if locality_elem.count() > 0 else ""

            # Extract phone
            phone_elem = listing.locator(".phones")
            phone = phone_elem.text_content().strip() if phone_elem.count() > 0 else ""

            # Extract website if available
            website_elem = listing.locator(".track-visit-website")
            website = website_elem.get_attribute("href") if website_elem.count() > 0 else ""

            if not name:
                return None

            return {
                "name": name,
                "street": street,
                "locality": locality,
                "phone": phone,
                "website": website,
                "source": "yellowpages",
            }

        except Exception as e:
            print(f"Error extracting business info: {e}")
            return None

    def scrape_generic_directory(self, url: str, selectors: Dict[str, str]) -> List[Dict]:
        """
        Generic scraper for business directories with custom selectors.

        Args:
            url: Target URL
            selectors: Dictionary mapping fields to CSS selectors

        Returns:
            List of business records
        """
        businesses = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                print(f"Navigating to: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait for listings container
                if "container" in selectors:
                    page.wait_for_selector(selectors["container"], timeout=10000)
                    listings = page.locator(selectors["container"]).all()

                    for listing in listings:
                        business = {}

                        for field, selector in selectors.items():
                            if field == "container":
                                continue

                            try:
                                elem = listing.locator(selector)
                                business[field] = (
                                    elem.text_content().strip() if elem.count() > 0 else ""
                                )
                            except:
                                business[field] = ""

                        if business.get("name"):
                            businesses.append(business)

            except Exception as e:
                print(f"Generic scraping error: {e}")

            finally:
                browser.close()

        return businesses

    def save_results(self, filename: str, format: str = "json"):
        """
        Save scraping results to file.

        Args:
            filename: Output filename
            format: Output format (json or csv)
        """
        if format == "json":
            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"Saved {len(self.results)} records to {filename}")

        elif format == "csv":
            import pandas as pd

            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False)
            print(f"Saved {len(self.results)} records to {filename}")


def demo_scraper():
    """Demonstrate web scraping capabilities."""
    scraper = BusinessDirectoryScraper(headless=False)

    # Example: Scrape restaurants in New York
    results = scraper.scrape_yellowpages(
        search_term="restaurants", location="New York, NY", max_results=5
    )

    print(f"\nScraped {len(results)} businesses")
    for idx, business in enumerate(results, 1):
        print(f"\n{idx}. {business.get('name', 'N/A')}")
        print(f"   Address: {business.get('street', 'N/A')}, {business.get('locality', 'N/A')}")
        print(f"   Phone: {business.get('phone', 'N/A')}")

    return results


if __name__ == "__main__":
    demo_scraper()
