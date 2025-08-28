# Estructura de Almacenamiento de Tests

## Directorios del Sistema

```
test-generator/
├── tests/                     # Tests generados por Claude Code
│   ├── test_20250828_001.json # Test individual
│   ├── test_20250828_002.json
│   └── test_index.json       # Índice de todos los tests
├── results/                   # Resultados de tests realizados
│   ├── results_20250828/     # Resultados por fecha
│   │   ├── session_001.json  # Resultado de sesión
│   │   └── session_002.json
│   └── results_index.json    # Índice de resultados
├── web/                       # Interfaz web
├── api/                       # API backend
└── data/                      # Base de datos SQLite
```

## Formato de Índice de Tests

**Archivo:** `tests/test_index.json`

```json
{
  "last_updated": "2025-08-28T15:30:00Z",
  "total_tests": 3,
  "tests": [
    {
      "test_id": "test_20250828_001",
      "title": "Test de Afiliación a la Seguridad Social - Conceptos Básicos",
      "file_path": "test_20250828_001.json",
      "category": "afiliacion",
      "difficulty": "medium",
      "questions_count": 5,
      "created_at": "2025-08-28T10:30:00Z",
      "estimated_duration": 15,
      "status": "active"
    },
    {
      "test_id": "test_20250828_002", 
      "title": "Test de Cotización y Bases Reguladoras",
      "file_path": "test_20250828_002.json",
      "category": "cotizacion",
      "difficulty": "hard",
      "questions_count": 10,
      "created_at": "2025-08-28T11:15:00Z",
      "estimated_duration": 25,
      "status": "active"
    }
  ],
  "categories": {
    "afiliacion": 1,
    "cotizacion": 1,
    "prestaciones": 0,
    "procedimientos": 0,
    "general": 1
  },
  "difficulty_distribution": {
    "easy": 0,
    "medium": 2,
    "hard": 1,
    "mixed": 0
  }
}
```

## Formato de Resultado de Test

**Archivo:** `results/results_20250828/session_001.json`

```json
{
  "result_id": "result_20250828_001_session_001",
  "test_id": "test_20250828_001",
  "session_id": "session_001",
  "user_info": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_start": "2025-08-28T14:00:00Z"
  },
  "test_session": {
    "started_at": "2025-08-28T14:05:00Z",
    "completed_at": "2025-08-28T14:18:32Z",
    "duration_seconds": 812,
    "status": "completed"
  },
  "score": {
    "correct_answers": 4,
    "incorrect_answers": 1,
    "total_questions": 5,
    "percentage": 80.0,
    "passing_grade": 70,
    "passed": true
  },
  "detailed_answers": [
    {
      "question_id": 1,
      "selected_answer": 1,
      "correct_answer": 1,
      "is_correct": true,
      "time_seconds": 45,
      "question_text": "¿Cuál es la característica principal de la afiliación...",
      "selected_option": "Es obligatoria y única para toda la vida",
      "correct_option": "Es obligatoria y única para toda la vida"
    },
    {
      "question_id": 2,
      "selected_answer": 0,
      "correct_answer": 1,
      "is_correct": false,
      "time_seconds": 38,
      "question_text": "¿En qué casos los familiares del empresario...",
      "selected_option": "Cuando trabajan menos de 20 horas semanales",
      "correct_option": "Cuando conviven en el hogar del empresario y están a su cargo"
    }
  ],
  "category_performance": {
    "afiliacion": {
      "correct": 3,
      "total": 4,
      "percentage": 75.0
    },
    "cotizacion": {
      "correct": 1,
      "total": 1,
      "percentage": 100.0
    }
  },
  "difficulty_performance": {
    "medium": {
      "correct": 3,
      "total": 4,
      "percentage": 75.0
    },
    "hard": {
      "correct": 1,
      "total": 1,
      "percentage": 100.0
    }
  }
}
```

## Formato de Índice de Resultados

**Archivo:** `results/results_index.json`

```json
{
  "last_updated": "2025-08-28T16:00:00Z",
  "total_sessions": 15,
  "total_tests_completed": 12,
  "results_by_date": {
    "2025-08-28": {
      "sessions": 3,
      "completed_tests": 3,
      "average_score": 82.5,
      "directory": "results_20250828/"
    },
    "2025-08-27": {
      "sessions": 5,
      "completed_tests": 4,
      "average_score": 78.2,
      "directory": "results_20250827/"
    }
  },
  "global_statistics": {
    "average_score": 79.8,
    "highest_score": 95.5,
    "lowest_score": 65.0,
    "most_attempted_test": "test_20250828_001",
    "most_difficult_category": "procedimientos",
    "easiest_category": "afiliacion"
  }
}
```

## Convenciones de Nombrado

### Tests
- **Formato ID**: `test_YYYYMMDD_XXX`
- **Archivo**: `test_YYYYMMDD_XXX.json`
- **Ejemplo**: `test_20250828_001.json`

### Resultados
- **Formato ID**: `result_YYYYMMDD_XXX_session_XXX`
- **Directorio**: `results_YYYYMMDD/`
- **Archivo**: `session_XXX.json`
- **Ejemplo**: `results_20250828/session_001.json`

### Sesiones
- **Formato**: `session_XXX` (incremental por día)
- **Reset diario**: Cada día comienza desde session_001

## Operaciones de Mantenimiento

### Agregar Nuevo Test
1. Crear archivo JSON siguiendo el esquema
2. Actualizar `tests/test_index.json`
3. Validar estructura con el schema

### Limpiar Resultados Antiguos
```bash
# Mover resultados de más de 30 días a archivo
find results/ -name "results_*" -mtime +30 -exec tar -czf archive.tar.gz {} \;
```

### Backup de Tests
```bash
# Backup diario de tests generados
tar -czf backup_tests_$(date +%Y%m%d).tar.gz tests/
```