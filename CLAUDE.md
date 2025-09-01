# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a **Generic Test Generator** - a FastAPI web application that provides an interactive mobile-first interface for taking educational tests from a dynamic question bank system. The system supports any subject matter through standardized JSON question banks with intelligent anti-repetition algorithms.

### Core Components

- **FastAPI Application** (`app/main.py`): Complete application with dynamic test generation, admin panel, and session management
- **SQLite Database** (`app/database.py`): Async database with question banks, usage tracking, and anti-repetition algorithms
- **Pydantic Schemas** (`app/schemas.py`): Type validation for question banks, dynamic tests, and API responses
- **HTML Templates** (`templates/`): Mobile-first responsive interface with admin panel
- **Question Banks**: JSON files in `tests/bank_*.json` format loaded into database automatically
- **Admin Panel** (`/admin`): Web interface for uploading and managing question banks

### Key Design Patterns

1. **Question Bank System**: All questions stored in database, loaded from `bank_*.json` files with duplicate checking
2. **Dynamic Test Generation**: Tests created on-demand with 3 modes (Random, Category, Difficulty)
3. **Anti-Repetition Algorithm**: Tracks question usage per user to minimize repetition
4. **Session-based Testing**: Each test session has unique ID, tracks progress and question usage
5. **Admin Management**: Web-based upload and management of question banks with validation
6. **Mobile-first UI**: Responsive design optimized for touch interfaces with 44px minimum button sizes
7. **Duration Calculation**: Test duration based on sum of individual question estimated times

## Development Commands

### Docker (Primary)
```bash
# Build and start the application
docker compose up --build -d

# View logs
docker compose logs -f test-generator

# Stop application
docker compose down

# Complete rebuild
docker compose down -v && docker compose up --build
```

### Python Direct (Development)
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main

# With auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Testing
No automated test suite is configured. Testing is done manually through the web interface.

## JSON Test Format

All tests must follow the schema defined in `test-schema.json`. Key structure:

- **test_id**: Unique identifier (format: `test_YYYYMMDD_XXX`)
- **questions**: Array of 5-70 questions with 4 options each
- **category**: One of `afiliacion|cotizacion|prestaciones|procedimientos|general`
- **difficulty**: One of `easy|medium|hard|mixed`

Example question structure:
```json
{
  "id": 1,
  "question": "Question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Why this is correct...",
  "difficulty": "medium",
  "category": "general"
}
```

## Database Schema

SQLite database with these main tables:
- **test_sessions**: Session tracking, scores, completion status
- **session_answers**: Individual question responses with timing
- **test_statistics**: Aggregated test performance data

Database manager in `app/database.py` handles all async operations using aiosqlite.

## API Endpoints

### Web Interface
- `/` - Main page with statistics and test selection
- `/test/{session_id}` - Test taking interface (redirects to questions)
- `/test/{session_id}/question/{index}` - Individual question pages
- `/results/{session_id}` - Detailed results page

### REST API
- `GET /api/tests` - List available tests
- `POST /api/sessions` - Start new test session (normal or random)
- `GET /api/sessions/{id}/question/{index}` - Get specific question
- `POST /api/sessions/{id}/answers` - Save answer without validation
- `POST /api/sessions/{id}/complete` - Complete test and calculate results
- `GET /api/stats` - General statistics

## Configuration

Environment variables in `app/config.py`:
- **PORT**: Application port (default: 8080)
- **TESTS_DIR**: Directory containing JSON test files
- **DATABASE_PATH**: SQLite database file location
- **DEFAULT_PASSING_GRADE**: Minimum percentage to pass (default: 70)

## File Structure

```
app/
├── main.py          # Complete FastAPI application
├── database.py      # Async SQLite management
├── schemas.py       # Pydantic models
└── config.py        # Settings and configuration

templates/           # Jinja2 HTML templates
├── base.html        # Responsive base template
├── index.html       # Home page with stats
├── test.html        # Question interface
├── results.html     # Results display
└── redirect.html    # Navigation helper

tests/               # JSON test files directory
data/                # SQLite database storage
```

## Working with Tests

### Template Files Reference
The project includes two essential reference files for working with tests:

#### **`test-template.json`** (Primary Template)
- **Purpose**: Complete, ready-to-copy template for new tests
- **Usage**: `cp test-template.json tests/test_YYYYMMDD_XXX.json`
- **Features**: Full schema compliance, all fields included, optimal structure
- **Recommendation**: **Use this as base for all new tests**

