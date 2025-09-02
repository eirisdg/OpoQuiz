"""FastAPI Test Generator - Main Application."""

from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
import json
import uuid
from typing import Dict, List, Optional, Any

from app.config import get_settings, ensure_directories, validate_test_files
from app.database import init_database, get_db_manager, DatabaseManager
from app.schemas import (
    TestListResponse, TestResponse, StartSessionRequest, SessionResponse,
    QuestionResponse, SubmitAnswerRequest, CompleteTestRequest, TestResultsResponse,
    RandomTestConfig, RandomTestResponse, GeneralStats, HealthResponse, ErrorResponse,
    TestSchema, QuestionData, AnswerDetail, CategoryPerformance, DifficultyLevel, CategoryType
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database
    await init_database()
    
    # Validate test files
    test_files = validate_test_files()
    
    # Load question banks into database
    banks_loaded = await load_question_banks()
    print(f"📚 Loaded {banks_loaded} question banks into database")
    
    # Initialize empty cache for backward compatibility
    app.state.tests_cache = {}
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Interactive test generator for Spanish Social Security documents",
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url="/redoc" if settings.enable_api_docs else None,
        lifespan=lifespan
    )
    
    # CORS Configuration
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Static files
    if os.path.exists(settings.static_dir):
        app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    
    # Templates
    templates = Jinja2Templates(directory=settings.templates_dir)
    
    return app, templates


app, templates = create_app()


