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
            # Test sessions table
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
                    is_random_test BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User answers table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id INTEGER NOT NULL,
                    question_text TEXT,
                    selected_answer INTEGER,
                    correct_answer INTEGER,
                    is_correct BOOLEAN DEFAULT 0,
                    points_available INTEGER DEFAULT 1,
                    points_earned INTEGER DEFAULT 0,
                    time_spent_seconds INTEGER DEFAULT 0,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
                )
            """)
            
            # Test statistics table
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
                (session_id, test_id, test_title, user_ip, started_at, total_questions, is_random_test)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['test_id'],
                session_data.get('test_title', ''),
                session_data.get('user_ip'),
                session_data['started_at'],
                session_data['total_questions'],
                session_data.get('is_random_test', False)
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