# TODO - Aplicación de Tests de Seguridad Social

## Objetivo
Desarrollar una aplicación web FastAPI que permita realizar tests interactivos basados en los archivos JSON generados manualmente, con estadísticas persistentes en SQLite.

## Plan de Trabajo

### 📋 **FASE 1: Fundamentos y Estructura (MVP)**

#### ✅ **1.1 Preparación del Entorno**
- [x] Docker Compose configurado
- [x] Dockerfile con FastAPI + Python 3.11
- [x] Requirements.txt con dependencias mínimas
- [x] Test JSON de ejemplo creado

#### 🔲 **1.2 Estructura Base de la Aplicación**
- [ ] **`app/main.py`** - Punto de entrada FastAPI
- [ ] **`app/models.py`** - Modelos Pydantic para validación
- [ ] **`app/database.py`** - Conexión SQLite con aiosqlite
- [ ] **`app/schemas.py`** - Esquemas de datos para API
- [ ] **`app/config.py`** - Configuración y variables de entorno

#### 🔲 **1.3 Base de Datos SQLite**
- [ ] **Tabla `test_sessions`** - Sesiones de tests completados
- [ ] **Tabla `user_answers`** - Respuestas individuales por pregunta
- [ ] **Tabla `test_stats`** - Estadísticas agregadas por test
- [ ] **Script de inicialización** de BD
- [ ] **Funciones CRUD** básicas

### 📋 **FASE 2: Backend API REST**

#### 🔲 **2.1 Endpoints Core**
- [ ] **`GET /`** - Página principal (estadísticas + botones)
- [ ] **`GET /api/tests`** - Listar todos los tests disponibles
- [ ] **`GET /api/tests/{test_id}`** - Obtener test específico
- [ ] **`POST /api/sessions`** - Iniciar nueva sesión de test
- [ ] **`GET /api/sessions/{session_id}`** - Estado de sesión actual

#### 🔲 **2.2 Endpoints de Navegación**
- [ ] **`GET /api/sessions/{session_id}/question/{question_id}`** - Pregunta individual
- [ ] **`POST /api/sessions/{session_id}/answers`** - Guardar respuesta (sin validar)
- [ ] **`POST /api/sessions/{session_id}/complete`** - Finalizar test y validar todas las respuestas
- [ ] **`GET /api/sessions/{session_id}/results`** - Obtener resultados finales

#### 🔲 **2.3 Test Aleatorio**
- [ ] **`GET /api/random-test`** - Generar test aleatorio mezclando preguntas
- [ ] **Algoritmo de selección** - X preguntas aleatorias de diferentes tests
- [ ] **Validación de unicidad** - Evitar preguntas repetidas
- [ ] **Metadatos dinámicos** - Generar información del test aleatorio

#### 🔲 **2.4 Estadísticas**
- [ ] **`GET /api/stats`** - Estadísticas generales
- [ ] **`GET /api/stats/recent`** - Últimos tests realizados
- [ ] **Cálculos automáticos** - Promedios, mejores puntuaciones, categorías más difíciles

### 📋 **FASE 3: Frontend HTML/CSS/JS**

#### 🔲 **3.1 Vista Principal**
- [ ] **`templates/index.html`** - Página de inicio
- [ ] **Panel de estadísticas** - Cards con últimos resultados
- [ ] **Botón "Nuevo Test"** - Lista de tests disponibles
- [ ] **Botón "Test Aleatorio"** - Configuración rápida
- [ ] **Histórico reciente** - Últimas 5 sesiones completadas

#### 🔲 **3.2 Interfaz de Test**
- [ ] **`templates/test.html`** - Vista de pregunta individual
- [ ] **Navegación pregunta por pregunta** - Una pregunta por pantalla
- [ ] **Barra de progreso** - Indicador visual del avance
- [ ] **Selección de respuesta** - Radio buttons estilizados
- [ ] **Botones navegación** - Anterior/Siguiente/Saltar
- [ ] **Sin validación inmediata** - Solo guardar respuesta

#### 🔲 **3.3 Resultados Finales**
- [ ] **`templates/results.html`** - Página de resultados
- [ ] **Puntuación final** - Nota numérica y porcentaje
- [ ] **Desglose por categorías** - Rendimiento por tema
- [ ] **Respuestas incorrectas** - Revisión con explicaciones
- [ ] **Botones de acción** - Repetir test, nuevo test, inicio

#### 🔲 **3.4 Estilos CSS (Mobile First)**
- [ ] **`static/css/main.css`** - Estilos principales
- [ ] **Mobile First Design** - Diseño prioritario para smartphones
- [ ] **Tema "Social Security"** - Paleta de colores corporativa
- [ ] **Progressive Enhancement** - Desde móvil hacia desktop
- [ ] **Touch-friendly UI** - Botones grandes, fácil navegación táctil
- [ ] **Componentes reutilizables** - Cards, botones, formularios optimizados para móvil

### 📋 **FASE 4: Funcionalidades Avanzadas**

#### 🔲 **4.1 Test Aleatorio Avanzado**
- [ ] **Configuración personalizada** - Número de preguntas
- [ ] **Filtro por categorías** - Solo afiliación, solo cotización, etc.
- [ ] **Filtro por dificultad** - Fácil, medio, difícil
- [ ] **Modo examen** - Sin navegación hacia atrás