# Utility Functions
def normalize_test_data(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize test data to handle different JSON formats."""
    normalized = test_data.copy()
    
    # Handle created_date -> created_at
    if 'created_date' in normalized and 'created_at' not in normalized:
        created_date = normalized['created_date']
        # Convert YYYY-MM-DD to ISO datetime
        if isinstance(created_date, str) and len(created_date) == 10:
            normalized['created_at'] = f"{created_date}T00:00:00Z"
    
    # Handle time_limit_minutes -> estimated_duration
    if 'time_limit_minutes' in normalized and 'estimated_duration' not in normalized:
        normalized['estimated_duration'] = normalized['time_limit_minutes']
    
    # Handle passing_score -> passing_grade
    if 'passing_score' in normalized and 'passing_grade' not in normalized:
        total_questions = normalized.get('total_questions', len(normalized.get('questions', [])))
        if total_questions > 0:
            # Convert absolute score to percentage
            normalized['passing_grade'] = int((normalized['passing_score'] / total_questions) * 100)
    
    # Set defaults for missing required fields
    if 'category' not in normalized:
        normalized['category'] = 'general'
    if 'difficulty' not in normalized:
        normalized['difficulty'] = 'mixed'
    if 'estimated_duration' not in normalized:
        total_questions = len(normalized.get('questions', []))
        # Estimate 1.5 minutes per question
        normalized['estimated_duration'] = max(10, int(total_questions * 1.5))
    
    return normalized


async def load_question_banks() -> int:
    """Load all question bank files into database."""
    from app.schemas import QuestionBankSchema
    
    if not os.path.exists(settings.tests_dir):
        return 0
    
    db_manager = await get_db_manager()
    banks_loaded = 0
    
    for filename in os.listdir(settings.tests_dir):
        if filename.endswith('.json') and filename.startswith('bank_'):
            file_path = os.path.join(settings.tests_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    bank_data = json.load(f)
                    bank_schema = QuestionBankSchema(**bank_data)
                    
                    # Prepare data for database
                    bank_data_for_db = {
                        'bank_id': bank_schema.bank_id,
                        'title': bank_schema.title,
                        'description': bank_schema.description,
                        'file_path': file_path,
                        'questions': []
                    }
                    
                    # Convert questions
                    for question in bank_schema.questions:
                        question_data = {
                            'id': question.id,
                            'question': question.question,
                            'options': question.options,
                            'correct_answer': question.correct_answer,
                            'explanation': question.explanation,
                            'difficulty': question.difficulty,
                            'category': question.category,
                            'keywords': question.keywords,
                            'estimated_time_seconds': question.estimated_time_seconds,
                            'source_info': question.source_info.dict() if question.source_info else {}
                        }
                        bank_data_for_db['questions'].append(question_data)
                    
                    await db_manager.load_question_bank(bank_data_for_db)
                    banks_loaded += 1
                    print(f"📚 Loaded question bank: {bank_schema.title} ({len(bank_schema.questions)} questions)")
                    
            except Exception as e:
                print(f"Error loading question bank {filename}: {e}")
                continue
    
    return banks_loaded


def get_client_ip(request: Request) -> str:
    """Get client IP address."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def generate_session_id() -> str:
    """Generate unique session ID."""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Home page with question bank statistics and test generation options."""
    try:
        # Get general statistics
        stats_data = await db.get_general_stats()
        
        # Get question bank statistics
        question_stats = await db.get_question_stats()
        stats_data.update(question_stats)
        
        # Get available categories for test generation
        available_categories = await db.get_available_categories()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": stats_data,
            "available_categories": available_categories,
            "app_name": settings.app_name,
            "app_version": settings.app_version
        })
        
    except Exception as e:
        print(f"Error in home_page: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Error loading application data",
            "detail": str(e)
        })


# Admin Panel Routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Admin panel for question bank management."""
    try:
        # Get question bank statistics
        question_stats = await db.get_question_stats()
        
        # Get list of question banks
        async with db.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT bank_id, title, description, questions_count, loaded_at, last_updated 
                FROM question_banks ORDER BY last_updated DESC
            """)
            banks = await cursor.fetchall()
        
        bank_list = []
        for bank in banks:
            bank_list.append({
                'bank_id': bank[0],
                'title': bank[1], 
                'description': bank[2],
                'questions_count': bank[3],
                'loaded_at': bank[4],
                'last_updated': bank[5]
            })
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "stats": question_stats,
            "banks": bank_list,
            "app_name": settings.app_name
        })
        
    except Exception as e:
        print(f"Error in admin_panel: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Error loading admin panel",
            "detail": str(e)
        })


@app.post("/admin/upload")
async def upload_question_bank(
    request: Request,
    file: UploadFile = File(...),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Upload and load a new question bank file."""
    try:
        # Validate file
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")
        
        if not file.filename.startswith('bank_'):
            raise HTTPException(status_code=400, detail="File name must start with 'bank_'")
        
        # Read file content
        content = await file.read()
        
        # Validate JSON structure
        try:
            bank_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate against schema
        from app.schemas import QuestionBankSchema
        try:
            bank_schema = QuestionBankSchema(**bank_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid question bank format: {str(e)}")
        
        # Save file to tests directory
        file_path = os.path.join(settings.tests_dir, file.filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.decode('utf-8'))
        
        # Load into database
        bank_data_for_db = {
            'bank_id': bank_schema.bank_id,
            'title': bank_schema.title,
            'description': bank_schema.description,
            'file_path': file_path,
            'questions': []
        }
        
        # Convert questions
        for question in bank_schema.questions:
            question_data = {
                'id': question.id,
                'question': question.question,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'difficulty': question.difficulty,
                'category': question.category,
                'keywords': question.keywords,
                'estimated_time_seconds': question.estimated_time_seconds,
                'source_info': question.source_info.dict() if question.source_info else {}
            }
            bank_data_for_db['questions'].append(question_data)
        
        questions_loaded = await db.load_question_bank(bank_data_for_db)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully loaded {questions_loaded} questions from {bank_schema.title}",
            "bank_id": bank_schema.bank_id,
            "questions_count": questions_loaded
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_question_bank: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")


@app.delete("/admin/bank/{bank_id}")
async def delete_question_bank(
    bank_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Delete a question bank and its questions."""
    try:
        async with db.get_connection() as conn:
            # Get bank info including file path
            cursor = await conn.execute("SELECT file_path FROM question_banks WHERE bank_id = ?", (bank_id,))
            bank = await cursor.fetchone()
            
            if not bank:
                raise HTTPException(status_code=404, detail="Question bank not found")
            
            file_path = bank[0]
            
            # Delete questions from database
            await conn.execute("DELETE FROM questions WHERE bank_id = ?", (bank_id,))
            
            # Delete bank metadata
            await conn.execute("DELETE FROM question_banks WHERE bank_id = ?", (bank_id,))
            
            await conn.commit()
            
            # Delete file if it exists
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully deleted question bank {bank_id}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_question_bank: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting bank: {str(e)}")


@app.get("/admin/sessions")
async def list_test_sessions(
    db: DatabaseManager = Depends(get_db_manager),
    limit: int = 50
):
    """List completed test sessions for admin management."""
    try:
        async with db.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT 
                    ts.session_id,
                    ts.test_id,
                    COALESCE(dt.test_title, ts.test_title, ts.test_id) as test_title,
                    ts.user_ip,
                    ts.started_at,
                    ts.completed_at,
                    ts.total_questions,
                    ts.correct_answers,
                    ts.score_percentage,
                    ts.duration_seconds,
                    ts.is_dynamic_test,
                    ts.test_type
                FROM test_sessions ts
                LEFT JOIN dynamic_tests dt ON ts.test_id = dt.test_id
                ORDER BY ts.completed_at DESC
                LIMIT ?
            """, (limit,))
            sessions = await cursor.fetchall()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session[0],
                'test_id': session[1],
                'test_title': session[2] or f"Test {session[1]}",
                'user_ip': session[3],
                'started_at': session[4],
                'completed_at': session[5],
                'total_questions': session[6],
                'correct_answers': session[7],
                'score_percentage': session[8],
                'duration_seconds': session[9],
                'is_dynamic_test': bool(session[10]),
                'test_type': session[11]
            })
        
        return JSONResponse({
            "success": True,
            "sessions": session_list,
            "total": len(session_list)
        })
        
    except Exception as e:
        print(f"Error in list_test_sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@app.delete("/admin/session/{session_id}")
async def delete_test_session(
    session_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Delete a test session and its related data."""
    try:
        async with db.get_connection() as conn:
            # Check if session exists
            cursor = await conn.execute("SELECT session_id FROM test_sessions WHERE session_id = ?", (session_id,))
            session = await cursor.fetchone()
            
            if not session:
                raise HTTPException(status_code=404, detail="Test session not found")
            
            # Delete related data in order (foreign key constraints)
            await conn.execute("DELETE FROM user_answers WHERE session_id = ?", (session_id,))
            await conn.execute("DELETE FROM session_progress WHERE session_id = ?", (session_id,))
            await conn.execute("DELETE FROM test_sessions WHERE session_id = ?", (session_id,))
            
            await conn.commit()
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully deleted session {session_id}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_test_session: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@app.get("/test/{session_id}", response_class=HTMLResponse)
async def test_page(
    session_id: str,
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Test taking interface - redirect to first question."""
    try:
        session_data = await db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_data['status'] == 'completed':
            # Redirect to results page
            return templates.TemplateResponse("redirect.html", {
                "request": request,
                "redirect_url": f"/results/{session_id}"
            })
        
        # Redirect to current question
        current_index = session_data.get('current_question_index', 0)
        return templates.TemplateResponse("redirect.html", {
            "request": request,
            "redirect_url": f"/test/{session_id}/question/{current_index}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in test_page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/test/{session_id}/question/{question_index}", response_class=HTMLResponse)
async def test_question_page(
    session_id: str,
    question_index: int,
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Individual question page."""
    try:
        session_data = await db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_data['status'] == 'completed':
            return templates.TemplateResponse("redirect.html", {
                "request": request,
                "redirect_url": f"/results/{session_id}"
            })
        
        # Get test data (dynamic or static)
        test_data = await db.get_dynamic_test(session_data['test_id'])
        print(f"DEBUG: test_data from get_dynamic_test: {test_data is not None}")
        if test_data:
            print(f"DEBUG: test_data type: {type(test_data)}")
            print(f"DEBUG: test_data keys: {list(test_data.keys()) if isinstance(test_data, dict) else 'not dict'}")
        
        if not test_data:
            # Fallback to static tests cache if dynamic test not found
            test_schema = app.state.tests_cache.get(session_data['test_id'])
            print(f"DEBUG: fallback test_schema: {test_schema is not None}")
            if not test_schema:
                raise HTTPException(status_code=404, detail="Test not found")
            test_data = test_schema
        
        # Get questions list (handle both dict and object formats)
        questions = test_data['questions'] if isinstance(test_data, dict) else test_data.questions
        print(f"DEBUG: questions length: {len(questions)}")
        print(f"DEBUG: question_index: {question_index}")
        
        # Validate question index
        if question_index < 0 or question_index >= len(questions):
            print(f"DEBUG: Question index validation failed. Index: {question_index}, Length: {len(questions)}")
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Get current question
        question = questions[question_index]
        print(f"DEBUG: question type: {type(question)}")
        print(f"DEBUG: question keys: {list(question.keys()) if isinstance(question, dict) else 'not dict'}")
        
        # Get any existing answer for this question
        answers_data = session_data.get('answers_data', {})
        question_id = question.get('id') if isinstance(question, dict) else question.id
        selected_answer = answers_data.get(str(question_id))
        
        # Get answered questions for navigation
        answered_questions = [k for k in answers_data.keys() if answers_data[k] is not None]
        
        # Update current question index
        await db.update_session_progress(session_id, question_index, answers_data)
        
        return templates.TemplateResponse("test.html", {
            "request": request,
            "session_id": session_id,
            "test_data": {
                "title": test_data.get('title') if isinstance(test_data, dict) else test_data.title,
                "test_id": test_data.get('test_id') if isinstance(test_data, dict) else test_data.test_id
            },
            "question": question,
            "current_question": question_index,
            "total_questions": len(questions),
            "selected_answer": selected_answer,
            "answered_questions": answered_questions,
            "session_start_time": session_data.get('started_at')
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in test_question_page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/results/{session_id}", response_class=HTMLResponse)
async def results_page(
    session_id: str,
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Test results page."""
    try:
        session_data = await db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_data['status'] != 'completed':
            raise HTTPException(status_code=400, detail="Test not completed yet")
        
        # Get detailed answers
        answers = await db.get_session_answers(session_id)
        
        # Build results structure for template
        detailed_answers = []
        
        # Get test data (dynamic or static)
        test_data = await db.get_dynamic_test(session_data['test_id'])
        
        if not test_data:
            # Fallback to static tests cache if dynamic test not found
            test_schema = app.state.tests_cache.get(session_data['test_id'])
            if test_schema:
                test_data = test_schema
        
        for answer in answers:
            question = None
            if test_data:
                if isinstance(test_data, dict):
                    # Dynamic test - search in questions list by string ID
                    answer_id = str(answer['question_id'])
                    # Try to find by question_id first, then by id
                    question = next((q for q in test_data['questions'] if str(q.get('question_id', '')) == answer_id), None)
                    if not question:
                        question = next((q for q in test_data['questions'] if str(q.get('id', '')) == answer_id), None)
                else:
                    # Static test - search in questions list
                    question = next((q for q in test_data.questions if q.id == answer['question_id']), None)
                
            if question:
                # Handle both dict and object formats
                options = question.get('options') if isinstance(question, dict) else question.options
                explanation = question.get('explanation', '') if isinstance(question, dict) else getattr(question, 'explanation', '')
                source_info = question.get('source_info', {}) if isinstance(question, dict) else getattr(question, 'source_info', {})
                
                detailed_answers.append({
                    'question_id': answer['question_id'],
                    'question_text': answer['question_text'],
                    'selected_answer': answer['selected_answer'],
                    'correct_answer': answer['correct_answer'],
                    'is_correct': answer['is_correct'],
                    'selected_option': options[answer['selected_answer']] if answer['selected_answer'] is not None and answer['selected_answer'] < len(options) else "Sin responder",
                    'correct_option': options[answer['correct_answer']] if answer['correct_answer'] < len(options) else "N/A",
                    'explanation': explanation,
                    'source_info': source_info,
                    'points_earned': answer['points_earned'],
                    'time_spent_seconds': answer['time_spent_seconds']
                })
        
        print(f"DEBUG RESULTS: Built {len(detailed_answers)} detailed answers")
        
        # Calculate category and difficulty performance
        category_performance = {}
        difficulty_performance = {}
        
        for answer in answers:
            question = None
            if test_data:
                if isinstance(test_data, dict):
                    # Dynamic test - search in questions list
                    question = next((q for q in test_data['questions'] if q['id'] == answer['question_id']), None)
                else:
                    # Static test - search in questions list
                    question = next((q for q in test_data.questions if q.id == answer['question_id']), None)
                    
            if question:
                # Handle both dict and object formats for category
                cat = question.get('category') if isinstance(question, dict) else (question.category.value if hasattr(question.category, 'value') else str(question.category))
                if cat not in category_performance:
                    category_performance[cat] = {'correct': 0, 'total': 0, 'percentage': 0}
                category_performance[cat]['total'] += 1
                if answer['is_correct']:
                    category_performance[cat]['correct'] += 1
                
                # Handle both dict and object formats for difficulty
                diff = question.get('difficulty') if isinstance(question, dict) else (question.difficulty.value if hasattr(question.difficulty, 'value') else str(question.difficulty))
                if diff not in difficulty_performance:
                    difficulty_performance[diff] = {'correct': 0, 'total': 0, 'percentage': 0}
                difficulty_performance[diff]['total'] += 1
                if answer['is_correct']:
                    difficulty_performance[diff]['correct'] += 1
        
        # Calculate percentages
        for perf in category_performance.values():
            perf['percentage'] = (perf['correct'] / perf['total'] * 100) if perf['total'] > 0 else 0
        
        for perf in difficulty_performance.values():
            perf['percentage'] = (perf['correct'] / perf['total'] * 100) if perf['total'] > 0 else 0
        
        results = {
            'session_id': session_id,
            'test_id': session_data['test_id'],
            'score': session_data['correct_answers'],
            'total_questions': session_data['total_questions'],
            'total_points': session_data['total_points'],
            'points_earned': session_data['points_earned'],
            'percentage': session_data['score_percentage'],
            'duration_seconds': session_data['duration_seconds'],
            'passed': session_data['score_percentage'] >= settings.default_passing_grade,
            'completed_at': session_data['completed_at'],
            'category_performance': category_performance,
            'difficulty_performance': difficulty_performance,
            'detailed_answers': detailed_answers
        }
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "results": results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in results_page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# API Routes
@app.get("/api/tests", response_model=TestListResponse)
async def list_tests():
    """Get list of available tests."""
    tests = []
    for test_id, test_schema in app.state.tests_cache.items():
        tests.append({
            "test_id": test_id,
            "title": test_schema.title,
            "description": test_schema.description,
            "category": test_schema.category.value,
            "difficulty": test_schema.difficulty.value,
            "total_questions": len(test_schema.questions),
            "estimated_duration": test_schema.estimated_duration,
            "passing_grade": test_schema.passing_grade
        })
    
    return TestListResponse(tests=tests, total_count=len(tests))


@app.get("/api/tests/{test_id}", response_model=TestResponse)
async def get_test(test_id: str):
    """Get specific test details."""
    if test_id not in app.state.tests_cache:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return TestResponse(test=app.state.tests_cache[test_id])


@app.post("/api/sessions", response_model=SessionResponse)
async def start_session(
    request_data: StartSessionRequest,
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Start a new test session."""
    print(f"[DEBUG] Starting session with request_data: {request_data}")
    test_id = request_data.test_id
    print(f"[DEBUG] test_id: {test_id}, is_random_test: {request_data.is_random_test}")
    
    # Handle random test generation
    if test_id == 'random' or test_id == 'failed_questions' or request_data.is_random_test:
        try:
            print(f"[DEBUG] About to call generate_random_test with config: {request_data.random_config}")
            test_schema = await generate_dynamic_random_test(request_data.random_config or {})
            print(f"[DEBUG] Successfully generated test_schema: {test_schema.test_id}")
            test_id = test_schema.test_id
            # Store in cache temporarily
            app.state.tests_cache[test_id] = test_schema
        except Exception as e:
            print(f"[ERROR] Error in generate_random_test: {e}")
            import traceback
            print(f"[ERROR] Full traceback: {traceback.format_exc()}")
            raise
    elif test_id not in app.state.tests_cache:
        raise HTTPException(status_code=404, detail="Test not found")
    else:
        test_schema = app.state.tests_cache[test_id]
    
    session_id = generate_session_id()
    
    session_data = {
        'session_id': session_id,
        'test_id': test_id,
        'test_title': test_schema.title,
        'user_ip': request_data.user_ip or get_client_ip(request),
        'started_at': datetime.now(),
        'total_questions': len(test_schema.questions),
        'is_random_test': request_data.is_random_test,
        'question_ids': [q.id for q in test_schema.questions]
    }
    
    await db.create_session(session_data)
    
    return SessionResponse(
        session_id=session_id,
        test_id=test_id,
        current_question=1,
        total_questions=len(test_schema.questions),
        started_at=session_data['started_at'],
        status="active"
    )


@app.get("/api/sessions/{session_id}/question/{question_index}", response_model=QuestionResponse)
async def get_question(
    session_id: str,
    question_index: int,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get a specific question for a session."""
    session_data = await db.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    test_schema = app.state.tests_cache.get(session_data['test_id'])
    if not test_schema:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if question_index < 0 or question_index >= len(test_schema.questions):
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = test_schema.questions[question_index]
    
    return QuestionResponse(
        session_id=session_id,
        question_id=question.id,
        question=question.question,
        options=question.options,
        category=question.category.value if hasattr(question.category, 'value') else str(question.category),
        difficulty=question.difficulty.value if hasattr(question.difficulty, 'value') else str(question.difficulty),
        current_position=question_index + 1,
        total_questions=len(test_schema.questions),
        can_go_previous=question_index > 0,
        can_go_next=question_index < len(test_schema.questions) - 1
    )


@app.post("/api/sessions/{session_id}/answers")
async def submit_answer(
    session_id: str,
    answer_data: SubmitAnswerRequest,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Submit an answer (without validation)."""
    session_data = await db.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update answers in session progress
    answers = session_data.get('answers_data', {})
    answers[str(answer_data.question_id)] = {
        'selected_answer': answer_data.selected_answer,
        'time_spent_seconds': answer_data.time_spent_seconds
    }
    
    await db.update_session_progress(
        session_id, 
        session_data.get('current_question_index', 0),
        answers
    )
    
    # Save basic answer immediately to ensure no data loss
    await db.save_user_answer_basic(
        session_id,
        str(answer_data.question_id),
        answer_data.selected_answer,
        answer_data.time_spent_seconds
    )
    
    return {"status": "answer_saved", "question_id": answer_data.question_id}


@app.post("/api/sessions/{session_id}/complete", response_model=TestResultsResponse)
async def complete_test(
    session_id: str,
    request_data: CompleteTestRequest,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Complete test and calculate results."""
    session_data = await db.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get test data (dynamic or static)
    test_data = await db.get_dynamic_test(session_data['test_id'])
    if not test_data:
        # Fallback to static tests cache if dynamic test not found
        test_schema = app.state.tests_cache.get(session_data['test_id'])
        if not test_schema:
            raise HTTPException(status_code=404, detail="Test not found")
        test_data = test_schema
    
    # Calculate results
    answers_data = session_data.get('answers_data', {})
    detailed_answers = []
    total_points = 0
    category_stats = {}
    difficulty_stats = {}
    
    questions = test_data['questions'] if isinstance(test_data, dict) else test_data.questions
    for question in questions:
        # Handle both dict and object formats
        # Use question_id for dynamic tests, fallback to id for static tests
        q_id = str(question.get('question_id') if isinstance(question, dict) and question.get('question_id') else (question.get('id') if isinstance(question, dict) else question.id))
        user_answer_data = answers_data.get(q_id, {})
        selected_answer = user_answer_data.get('selected_answer')
        
        correct_answer = question.get('correct_answer') if isinstance(question, dict) else question.correct_answer
        is_correct = selected_answer == correct_answer
        question_points = question.get('points', 1) if isinstance(question, dict) else getattr(question, 'points', 1)
        
        total_points += question_points
        
        # Category stats
        cat = question.get('category') if isinstance(question, dict) else (question.category.value if hasattr(question.category, 'value') else question.category)
        if cat not in category_stats:
            category_stats[cat] = {'correct': 0, 'total': 0}
        category_stats[cat]['total'] += 1
        if is_correct:
            category_stats[cat]['correct'] += 1
        
        # Difficulty stats  
        diff = question.get('difficulty') if isinstance(question, dict) else (question.difficulty.value if hasattr(question.difficulty, 'value') else question.difficulty)
        if diff not in difficulty_stats:
            difficulty_stats[diff] = {'correct': 0, 'total': 0}
        difficulty_stats[diff]['total'] += 1
        if is_correct:
            difficulty_stats[diff]['correct'] += 1
        
        # Save answer to database
        question_text = question.get('question') if isinstance(question, dict) else question.question
        options = question.get('options') if isinstance(question, dict) else question.options
        explanation = question.get('explanation', '') if isinstance(question, dict) else getattr(question, 'explanation', '')
        source_info_raw = question.get('source_info', {}) if isinstance(question, dict) else getattr(question, 'source_info', {})
        
        # Convert source_info to proper format or None for Pydantic validation
        source_info = None
        if source_info_raw and isinstance(source_info_raw, dict) and source_info_raw.get('document'):
            source_info = source_info_raw
        
        # Update existing answer with detailed information
        await db.update_answer_details(
            session_id,
            str(q_id),
            question_text,
            correct_answer,
            is_correct,
            question_points,
            question_points if is_correct else 0
        )
        
        detailed_answers.append(AnswerDetail(
            question_id=str(q_id),
            question_text=question_text,
            selected_answer=selected_answer if selected_answer is not None else -1,
            correct_answer=correct_answer,
            is_correct=is_correct,
            selected_option=options[selected_answer] if selected_answer is not None and selected_answer < len(options) else "No respondida",
            correct_option=options[correct_answer] if correct_answer < len(options) else "N/A",
            explanation=explanation,
            source_info=source_info,
            points_earned=question_points if is_correct else 0,
            time_spent_seconds=user_answer_data.get('time_spent_seconds', 0)
        ))
    
    # Calculate final metrics from database after all answers are updated
    async with db.get_connection() as conn:
        cursor = await conn.execute("SELECT SUM(is_correct), SUM(points_earned) FROM user_answers WHERE session_id = ?", (session_id,))
        db_result = await cursor.fetchone()
        correct_count = int(db_result[0]) if db_result[0] else 0
        points_earned = int(db_result[1]) if db_result[1] else 0
    
    percentage = (points_earned / total_points * 100) if total_points > 0 else 0
    duration = int((datetime.now() - datetime.fromisoformat(session_data['started_at'].replace('Z', '+00:00'))).total_seconds())
    passing_grade = test_data.get('passing_grade', 70) if isinstance(test_data, dict) else getattr(test_data, 'passing_grade', 70)
    passed = percentage >= passing_grade
    
    # Complete session
    await db.complete_session(session_id, {
        'completed_at': datetime.now(),
        'correct_answers': correct_count,
        'total_points': total_points,
        'points_earned': points_earned,
        'score_percentage': percentage,
        'duration_seconds': duration
    })
    
    # Update test statistics
    test_id = test_data.get('test_id') if isinstance(test_data, dict) else test_data.test_id
    test_title = test_data.get('title') if isinstance(test_data, dict) else test_data.title
    question_count = len(questions)
    await db.update_test_stats(test_id, test_title, percentage, question_count)
    
    # Build category performance
    category_performance = {}
    for cat, stats in category_stats.items():
        category_performance[cat] = CategoryPerformance(
            correct=stats['correct'],
            total=stats['total'],
            percentage=stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        )
    
    difficulty_performance = {}
    for diff, stats in difficulty_stats.items():
        difficulty_performance[diff] = CategoryPerformance(
            correct=stats['correct'],
            total=stats['total'],
            percentage=stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        )
    
    return TestResultsResponse(
        session_id=session_id,
        test_id=test_id,
        score=correct_count,
        total_questions=question_count,
        total_points=total_points,
        points_earned=points_earned,
        percentage=round(percentage, 2),
        duration_seconds=duration,
        passed=passed,
        completed_at=datetime.now(),
        category_performance=category_performance,
        difficulty_performance=difficulty_performance,
        detailed_answers=detailed_answers
    )


@app.get("/api/stats", response_model=GeneralStats)
async def get_stats(db: DatabaseManager = Depends(get_db_manager)):
    """Get general application statistics."""
    stats_data = await db.get_general_stats()
    
    # Process recent sessions
    recent_sessions = []
    for session_data in stats_data.get('recent_sessions', []):
        recent_sessions.append({
            'session_id': session_data[0],
            'test_id': session_data[1], 
            'test_title': session_data[2],
            'score_percentage': session_data[3],
            'completed_at': session_data[4],
            'duration_seconds': session_data[5]
        })
    
    # Process test statistics
    test_statistics = []
    for test_stat_data in stats_data.get('test_statistics', []):
        test_statistics.append({
            'test_id': test_stat_data[0],
            'test_title': test_stat_data[1],
            'times_taken': test_stat_data[2],
            'average_score': test_stat_data[3],
            'best_score': test_stat_data[4],
            'worst_score': test_stat_data[5],
            'last_taken': test_stat_data[7]
        })
    
    return GeneralStats(
        total_tests_available=len(app.state.tests_cache),
        total_sessions_completed=stats_data['total_sessions_completed'],
        average_score_all_tests=stats_data['average_score_all_tests'],
        recent_sessions=recent_sessions,
        test_statistics=test_statistics
    )


@app.get("/api/categories")
async def get_available_categories(db: DatabaseManager = Depends(get_db_manager)):
    """Get list of available categories."""
    try:
        categories = await db.get_available_categories()
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Error getting categories")


# Dynamic Test Generation API Endpoints
@app.get("/api/test-config")
async def get_test_configuration(
    request: Request,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get available test configuration options."""
    try:
        # Get available categories
        categories = await db.get_available_categories()
        
        # Get question statistics  
        question_stats = await db.get_question_stats()
        
        # Check if user has failed questions
        user_ip = get_client_ip(request)
        failed_questions = await db.get_failed_questions(user_ip, 1)
        
        return {
            "available_categories": [
                {"category": cat, "question_count": question_stats.get("category_distribution", {}).get(cat, 0)}
                for cat in categories
            ],
            "available_difficulties": [
                {"difficulty": "easy", "question_count": question_stats.get("difficulty_distribution", {}).get("easy", 0)},
                {"difficulty": "medium", "question_count": question_stats.get("difficulty_distribution", {}).get("medium", 0)},
                {"difficulty": "hard", "question_count": question_stats.get("difficulty_distribution", {}).get("hard", 0)},
                {"difficulty": "mixed", "question_count": question_stats.get("total_questions", 0)}
            ],
            "total_questions": question_stats.get("total_questions", 0),
            "has_failed_questions": len(failed_questions) > 0
        }
    except Exception as e:
        print(f"Error in get_test_configuration: {e}")
        raise HTTPException(status_code=500, detail="Error getting test configuration")


@app.post("/api/generate-test")
async def generate_dynamic_test(
    request: Request,
    test_request: dict,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Generate a dynamic test based on specified criteria."""
    try:
        from app.schemas import TestGenerationType
        
        user_ip = get_client_ip(request)
        test_type = test_request.get("test_type", "random")
        num_questions = test_request.get("num_questions", 50)
        
        # Validate request
        if num_questions < 5 or num_questions > 100:
            raise HTTPException(status_code=400, detail="Number of questions must be between 5 and 100")
        
        # Build criteria based on test type
        criteria = {}
        test_title = ""
        
        if test_type == "random":
            test_title = f"Test Aleatorio - {num_questions} preguntas"
            criteria = {}
            
        elif test_type == "category":
            config = test_request.get("config", {})
            categories = config.get("categories", [])
            if not categories:
                raise HTTPException(status_code=400, detail="At least one category must be selected")
            criteria = {"categories": categories}
            test_title = f"Test por Categorías - {num_questions} preguntas"
            
        elif test_type == "difficulty":
            config = test_request.get("config", {})
            difficulty = config.get("difficulty", "medium")
            criteria = {"difficulty": difficulty}
            test_title = f"Test {difficulty.title()} - {num_questions} preguntas"
            
        elif test_type == "failed_questions":
            config = test_request.get("config", {})
            source_session_id = config.get("source_session_id")
            if not source_session_id:
                # Get failed questions for this user
                failed_questions = await db.get_failed_questions(user_ip, num_questions)
                if not failed_questions:
                    raise HTTPException(status_code=400, detail="No failed questions found for this user")
                question_ids = [q['question_id'] for q in failed_questions]
                criteria = {"question_ids": question_ids}
                test_title = f"Repaso de Errores - {len(question_ids)} preguntas"
            else:
                # Get failed questions from specific session
                failed_questions = await db.get_failed_questions_from_session(source_session_id, num_questions)
                if not failed_questions:
                    raise HTTPException(status_code=400, detail="No failed questions found in the specified session")
                question_ids = [q['question_id'] for q in failed_questions]
                criteria = {"question_ids": question_ids}
                test_title = f"Repaso de Errores - {len(question_ids)} preguntas de sesión {source_session_id}"
        
        else:
            raise HTTPException(status_code=400, detail="Invalid test type")
        
        # Get questions based on criteria
        if test_type == "failed_questions" and 'question_ids' in locals():
            # Use specific failed questions
            questions = await db.get_failed_questions(user_ip, num_questions)
        else:
            # Get questions by criteria with anti-repetition
            questions = await db.get_questions_by_criteria(criteria, user_ip, num_questions)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions available matching the specified criteria")
        
        if len(questions) < num_questions:
            num_questions = len(questions)
        
        # Calculate estimated duration based on question times
        estimated_duration_seconds = sum(q.get('estimated_time_seconds', 90) for q in questions)
        estimated_duration_minutes = round(estimated_duration_seconds / 60)
        
        # Generate test ID
        test_id = f"dyn_{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Save dynamic test
        await db.save_dynamic_test({
            'test_id': test_id,
            'test_type': test_type,
            'test_title': test_title,
            'criteria': criteria,
            'question_ids': [q['question_id'] for q in questions],
            'user_ip': user_ip
        })
        
        # Create session for this test
        session_id = generate_session_id()
        
        await db.create_session({
            'session_id': session_id,
            'test_id': test_id,
            'test_title': test_title,
            'user_ip': user_ip,
            'started_at': datetime.now().isoformat(),
            'total_questions': num_questions,
            'is_dynamic_test': True,
            'test_type': test_type,
            'question_ids': [q['question_id'] for q in questions]
        })
        
        return {
            "test_id": test_id,
            "session_id": session_id,
            "test_type": test_type,
            "title": test_title,
            "num_questions": num_questions,
            "estimated_duration_minutes": estimated_duration_minutes
        }
        
    except HTTPException as e:
        # Re-raise HTTPExceptions without modification
        raise e
    except Exception as e:
        import traceback
        print(f"Error in generate_dynamic_test: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating test: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check(db: DatabaseManager = Depends(get_db_manager)):
    """Health check endpoint."""
    db_healthy = await db.health_check()
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        database_connected=db_healthy,
        tests_available=len(app.state.tests_cache)
    )


async def generate_dynamic_random_test(config: Dict[str, Any]) -> TestSchema:
    """Generate a random test from question bank."""
    from app.database import DatabaseManager
    db = DatabaseManager()
    
    # Default configuration
    num_questions = config.get('num_questions', 10)
    difficulty = config.get('difficulty', 'mixed')
    categories = config.get('categories', [])
    failed_questions_only = config.get('failed_questions_only', False)
    source_session_id = config.get('source_session_id')
    user_ip = config.get('user_ip', 'anonymous')
    
    # Build criteria for question selection
    criteria = {
        'difficulty': difficulty,
        'categories': categories if categories else None
    }
    
    # Get questions based on criteria
    print(f"[DEBUG] Generating random test with config: {config}")
    print(f"[DEBUG] Criteria: {criteria}, user_ip: {user_ip}, num_questions: {num_questions}")
    
    try:
        if failed_questions_only and source_session_id:
            questions_data = await db.get_failed_questions_from_session(source_session_id, num_questions)
        elif failed_questions_only:
            questions_data = await db.get_failed_questions(user_ip, num_questions)
        else:
            questions_data = await db.get_questions_by_criteria(criteria, user_ip, num_questions)
        
        print(f"[DEBUG] Retrieved {len(questions_data) if questions_data else 0} questions")
        
    except Exception as e:
        print(f"[ERROR] Error getting questions: {e}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if not questions_data:
        print("[DEBUG] No questions found, checking database...")
        # Debug: check if questions exist at all
        try:
            async with db.get_connection() as conn:
                cursor = await conn.execute("SELECT COUNT(*) FROM questions")
                total_questions = await cursor.fetchone()
                print(f"[DEBUG] Total questions in DB: {total_questions[0] if total_questions else 0}")
        except Exception as debug_e:
            print(f"[DEBUG] Error checking total questions: {debug_e}")
        
        raise HTTPException(status_code=404, detail="No questions available for random test generation")
    
    # Convert to QuestionData objects
    questions = []
    for i, q_data in enumerate(questions_data):
        question = QuestionData(
            id=str(q_data['question_id']),
            question=q_data['question_text'],
            options=q_data['options'],
            correct_answer=q_data['correct_answer'],
            explanation=q_data.get('explanation', ''),
            difficulty=DifficultyLevel(q_data.get('difficulty', 'medium')),
            category=CategoryType(q_data.get('category', 'general')),
            keywords=q_data.get('keywords', []),
            estimated_time_seconds=q_data.get('estimated_time_seconds', 90),
            source_info=q_data.get('source_info', {})
        )
        questions.append(question)
    
    # Generate test ID
    if failed_questions_only:
        test_type = "failed"
    elif categories:
        test_type = "category"
    elif difficulty != 'mixed':
        test_type = "difficulty"
    else:
        test_type = "random"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_id = f"dyn_{test_type}_{timestamp}_{str(uuid.uuid4())[:8]}"
    
    # Create test title
    if failed_questions_only:
        title = f"Repasar Errores - {len(questions)} preguntas"
    elif categories:
        cats_str = ", ".join(categories[:2]) + ("..." if len(categories) > 2 else "")
        title = f"Test por Categorías ({cats_str}) - {len(questions)} preguntas"
    elif difficulty != 'mixed':
        title = f"Test {difficulty.title()} - {len(questions)} preguntas"
    else:
        title = f"Test Aleatorio - {len(questions)} preguntas"
    
    # Calculate estimated duration
    total_time = sum(q.estimated_time_seconds for q in questions)
    estimated_duration = max(5, round(total_time / 60))  # minutes, minimum 5
    
    # Create TestSchema
    test_schema = TestSchema(
        test_id=test_id,
        title=title,
        description=f"Test generado dinámicamente con {len(questions)} preguntas.",
        created_at=datetime.now(),
        category=CategoryType("general"),
        difficulty=DifficultyLevel(difficulty) if difficulty != 'mixed' else DifficultyLevel("mixed"),
        estimated_duration=estimated_duration,
        passing_grade=70,
        questions=questions
    )
    
    # Save dynamic test to database
    await db.save_dynamic_test({
        'test_id': test_id,
        'test_type': test_type,
        'test_title': title,
        'criteria': criteria,
        'question_ids': [q.id for q in questions],
        'user_ip': user_ip
    })
    
    return test_schema


# Utility Functions
def generate_session_id() -> str:
    """Generate unique session ID."""
    return str(uuid.uuid4())


def get_client_ip(request: Request) -> str:
    """Get client IP address."""
    # Check for forwarded headers first (for proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    forwarded = request.headers.get("X-Forwarded")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"


async def get_failed_questions_from_session(session_id: str) -> List[QuestionData]:
    """Get failed questions from a specific session."""
    from app.database import get_db_manager
    
    db = await get_db_manager()
    
    try:
        # Get session data
        session_data = await db.get_session(session_id)
        if not session_data:
            return []
        
        # Get session answers - only the incorrect ones
        answers = await db.get_session_answers(session_id)
        failed_question_ids = [answer['question_id'] for answer in answers if not answer['is_correct']]
        
        if not failed_question_ids:
            return []
        
        # Get the original test to retrieve the failed questions
        test_schema = app.state.tests_cache.get(session_data['test_id'])
        if not test_schema:
            return []
        
        # Extract failed questions
        failed_questions = []
        for question in test_schema.questions:
            if question.id in failed_question_ids:
                # Create a copy to avoid modifying the original
                import copy
                failed_question = copy.deepcopy(question)
                failed_questions.append(failed_question)
        
        return failed_questions
        
    except Exception as e:
        print(f"Error getting failed questions from session {session_id}: {e}")
        return []


async def generate_random_test(config: Dict[str, Any]) -> TestSchema:
    """Generate a random test from existing questions."""
    import random
    from datetime import datetime
    
    # Configuration with defaults
    num_questions = config.get('num_questions', settings.random_test_default_questions)
    categories = config.get('categories', [])
    difficulties = config.get('difficulties', [])
    exclude_test_ids = config.get('exclude_test_ids', [])
    allow_repeats = config.get('allow_repeats', False)
    source_session_id = config.get('source_session_id')
    failed_questions_only = config.get('failed_questions_only', False)
    
    # Collect all available questions
    all_questions = []
    source_test_ids = []
    
    # Special case: Generate test with failed questions from a specific session
    if failed_questions_only and source_session_id:
        all_questions = await get_failed_questions_from_session(source_session_id)
        if not all_questions:
            raise HTTPException(status_code=400, detail="No hay preguntas falladas en la sesión especificada o la sesión no existe")
        source_test_ids = [f"session_{source_session_id}"]
    else:
        # Regular random test generation
        for test_id, test_schema in app.state.tests_cache.items():
            if test_id in exclude_test_ids:
                continue
                
            source_test_ids.append(test_id)
            
            for question in test_schema.questions:
                # Filter by category if specified
                if categories:
                    question_category = question.category.value if hasattr(question.category, 'value') else str(question.category)
                    if question_category not in categories:
                        continue
                
                # Filter by difficulty if specified
                if difficulties:
                    question_difficulty = question.difficulty.value if hasattr(question.difficulty, 'value') else str(question.difficulty)
                    if question_difficulty not in difficulties:
                        continue
                
                all_questions.append(question)
    
    if len(all_questions) < num_questions:
        num_questions = len(all_questions)
    
    if not all_questions:
        raise HTTPException(status_code=400, detail="No questions available for random test generation")
    
    # Select random questions
    if allow_repeats:
        selected_questions = random.choices(all_questions, k=num_questions)
    else:
        selected_questions = random.sample(all_questions, num_questions)
    
    # Reassign IDs to avoid conflicts
    for i, question in enumerate(selected_questions):
        question.id = i + 1
    
    # Generate random test ID
    test_id = f"random_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Set title and description based on test type
    if failed_questions_only:
        title = f"Repaso de Errores ({num_questions} preguntas)"
        description = f"Test de repaso con preguntas falladas de la sesión {source_session_id}"
    else:
        title = f"Test Aleatorio ({num_questions} preguntas)"
        description = "Test generado aleatoriamente a partir de preguntas existentes"
    
    # Create test schema
    random_test = TestSchema(
        test_id=test_id,
        title=title,
        description=description,
        created_at=datetime.now(),
        category="general",
        difficulty="mixed",
        estimated_duration=num_questions * 2,  # 2 minutes per question
        instructions="Responde todas las preguntas. Se evaluará al finalizar el test.",
        passing_grade=settings.default_passing_grade,
        questions=selected_questions,
        scoring={
            "total_points": sum(q.points for q in selected_questions),
            "passing_threshold": settings.default_passing_grade
        },
        statistics={
            "source_tests": len(source_test_ids),
            "total_source_questions": len(all_questions)
        }
    )
    
    return random_test


async def load_all_tests() -> Dict[str, TestSchema]:
    """Load all test files into memory."""
    tests_cache = {}
    
    if not os.path.exists(settings.tests_dir):
        return tests_cache
    
    for filename in os.listdir(settings.tests_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(settings.tests_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                
                # Convert to TestSchema
                test_schema = TestSchema(**test_data)
                tests_cache[test_schema.test_id] = test_schema
                
            except Exception as e:
                print(f"Error loading test file {filename}: {e}")
                continue
    
    return tests_cache


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )