"""
This module defines the data models for the application, such as WebSource.
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Summary:
    """
    Represents the structured, three-part summary of an article.
    """
    proposal_details: str  # What is the matter proposed?
    status_and_outcome: str # What is the outcome or status?
    citizen_impact: str    # What is the impact on a Finnish citizen?

@dataclass
class Article:
    """
    Represents a scraped article, now with a structured summary.
    """
    title: str
    source_url: str
    raw_content: str # We should store the full scraped text
    summary: Summary   # The summary is now its own structured object
    source_id: int     # Foreign key to the WebSource
    id: int = None
    primary_category: str = None
    tags: List[str] = None
