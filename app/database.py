"""Database configuration and connection management."""

import aiosqlite
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from contextlib import asynccontextmanager

from app.config import get_settings

settings = get_settings()


class DatabaseManager:
    """SQLite database manager with async support."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self._connection_pool = {}
        
    async def init_database(self):
        """Initialize database with required tables."""
        await self._create_tables()
        print(f"Database initialized at: {self.db_path}")
    
    async def _create_tables(self):
        """Create all required database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Questions bank table (NEW)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT UNIQUE NOT NULL,
                    bank_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    correct_answer INTEGER NOT NULL,
                    explanation TEXT,
                    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
                    category TEXT,
                    keywords_json TEXT,
                    estimated_time_seconds INTEGER DEFAULT 90,
                    source_info_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Question usage tracking per user (NEW)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS question_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT NOT NULL,
                    user_ip TEXT NOT NULL,
                    times_used INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    correct_count INTEGER DEFAULT 0,
                    incorrect_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(question_id, user_ip),
                    FOREIGN KEY (question_id) REFERENCES questions (question_id)
                )
            """)
            
            # Dynamic tests generation tracking (NEW)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dynamic_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE NOT NULL,
                    test_type TEXT CHECK(test_type IN ('random', 'category', 'difficulty', 'failed_questions')),
                    test_title TEXT NOT NULL,
                    generation_criteria_json TEXT,
                    question_ids_json TEXT NOT NULL,
                    user_ip TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Test sessions table (UPDATED for dynamic tests)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    test_id TEXT NOT NULL,
                    test_title TEXT,
                    user_ip TEXT,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    total_questions INTEGER NOT NULL,
                    correct_answers INTEGER DEFAULT 0,
                    total_points INTEGER DEFAULT 0,
                    points_earned INTEGER DEFAULT 0,
                    score_percentage REAL DEFAULT 0,
                    duration_seconds INTEGER DEFAULT 0,
                    is_dynamic_test BOOLEAN DEFAULT 1,
                    test_type TEXT DEFAULT 'random',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User answers table (UPDATED with question_id reference)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT,
                    selected_answer INTEGER,
                    correct_answer INTEGER,
                    is_correct BOOLEAN DEFAULT 0,
                    points_available INTEGER DEFAULT 1,
                    points_earned INTEGER DEFAULT 1,
                    time_spent_seconds INTEGER DEFAULT 0,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id),
                    FOREIGN KEY (question_id) REFERENCES questions (question_id)
                )
            """)
            
            # Question banks metadata (NEW)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS question_banks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bank_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    file_path TEXT,
                    questions_count INTEGER DEFAULT 0,
                    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Test statistics table (for backward compatibility)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_stats (
                    test_id TEXT PRIMARY KEY,
                    test_title TEXT,
                    times_taken INTEGER DEFAULT 0,
                    average_score REAL DEFAULT 0,
                    best_score REAL DEFAULT 0,
                    worst_score REAL DEFAULT 100,
                    total_questions INTEGER,
                    last_taken TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Session progress table (for tracking current question)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS session_progress (
                    session_id TEXT PRIMARY KEY,
                    current_question_index INTEGER DEFAULT 0,
                    questions_data TEXT, -- JSON array of question IDs
                    answers_data TEXT,   -- JSON object of answers
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
                )
            """)
            
            await db.commit()
            
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = await aiosqlite.connect(self.db_path)
        try:
            yield conn
        finally:
            await conn.close()
    
    # Session Management
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new test session."""
        async with self.get_connection() as db:
            await db.execute("""
                INSERT INTO test_sessions 
                (session_id, test_id, test_title, user_ip, started_at, total_questions, is_dynamic_test, test_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['test_id'],
                session_data.get('test_title', ''),
                session_data.get('user_ip'),
                session_data['started_at'],
                session_data['total_questions'],
                session_data.get('is_dynamic_test', True),
                session_data.get('test_type', 'random')
            ))
            
            # Initialize session progress
            await db.execute("""
                INSERT INTO session_progress (session_id, questions_data, answers_data)
                VALUES (?, ?, ?)
            """, (
                session_data['session_id'],
                json.dumps(session_data.get('question_ids', [])),
                json.dumps({})
            ))
            
            await db.commit()
            return session_data['session_id']
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        async with self.get_connection() as db:
            cursor = await db.execute("""
                SELECT ts.*, sp.current_question_index, sp.questions_data, sp.answers_data
                FROM test_sessions ts
                LEFT JOIN session_progress sp ON ts.session_id = sp.session_id
                WHERE ts.session_id = ?
            """, (session_id,))
            
            row = await cursor.fetchone()
            if not row:
                return None
                
            columns = [description[0] for description in cursor.description]
            session_data = dict(zip(columns, row))
            
            # Parse JSON fields
            if session_data.get('questions_data'):
                session_data['questions_data'] = json.loads(session_data['questions_data'])
            if session_data.get('answers_data'):
                session_data['answers_data'] = json.loads(session_data['answers_data'])
            
            return session_data
    
    async def update_session_progress(self, session_id: str, current_question_index: int, answers_data: Dict):
        """Update session progress."""
        async with self.get_connection() as db:
            await db.execute("""
                UPDATE session_progress 
                SET current_question_index = ?, answers_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (current_question_index, json.dumps(answers_data), session_id))
            await db.commit()
    
    async def complete_session(self, session_id: str, results: Dict[str, Any]):
        """Complete a test session with final results."""
        async with self.get_connection() as db:
            await db.execute("""
                UPDATE test_sessions 
                SET completed_at = ?, correct_answers = ?, total_points = ?, 
                    points_earned = ?, score_percentage = ?, duration_seconds = ?, status = 'completed'
                WHERE session_id = ?
            """, (
                results['completed_at'],
                results['correct_answers'],
                results['total_points'],
                results['points_earned'],
                results['score_percentage'],
                results['duration_seconds'],
                session_id
            ))
            await db.commit()
    
    # Question Bank Management (NEW)
    async def load_question_bank(self, bank_data: Dict[str, Any]) -> int:
        """Load questions from a bank into the database, avoiding duplicates."""
        async with self.get_connection() as db:
            bank_id = bank_data['bank_id']
            
            # Check if bank already exists and compare last updated
            cursor = await db.execute("""
                SELECT last_updated, questions_count FROM question_banks WHERE bank_id = ?
            """, (bank_id,))
            existing_bank = await cursor.fetchone()
            
            # If bank exists and has same number of questions, skip loading
            if existing_bank:
                existing_count = existing_bank[1]
                new_count = len(bank_data.get('questions', []))
                if existing_count == new_count:
                    print(f"📚 Skipping {bank_id}: already loaded with {existing_count} questions")
                    return 0
            
            # Save bank metadata
            await db.execute("""
                INSERT OR REPLACE INTO question_banks 
                (bank_id, title, description, file_path, questions_count, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                bank_id,
                bank_data.get('title', ''),
                bank_data.get('description', ''),
                bank_data.get('file_path', ''),
                len(bank_data.get('questions', []))
            ))
            
            # Delete existing questions from this bank to reload them
            await db.execute("DELETE FROM questions WHERE bank_id = ?", (bank_id,))
            
            # Load questions with duplicate checking by question_id
            questions_loaded = 0
            for question in bank_data.get('questions', []):
                question_id = question['id']
                
                # Check if question already exists (from other banks)
                cursor = await db.execute("SELECT COUNT(*) FROM questions WHERE question_id = ?", (question_id,))
                exists = (await cursor.fetchone())[0] > 0
                
                if exists:
                    print(f"⚠️ Question {question_id} already exists, updating...")
                    await db.execute("""
                        UPDATE questions 
                        SET bank_id = ?, question_text = ?, options_json = ?, correct_answer = ?, 
                            explanation = ?, difficulty = ?, category = ?, keywords_json = ?, 
                            estimated_time_seconds = ?, source_info_json = ?
                        WHERE question_id = ?
                    """, (
                        bank_id,
                        question['question'],
                        json.dumps(question['options']),
                        question['correct_answer'],
                        question.get('explanation', ''),
                        question.get('difficulty', 'medium'),
                        question.get('category', ''),
                        json.dumps(question.get('keywords', [])),
                        question.get('estimated_time_seconds', 90),
                        json.dumps(question.get('source_info', {})),
                        question_id
                    ))
                else:
                    await db.execute("""
                        INSERT INTO questions 
                        (question_id, bank_id, question_text, options_json, correct_answer, 
                         explanation, difficulty, category, keywords_json, estimated_time_seconds, source_info_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        question_id,
                        bank_id,
                        question['question'],
                        json.dumps(question['options']),
                        question['correct_answer'],
                        question.get('explanation', ''),
                        question.get('difficulty', 'medium'),
                        question.get('category', ''),
                        json.dumps(question.get('keywords', [])),
                        question.get('estimated_time_seconds', 90),
                        json.dumps(question.get('source_info', {}))
                    ))
                
                questions_loaded += 1
            
            await db.commit()
            return questions_loaded
    
    async def get_questions_by_criteria(self, criteria: Dict[str, Any], user_ip: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get questions based on criteria with anti-repetition logic."""
        async with self.get_connection() as db:
            # Build base query
            query = """
                SELECT q.*, 
                       COALESCE(qu.times_used, 0) as times_used,
                       COALESCE(qu.last_used, '1970-01-01') as last_used
                FROM questions q
                LEFT JOIN question_usage qu ON q.question_id = qu.question_id AND qu.user_ip = ?
                WHERE 1=1
            """
            params = [user_ip or 'anonymous']
            
            # Apply filters
            if criteria.get('difficulty'):
                if criteria['difficulty'] != 'mixed':
                    query += " AND q.difficulty = ?"
                    params.append(criteria['difficulty'])
            
            if criteria.get('categories'):
                categories = criteria['categories']
                if isinstance(categories, list) and categories:
                    placeholders = ','.join(['?' for _ in categories])
                    query += f" AND q.category IN ({placeholders})"
                    params.extend(categories)
            
            if criteria.get('keywords'):
                # Simple keyword matching in keywords_json
                query += " AND q.keywords_json LIKE ?"
                params.append(f"%{criteria['keywords']}%")
            
            if criteria.get('exclude_question_ids'):
                placeholders = ','.join(['?' for _ in criteria['exclude_question_ids']])
                query += f" AND q.question_id NOT IN ({placeholders})"
                params.extend(criteria['exclude_question_ids'])
            
            # Anti-repetition ordering: less used first, then older usage, then random
            query += """
                ORDER BY 
                    times_used ASC,
                    last_used ASC,
                    RANDOM()
                LIMIT ?
            """
            params.append(limit)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            questions = []
            for row in rows:
                question_data = dict(zip(columns, row))
                # Parse JSON fields
                question_data['options'] = json.loads(question_data['options_json'])
                question_data['keywords'] = json.loads(question_data.get('keywords_json', '[]'))
                question_data['source_info'] = json.loads(question_data.get('source_info_json', '{}'))
                questions.append(question_data)
            
            return questions
    
    async def get_failed_questions(self, user_ip: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get questions that the user answered incorrectly."""
        async with self.get_connection() as db:
            cursor = await db.execute("""
                SELECT DISTINCT q.*, qu.incorrect_count
                FROM questions q
                JOIN question_usage qu ON q.question_id = qu.question_id
                WHERE qu.user_ip = ? AND qu.incorrect_count > 0
                ORDER BY qu.incorrect_count DESC, qu.last_used ASC, RANDOM()
                LIMIT ?
            """, (user_ip, limit))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            questions = []
            for row in rows:
                question_data = dict(zip(columns, row))
                question_data['options'] = json.loads(question_data['options_json'])
                question_data['keywords'] = json.loads(question_data.get('keywords_json', '[]'))
                question_data['source_info'] = json.loads(question_data.get('source_info_json', '{}'))
                questions.append(question_data)
            
            return questions
    
    async def update_question_usage(self, question_id: str, user_ip: str, is_correct: bool):
        """Update question usage statistics."""
        async with self.get_connection() as db:
            await db.execute("""
                INSERT OR REPLACE INTO question_usage 
                (question_id, user_ip, times_used, last_used, correct_count, incorrect_count, updated_at)
                VALUES (
                    ?, ?, 
                    COALESCE((SELECT times_used FROM question_usage WHERE question_id = ? AND user_ip = ?), 0) + 1,
                    CURRENT_TIMESTAMP,
                    COALESCE((SELECT correct_count FROM question_usage WHERE question_id = ? AND user_ip = ?), 0) + ?,
                    COALESCE((SELECT incorrect_count FROM question_usage WHERE question_id = ? AND user_ip = ?), 0) + ?,
                    CURRENT_TIMESTAMP
                )
            """, (
                question_id, user_ip,
                question_id, user_ip,  # for times_used lookup
                question_id, user_ip,  # for correct_count lookup  
                1 if is_correct else 0,
                question_id, user_ip,  # for incorrect_count lookup
                0 if is_correct else 1
            ))
            await db.commit()
    
    async def save_dynamic_test(self, test_data: Dict[str, Any]) -> str:
        """Save dynamically generated test."""
        async with self.get_connection() as db:
            await db.execute("""
                INSERT INTO dynamic_tests 
                (test_id, test_type, test_title, generation_criteria_json, question_ids_json, user_ip)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                test_data['test_id'],
                test_data['test_type'],
                test_data['test_title'],
                json.dumps(test_data.get('criteria', {})),
                json.dumps(test_data['question_ids']),
                test_data.get('user_ip')
            ))
            await db.commit()
            return test_data['test_id']
    
    async def get_available_categories(self) -> List[str]:
        """Get all available question categories."""
        async with self.get_connection() as db:
            cursor = await db.execute("SELECT DISTINCT category FROM questions WHERE category IS NOT NULL AND category != '' ORDER BY category")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def get_question_stats(self) -> Dict[str, Any]:
        """Get statistics about the question bank."""
        async with self.get_connection() as db:
            # Total questions
            cursor = await db.execute("SELECT COUNT(*) FROM questions")
            total_questions = (await cursor.fetchone())[0]
            
            # Questions by difficulty
            cursor = await db.execute("""
                SELECT difficulty, COUNT(*) 
                FROM questions 
                GROUP BY difficulty
                ORDER BY difficulty
            """)
            difficulty_stats = dict(await cursor.fetchall())
            
            # Questions by category
            cursor = await db.execute("""
                SELECT category, COUNT(*) 
                FROM questions 
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY COUNT(*) DESC
            """)
            category_stats = dict(await cursor.fetchall())
            
            # Question banks
            cursor = await db.execute("SELECT COUNT(*) FROM question_banks")
            total_banks = (await cursor.fetchone())[0]
            
            return {
                'total_questions': total_questions,
                'total_banks': total_banks,
                'difficulty_distribution': difficulty_stats,
                'category_distribution': category_stats
            }
    
    # Answer Management
    async def save_answer(self, session_id: str, answer_data: Dict[str, Any]):
        """Save user answer."""
        async with self.get_connection() as db:
            await db.execute("""
                INSERT OR REPLACE INTO user_answers 
                (session_id, question_id, question_text, selected_answer, correct_answer, 
                 is_correct, points_available, points_earned, time_spent_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                answer_data['question_id'],
                answer_data.get('question_text', ''),
                answer_data['selected_answer'],
                answer_data['correct_answer'],
                answer_data['is_correct'],
                answer_data.get('points_available', 1),
                answer_data.get('points_earned', 0),
                answer_data.get('time_spent_seconds', 0)
            ))
            await db.commit()
    
    async def get_session_answers(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all answers for a session."""
        async with self.get_connection() as db:
            cursor = await db.execute("""
                SELECT * FROM user_answers WHERE session_id = ? ORDER BY question_id
            """, (session_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
    
    # Statistics
    async def update_test_stats(self, test_id: str, test_title: str, score: float, total_questions: int):
        """Update statistics for a test."""
        async with self.get_connection() as db:
            # Get current stats
            cursor = await db.execute("SELECT * FROM test_stats WHERE test_id = ?", (test_id,))
            current_stats = await cursor.fetchone()
            
            if current_stats:
                # Update existing stats
                times_taken = current_stats[2] + 1
                current_avg = current_stats[3]
                new_avg = ((current_avg * (times_taken - 1)) + score) / times_taken
                best_score = max(current_stats[4], score)
                worst_score = min(current_stats[5], score)
                
                await db.execute("""
                    UPDATE test_stats 
                    SET times_taken = ?, average_score = ?, best_score = ?, worst_score = ?,
                        last_taken = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE test_id = ?
                """, (times_taken, new_avg, best_score, worst_score, test_id))
            else:
                # Create new stats
                await db.execute("""
                    INSERT INTO test_stats 
                    (test_id, test_title, times_taken, average_score, best_score, worst_score, total_questions, last_taken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (test_id, test_title, 1, score, score, score, total_questions))
            
            await db.commit()
    
    async def get_general_stats(self) -> Dict[str, Any]:
        """Get general application statistics."""
        async with self.get_connection() as db:
            # Total completed sessions
            cursor = await db.execute("SELECT COUNT(*) FROM test_sessions WHERE status = 'completed'")
            total_sessions = (await cursor.fetchone())[0]
            
            # Average score across all tests
            cursor = await db.execute("SELECT AVG(score_percentage) FROM test_sessions WHERE status = 'completed'")
            avg_score_result = await cursor.fetchone()
            avg_score = avg_score_result[0] if avg_score_result[0] is not None else 0
            
            # Recent sessions
            cursor = await db.execute("""
                SELECT session_id, test_id, test_title, score_percentage, completed_at, duration_seconds
                FROM test_sessions 
                WHERE status = 'completed'
                ORDER BY completed_at DESC 
                LIMIT 5
            """)
            recent_sessions_data = await cursor.fetchall()
            
            # Test statistics
            cursor = await db.execute("SELECT * FROM test_stats ORDER BY times_taken DESC")
            test_stats_data = await cursor.fetchall()
            
            return {
                'total_sessions_completed': total_sessions,
                'average_score_all_tests': round(avg_score, 2),
                'recent_sessions': recent_sessions_data,
                'test_statistics': test_stats_data
            }
    
    async def health_check(self) -> bool:
        """Check if database is accessible."""
        try:
            async with self.get_connection() as db:
                await db.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False


# Global database instance
db_manager = DatabaseManager()


async def init_database():
    """Initialize database on startup."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    await db_manager.init_database()


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager."""
    return db_manager


if __name__ == "__main__":
    # Test database setup
    async def test_db():
        await init_database()
        print("Database test completed successfully!")
    
    asyncio.run(test_db())