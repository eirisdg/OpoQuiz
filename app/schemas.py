"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Test difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class CategoryType(str, Enum):
    """Test categories - Generic for any subject."""
    GENERAL = "general"
    TEMA_1 = "tema_1"
    TEMA_2 = "tema_2" 
    TEMA_3 = "tema_3"
    DERECHO_ADMINISTRATIVO = "derecho_administrativo"
    DERECHO_CONSTITUCIONAL = "derecho_constitucional"
    LEGISLACION = "legislacion"
    PROCEDIMIENTOS = "procedimientos"
    TEORIA = "teoria"
    PRACTICA = "practica"


class TestStatus(str, Enum):
    """Test session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Test Question Schemas
class SourceInfo(BaseModel):
    """Source information for a question."""
    document: str
    section: str
    page: Optional[int] = None
    legal_reference: Optional[str] = None


class QuestionData(BaseModel):
    """Individual question data."""
    id: int
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    source_info: Optional[SourceInfo] = None
    difficulty: DifficultyLevel
    category: CategoryType
    keywords: List[str] = []
    points: int = Field(default=1, ge=1, le=5)


class TestMetadata(BaseModel):
    """Test metadata information."""
    source_documents: List[Dict[str, Any]] = []
    generated_by: str = "Generic Test Generator"
    generation_method: str = "manual"
    version: str = "1.0"
    language: str = "es"
    region: str = "ES"
    subject_area: str = "Generic Subject"
    last_updated: datetime
    tags: List[str] = []
    quality_checks: Dict[str, bool] = {}


class UIConfig(BaseModel):
    """UI configuration for test display."""
    theme: str = "generic"
    show_progress: bool = True
    show_timer: bool = True
    allow_review: bool = True
    shuffle_options: bool = False
    shuffle_questions: bool = False
    show_explanation_after: str = "question"
    navigation: Dict[str, bool] = {}
    display_settings: Dict[str, Any] = {}


class TestSchema(BaseModel):
    """Complete test schema."""
    test_id: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    category: CategoryType
    difficulty: DifficultyLevel
    estimated_duration: int
    instructions: Optional[str] = None
    passing_grade: int = 70
    questions: List[QuestionData]
    scoring: Dict[str, Any] = {}
    statistics: Dict[str, Any] = {}
    metadata: Optional[TestMetadata] = None
    ui_config: Optional[UIConfig] = None


# API Request/Response Schemas
class TestListResponse(BaseModel):
    """Response for listing available tests."""
    tests: List[Dict[str, Any]]
    total_count: int


class TestResponse(BaseModel):
    """Response for getting a specific test."""
    test: TestSchema


class StartSessionRequest(BaseModel):
    """Request to start a new test session."""
    test_id: str
    user_ip: Optional[str] = None
    is_random_test: bool = False
    random_config: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response for test session operations."""
    session_id: str
    test_id: str
    current_question: int
    total_questions: int
    started_at: datetime
    status: TestStatus


class QuestionResponse(BaseModel):
    """Response for getting a question."""
    session_id: str
    question_id: int
    question: str
    options: List[str]
    category: str
    difficulty: str
    current_position: int
    total_questions: int
    can_go_previous: bool
    can_go_next: bool


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: int
    selected_answer: int
    time_spent_seconds: Optional[int] = None


class CompleteTestRequest(BaseModel):
    """Request to complete a test."""
    final_answers: Optional[Dict[int, int]] = None


class AnswerDetail(BaseModel):
    """Detailed answer information."""
    question_id: int
    question_text: str
    selected_answer: int
    correct_answer: int
    is_correct: bool
    selected_option: str
    correct_option: str
    explanation: Optional[str] = None
    points_earned: int
    time_spent_seconds: Optional[int] = None


class CategoryPerformance(BaseModel):
    """Performance breakdown by category."""
    correct: int
    total: int
    percentage: float


class TestResultsResponse(BaseModel):
    """Response for test completion results."""
    session_id: str
    test_id: str
    score: int
    total_questions: int
    total_points: int
    points_earned: int
    percentage: float
    duration_seconds: int
    passed: bool
    completed_at: datetime
    category_performance: Dict[str, CategoryPerformance]
    difficulty_performance: Dict[str, CategoryPerformance]
    detailed_answers: List[AnswerDetail]


class RandomTestConfig(BaseModel):
    """Configuration for random test generation."""
    num_questions: int = Field(default=10, ge=5, le=50)
    categories: Optional[List[CategoryType]] = None
    difficulties: Optional[List[DifficultyLevel]] = None
    exclude_test_ids: List[str] = []
    allow_repeats: bool = False


class RandomTestResponse(BaseModel):
    """Response for random test generation."""
    test: TestSchema
    source_test_ids: List[str]


# Statistics Schemas
class RecentSession(BaseModel):
    """Recent test session summary."""
    session_id: str
    test_id: str
    test_title: str
    score_percentage: float
    completed_at: datetime
    duration_seconds: int


class TestStatistics(BaseModel):
    """Statistics for a specific test."""
    test_id: str
    test_title: str
    times_taken: int
    average_score: float
    best_score: float
    worst_score: float
    last_taken: Optional[datetime] = None


class GeneralStats(BaseModel):
    """General application statistics."""
    total_tests_available: int
    total_sessions_completed: int
    average_score_all_tests: float
    most_popular_test: Optional[str] = None
    most_difficult_category: Optional[str] = None
    recent_sessions: List[RecentSession]
    test_statistics: List[TestStatistics]


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime
    version: str
    database_connected: bool
    tests_available: int


# Error Response Schema
class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime