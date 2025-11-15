"""
Data cleaning and normalization utilities for business records.
"""

import re
from typing import Dict, List


class BusinessNameNormalizer:
    """Normalize business names for fuzzy matching."""

    LEGAL_SUFFIXES = [
        r"\bincorporated\b",
        r"\binc\.?\b",
        r"\bcorporation\b",
        r"\bcorp\.?\b",
        r"\bcompany\b",
        r"\bco\.?\b",
        r"\blimited\b",
        r"\bltd\.?\b",
        r"\bllc\b",
        r"\bllp\b",
        r"\blp\b",
        r"\bplc\b",
    ]

    ABBREVIATION_MAP = {
        r"\b&\b": "and",
        r"\bintl\.?\b": "international",
        r"\bmfg\.?\b": "manufacturing",
        r"\bsvcs?\.?\b": "services",
        r"\btechs?\.?\b": "technology",
        r"\bmgmt\.?\b": "management",
        r"\bgrp\.?\b": "group",
        r"\bassocs?\.?\b": "associates",
        r"\bsys\.?\b": "systems",
    }

    @staticmethod
    def normalize(name: str) -> str:
        """
        Normalize business name for comparison.

        Args:
            name: Raw business name

        Returns:
            Normalized business name
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove legal suffixes
        for suffix in BusinessNameNormalizer.LEGAL_SUFFIXES:
            normalized = re.sub(suffix, "", normalized, flags=re.IGNORECASE)

        # Expand common abbreviations
        for abbr, full in BusinessNameNormalizer.ABBREVIATION_MAP.items():
            normalized = re.sub(abbr, full, normalized, flags=re.IGNORECASE)

        # Remove special characters except spaces
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # Collapse whitespace
        normalized = " ".join(normalized.split())

        return normalized.strip()


class AddressNormalizer:
    """Normalize address components."""

    STREET_ABBREV = {
        r"\bstreet\b": "st",
        r"\bavenue\b": "ave",
        r"\bboulevard\b": "blvd",
        r"\bdrive\b": "dr",
        r"\broad\b": "rd",
        r"\blane\b": "ln",
        r"\bcourt\b": "ct",
        r"\bparkway\b": "pkwy",
        r"\bplace\b": "pl",
    }

    STATE_ABBREV = {
        "california": "ca",
        "new york": "ny",
        "texas": "tx",
        "florida": "fl",
        "illinois": "il",
        "massachusetts": "ma",
        "washington": "wa",
        "colorado": "co",
        "michigan": "mi",
    }

    @staticmethod
    def normalize_street(street: str) -> str:
        """Normalize street address."""
        if not street:
            return ""

        normalized = street.lower()

        for full, abbr in AddressNormalizer.STREET_ABBREV.items():
            normalized = re.sub(full, abbr, normalized, flags=re.IGNORECASE)

        # Remove extra whitespace and punctuation
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = " ".join(normalized.split())

        return normalized.strip()

    @staticmethod
    def normalize_state(state: str) -> str:
        """Normalize state to abbreviation."""
        if not state:
            return ""

        state_lower = state.lower().strip()

        # Already abbreviated
        if len(state_lower) == 2 and state_lower.isalpha():
            return state_lower

        # Convert full name to abbreviation
        return AddressNormalizer.STATE_ABBREV.get(state_lower, state_lower)


class PhoneNormalizer:
    """Normalize phone numbers."""

    @staticmethod
    def normalize(phone: str) -> str:
        """Extract digits only from phone number."""
        if not phone:
            return ""

        # Keep digits only
        digits = re.sub(r"\D", "", phone)

        # Remove leading 1 for US numbers
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]

        return digits


def clean_dataframe(df, column_mapping: Dict[str, str]) -> Dict[str, List]:
    """
    Clean and normalize a pandas DataFrame.

    Args:
        df: Input DataFrame
        column_mapping: Mapping of {standard_name: source_column}

    Returns:
        Dictionary of cleaned data
    """
    cleaned = {}

    for standard_name, source_col in column_mapping.items():
        if source_col not in df.columns:
            cleaned[standard_name] = [""] * len(df)
            continue

        if standard_name == "normalized_name":
            cleaned[standard_name] = df[source_col].apply(
                BusinessNameNormalizer.normalize
            )
        elif standard_name == "normalized_street":
            cleaned[standard_name] = df[source_col].apply(AddressNormalizer.normalize_street)
        elif standard_name == "normalized_state":
            cleaned[standard_name] = df[source_col].apply(AddressNormalizer.normalize_state)
        elif standard_name == "normalized_phone":
            cleaned[standard_name] = df[source_col].apply(PhoneNormalizer.normalize)
        else:
            cleaned[standard_name] = df[source_col].fillna("").astype(str)

    return cleaned