#### 🔲 **4.2 Estadísticas Avanzadas**
- [ ] **Gráficos básicos** - Chart.js para visualizaciones
- [ ] **Evolución temporal** - Progreso a lo largo del tiempo
- [ ] **Comparativa por test** - Qué tests son más difíciles
- [ ] **Export de resultados** - Descargar CSV/JSON

#### 🔲 **4.3 Mejoras UX Mobile**
- [ ] **Confirmación de salida** - Modal de advertencia táctil
- [ ] **Autoguardado** - Guardar progreso automáticamente
- [ ] **Modo oscuro** - Toggle para tema oscuro (mejor para móvil nocturno)
- [ ] **Gestos táctiles** - Swipe para navegar entre preguntas
- [ ] **Orientación responsive** - Soporte portrait/landscape
- [ ] **Accesibilidad móvil** - ARIA labels, botones accesibles para touch

### 📋 **FASE 5: Optimización y Deployment**

#### 🔲 **5.1 Optimización Backend**
- [ ] **Cache en memoria** - Tests cargados una vez
- [ ] **Validación de entrada** - Pydantic en todos los endpoints
- [ ] **Logs estructurados** - Seguimiento de errores
- [ ] **Health checks** - Endpoint de estado

#### 🔲 **5.2 Testing y Validación**
- [ ] **Tests unitarios** - Pytest para funciones core
- [ ] **Tests de integración** - API endpoints
- [ ] **Validación JSON** - Schema compliance
- [ ] **Tests E2E** - Playwright/Selenium básico

#### 🔲 **5.3 Documentation**
- [ ] **API Documentation** - FastAPI automática en /docs
- [ ] **README actualizado** - Instrucciones de uso
- [ ] **Deployment guide** - Docker production

## Arquitectura de Archivos

```
test-generator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configuración y settings
│   ├── database.py          # SQLite connection y setup
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Operaciones CRUD
│   └── routers/
│       ├── __init__.py
│       ├── tests.py         # Endpoints de tests
│       ├── sessions.py      # Endpoints de sesiones
│       └── stats.py         # Endpoints de estadísticas
├── static/
│   ├── css/
│   │   └── main.css         # Estilos principales
│   ├── js/
│   │   ├── test.js          # Lógica de tests
│   │   └── stats.js         # Lógica de estadísticas
│   └── images/              # Assets gráficos
├── templates/
│   ├── base.html            # Template base
│   ├── index.html           # Página principal
│   ├── test.html            # Interface de test
│   ├── results.html         # Resultados
│   └── components/          # Componentes reutilizables
├── tests/                   # Tests JSON (ya existe)
├── data/                    # Base de datos SQLite
└── requirements.txt
```

## Especificaciones Técnicas

### Base de Datos SQLite

```sql
-- Sesiones de tests completados
CREATE TABLE test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    test_id TEXT NOT NULL,
    user_ip TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER,
    score_percentage REAL,
    duration_seconds INTEGER,
    is_random_test BOOLEAN DEFAULT 0
);

-- Respuestas individuales
CREATE TABLE user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer INTEGER,
    correct_answer INTEGER,
    is_correct BOOLEAN,
    time_spent_seconds INTEGER,
    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
);

-- Estadísticas agregadas
CREATE TABLE test_stats (
    test_id TEXT PRIMARY KEY,
    times_taken INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0,
    best_score REAL DEFAULT 0,
    worst_score REAL DEFAULT 100,
    last_taken TIMESTAMP
);
```

### API Response Schemas

```python
class TestSession(BaseModel):
    session_id: str
    test_id: str
    current_question: int
    total_questions: int
    started_at: datetime
    
class QuestionResponse(BaseModel):
    question_id: int
    question: str
    options: List[str]
    category: str
    difficulty: str
    
class TestResults(BaseModel):
    session_id: str
    score: int
    total_questions: int
    percentage: float
    duration_seconds: int
    category_breakdown: Dict[str, Dict]
```

## Criterios de Éxito

### MVP Mobile-First (Fase 1-3)
- ✅ Tests JSON se cargan correctamente
- ✅ Usuario puede completar un test navegando pregunta por pregunta EN MÓVIL
- ✅ Interface optimizada para touch y pantallas pequeñas
- ✅ Resultados se calculan y almacenan en SQLite
- ✅ Página principal muestra estadísticas básicas en formato mobile
- ✅ Test aleatorio funciona mezclando preguntas

### Funcionalidad Completa Mobile (Fase 4-5)
- ✅ Interface totalmente responsive (mobile → tablet → desktop)
- ✅ Navegación táctil fluida y natural
- ✅ Estadísticas detalladas optimizadas para móvil
- ✅ Tests rápidos y eficientes en dispositivos móviles
- ✅ Configuración avanzada accesible desde smartphone
- ✅ Sistema robusto sin errores críticos en cualquier dispositivo

## Principios de Diseño Mobile-First

1. **Contenido esencial primero** - Lo más importante visible sin scroll
2. **Botones de al menos 44px** - Fácil interacción táctil
3. **Tipografía legible** - Mínimo 16px para texto principal
4. **Navegación simple** - Máximo 2-3 niveles de profundidad
5. **Carga rápida** - CSS y JS optimizados para conexiones móviles
6. **Offline-friendly** - Cache de tests descargados para uso sin conexión

## Comandos de Desarrollo

```bash
# Iniciar desarrollo local
docker compose up --build -d

# Ver logs de desarrollo
docker compose logs -f test-viewer

# Rebuild completo
docker compose down && docker compose up --build

# Acceder a la app
open http://localhost:8080

# Ver documentación API
open http://localhost:8080/docs
```