#### **`test-schema.json`** (Technical Specification)  
- **Purpose**: JSON Schema definition for validation and documentation
- **Usage**: Reference for understanding field requirements and formats
- **Features**: Type definitions, validation rules, field descriptions
- **Recommendation**: Consult when building custom tools or debugging format

### Creating New Tests
1. **Copy Template**: `cp test-template.json tests/test_YYYYMMDD_XXX.json`
2. **Edit Content**: Update test_id, title, questions, and metadata
3. **Flexible Categories**: Any string is valid for category fields
4. **Auto-loading**: Application loads from `tests/*.json` on startup
5. **Format Normalization**: System handles different JSON structures automatically

## Documentation Strategy

- **README.md**: Contains only generic user information and deployment instructions
- **TODO.md**: Used for step-by-step development tracking and task management
- **CLAUDE.md**: Technical architecture and development guidance (this file)

## Common Tasks

### Creating New Test
1. **Use Primary Template**: Copy `test-template.json` as starting point
2. **Follow Naming Convention**: `test_YYYYMMDD_XXX` format for test_id
3. **Flexible Structure**: System normalizes different JSON formats automatically
4. **Question Format**: Ensure 4 options per question with correct_answer index (0-3)
5. **Automatic Validation**: Categories and most fields are flexible, validation happens on load

### Troubleshooting
- Check logs: `docker compose logs -f test-generator`
- Database issues: Check `/app/data/tests_stats.db` permissions
- Test loading: Verify JSON syntax and schema compliance
- Health check: `curl http://localhost:8080/health`

## Mobile-First Features

- Responsive breakpoints at 768px and 1024px
- Touch targets minimum 44px
- Progressive question navigation without validation
- Optimized for slow mobile connections
- Swipe-friendly interface design
- Clean question display without metadata clutter
- Focus on question content and answer options

## Development Workflow

### Important: Docker Development
**CRITICAL**: Para aplicar cambios durante el desarrollo, siempre ejecutar:
```bash
docker compose down && docker compose up --build
```
Los cambios en código **NO** se reflejan automáticamente. Docker debe ser reiniciado para aplicar modificaciones.

### Recent Enhancements (2025-08)

#### Critical Bug Fixes (31/08/2025) - LATEST
- ✅ **Detailed Results Fix**: Fixed critical issue where detailed answers weren't displayed in results page
- ✅ **Field Mismatch Resolution**: Resolved `question_id` vs `id` field inconsistency in dynamic tests (main.py:635-637)
- ✅ **Dual Search Implementation**: Added fallback search logic (question_id first, then id) for question matching
- ✅ **Complete Verification**: All functionality verified working 100% with Playwright testing
- ✅ **Code Cleanup**: Removed temporary debug logs after successful fixes

#### Interface Optimization (29/08/2025)
- ✅ **Simplified Navigation**: Removed top navigation bar, added header Inicio button
- ✅ **Redesigned Test Selection**: 3 main buttons (New Test, Random Test, Review Failures)
- ✅ **JSON-based Tests**: Direct loading from tests/*.json files 
- ✅ **Improved Random Tests**: Better question distribution, avoid excessive repetition
- ✅ **Clean Database**: Reset sessions, updated schema
- ✅ **Clean Question Interface**: Removed category/difficulty labels from question display for cleaner UI
- ✅ **Dynamic System Completion**: Full end-to-end dynamic test system with detailed results

#### Previous Features
- ✅ **Detailed Results**: Complete information about incorrect answers with explanations and sources
- ✅ **Source Information**: Shows document, section, page and legal reference for each question  
- ✅ **Review Tests**: Automatic generation of tests with only failed questions
- ✅ **Enhanced JavaScript**: Robust functions for show/hide results and sharing

### Schema Evolution
- `AnswerDetail` incluye ahora `source_info` para información de fuente
- `RandomTestConfig` soporta `failed_questions_only` y `source_session_id`
- Soporte completo para tests de repaso basados en sesiones anteriores

### Testing & Validation
- Health endpoint: `http://localhost:8080/health`
- Validar cambios navegando a resultados de tests completados
- Probar funcionalidad "Repasar Errores" desde el historial
- Verificar visualización de información de fuente en respuestas detalladas