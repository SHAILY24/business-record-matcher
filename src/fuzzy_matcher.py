"""
Fuzzy matching engine using RapidFuzz for business record matching.
"""

from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz, process


class FuzzyMatcher:
    """Fuzzy matching for business records."""

    def __init__(self, threshold: int = 80):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum similarity score (0-100) for matches
        """
        self.threshold = threshold

    def match_name(self, query: str, choices: List[str]) -> Optional[Tuple[str, float]]:
        """
        Find best match for a business name.

        Uses token_set_ratio to handle word order variations.

        Args:
            query: Business name to match
            choices: List of candidate names

        Returns:
            Tuple of (best_match, score) or None if below threshold
        """
        if not query or not choices:
            return None

        result = process.extractOne(
            query, choices, scorer=fuzz.token_set_ratio, score_cutoff=self.threshold
        )

        if result:
            return (result[0], result[1])
        return None

    def match_records(
        self,
        source_records: List[Dict],
        target_records: List[Dict],
        name_key: str = "normalized_name",
        phone_key: str = "normalized_phone",
    ) -> List[Dict]:
        """
        Match records from source to target using multiple strategies.

        Args:
            source_records: List of source business records
            target_records: List of target business records
            name_key: Key for normalized business name
            phone_key: Key for normalized phone number

        Returns:
            List of matched records with confidence scores
        """
        matches = []

        # Build lookup dictionaries for target records
        target_names = [r[name_key] for r in target_records]
        target_phones = {r[phone_key]: i for i, r in enumerate(target_records) if r[phone_key]}

        for src_idx, src_record in enumerate(source_records):
            match_info = {
                "source_index": src_idx,
                "source_record": src_record,
                "target_index": None,
                "target_record": None,
                "match_type": "unmatched",
                "confidence": 0.0,
                "name_similarity": 0.0,
                "phone_match": False,
            }

            # Strategy 1: Exact phone match (highest confidence)
            src_phone = src_record.get(phone_key, "")
            if src_phone and src_phone in target_phones:
                tgt_idx = target_phones[src_phone]
                match_info.update(
                    {
                        "target_index": tgt_idx,
                        "target_record": target_records[tgt_idx],
                        "match_type": "phone",
                        "confidence": 95.0,
                        "phone_match": True,
                    }
                )
                matches.append(match_info)
                continue

            # Strategy 2: Fuzzy name matching
            src_name = src_record.get(name_key, "")
            if src_name:
                name_match = self.match_name(src_name, target_names)
                if name_match:
                    best_match_name, name_score = name_match
                    tgt_idx = target_names.index(best_match_name)

                    # Calculate overall confidence
                    confidence = self._calculate_confidence(
                        name_score=name_score,
                        phone_match=False,
                    )

                    match_info.update(
                        {
                            "target_index": tgt_idx,
                            "target_record": target_records[tgt_idx],
                            "match_type": "fuzzy_name",
                            "confidence": confidence,
                            "name_similarity": name_score,
                            "phone_match": False,
                        }
                    )

            matches.append(match_info)

        return matches

    @staticmethod
    def _calculate_confidence(name_score: float, phone_match: bool) -> float:
        """
        Calculate overall confidence score.

        Args:
            name_score: Name similarity score (0-100)
            phone_match: Whether phone numbers matched

        Returns:
            Overall confidence score
        """
        if phone_match and name_score >= 80:
            return 98.0
        elif phone_match:
            return 90.0
        elif name_score >= 95:
            return 95.0
        elif name_score >= 90:
            return 85.0
        elif name_score >= 85:
            return 75.0
        elif name_score >= 80:
            return 65.0
        else:
            return name_score * 0.6

    def get_match_summary(self, matches: List[Dict]) -> Dict[str, int]:
        """
        Get summary statistics of matching results.

        Args:
            matches: List of match results

        Returns:
            Dictionary with match statistics
        """
        summary = {
            "total": len(matches),
            "matched": 0,
            "unmatched": 0,
            "phone_matches": 0,
            "fuzzy_matches": 0,
            "high_confidence": 0,  # >= 80
            "medium_confidence": 0,  # 60-79
            "low_confidence": 0,  # < 60
        }

        for match in matches:
            if match["match_type"] == "unmatched":
                summary["unmatched"] += 1
            else:
                summary["matched"] += 1

                if match["match_type"] == "phone":
                    summary["phone_matches"] += 1
                elif match["match_type"] == "fuzzy_name":
                    summary["fuzzy_matches"] += 1

                if match["confidence"] >= 80:
                    summary["high_confidence"] += 1
                elif match["confidence"] >= 60:
                    summary["medium_confidence"] += 1
                else:
                    summary["low_confidence"] += 1

        return summary
