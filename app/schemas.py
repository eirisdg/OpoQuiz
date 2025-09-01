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


# Flexible category type - allows any string for maximum flexibility
CategoryType = str


class TestStatus(str, Enum):
    """Test session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Question Bank Schemas (NEW)
class SourceInfo(BaseModel):
    """Source information for a question."""
    document: str
    section: str
    page: Optional[int] = None
    legal_reference: Optional[str] = None


class QuestionBankData(BaseModel):
    """Individual question data in a question bank."""
    id: str  # Changed to string for more flexible IDs
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    source_info: Optional[SourceInfo] = None
    difficulty: DifficultyLevel
    category: CategoryType
    keywords: List[str] = []
    estimated_time_seconds: int = Field(default=90, ge=30, le=300)


class QuestionBankSchema(BaseModel):
    """Question bank schema for JSON files."""
    bank_id: str
    title: str
    description: Optional[str] = None
    questions: List[QuestionBankData]


# Legacy Question Data (for backward compatibility)
class QuestionData(BaseModel):
    """Individual question data (legacy format)."""
    id: str
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None
    source_info: Optional[SourceInfo] = None
    difficulty: DifficultyLevel
    category: CategoryType
    keywords: List[str] = []
    points: int = Field(default=1, ge=1, le=5)
    estimated_time_seconds: int = Field(default=90, ge=30, le=300)


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
    created_at: Optional[datetime] = None
    created_date: Optional[str] = None  # Alternative format
    category: Optional[CategoryType] = "general"
    difficulty: Optional[DifficultyLevel] = "mixed"
    estimated_duration: Optional[int] = None
    time_limit_minutes: Optional[int] = None  # Alternative format
    instructions: Optional[str] = None
    passing_grade: Optional[int] = 70
    passing_score: Optional[int] = None  # Alternative format
    total_questions: Optional[int] = None  # Alternative format
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
    question_id: str
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
    question_id: str
    selected_answer: int
    time_spent_seconds: Optional[int] = None


class CompleteTestRequest(BaseModel):
    """Request to complete a test."""
    final_answers: Optional[Dict[str, int]] = None


class AnswerDetail(BaseModel):
    """Detailed answer information."""
    question_id: str
    question_text: str
    selected_answer: int
    correct_answer: int
    is_correct: bool
    selected_option: str
    correct_option: str
    explanation: Optional[str] = None
    source_info: Optional[SourceInfo] = None
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


# Dynamic Test Generation Schemas (NEW)
class TestGenerationType(str, Enum):
    """Types of dynamic test generation."""
    RANDOM = "random"
    CATEGORY = "category"
    DIFFICULTY = "difficulty"
    FAILED_QUESTIONS = "failed_questions"


class DynamicTestRequest(BaseModel):
    """Request to create a dynamic test."""
    test_type: TestGenerationType
    num_questions: int = Field(default=50, ge=5, le=100)
    title: Optional[str] = None
    
    # Category-based test
    categories: Optional[List[str]] = None
    
    # Difficulty-based test
    difficulty: Optional[DifficultyLevel] = None
    
    # Failed questions test
    source_session_id: Optional[str] = None
    
    # General options
    user_ip: Optional[str] = None


class DynamicTestResponse(BaseModel):
    """Response for dynamic test creation."""
    test_id: str
    test_type: str
    title: str
    num_questions: int
    estimated_duration_minutes: int
    session_id: str


class CategoryOption(BaseModel):
    """Available category for selection."""
    category: str
    question_count: int
    

class TestConfigurationResponse(BaseModel):
    """Response with available test configuration options."""
    available_categories: List[CategoryOption]
    available_difficulties: List[Dict[str, Any]]
    total_questions: int
    has_failed_questions: bool


# Legacy Random Test Config (for backward compatibility)
class RandomTestConfig(BaseModel):
    """Configuration for random test generation."""
    num_questions: int = Field(default=10, ge=5, le=50)
    categories: Optional[List[CategoryType]] = None
    difficulties: Optional[List[DifficultyLevel]] = None
    exclude_test_ids: List[str] = []
    allow_repeats: bool = False
    # New fields for failed questions test
    source_session_id: Optional[str] = None
    failed_questions_only: bool = False


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