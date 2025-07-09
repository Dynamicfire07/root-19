"""Data structures representing MongoDB documents.

This file previously contained Django ORM models using SQL terminology. It has
been simplified to dataclass representations that map directly to MongoDB
collections.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Question:
    question_id: str
    session_code: str
    session: str
    year: int
    paper_code: str
    variant: str
    file_question: str
    subtopic: str
    extracted_text: str
    image_base64: str
    answer: str


@dataclass
class User:
    user_id: str
    name: str
    email: str
    password: str
    role: str
    school: str


@dataclass
class UserActivity:
    user_id: str
    question_id: str
    solved: bool = False
    correct: bool = False
    bookmarked: bool = False
    starred: bool = False
    times_viewed: int = 0
    time_started: Optional[datetime] = None
    time_took: Optional[timedelta] = None
