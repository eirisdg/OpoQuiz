# TODO - Test Generator

## Estado Actual: ✅ **SISTEMA COMPLETO Y OPTIMIZADO 100% FUNCIONAL**
Sistema completamente funcional con API REST, interfaz móvil-first optimizada, navegación responsiva, modales móviles mejorados y UX pulida en todas las plataformas.

## 🚀 Últimas Funcionalidades Implementadas (Septiembre 2025)

### ✅ MEJORAS UX MOBILE COMPLETADAS (02/09/2025)
1. ✅ **Navegación móvil rediseñada** - Botones fijos al fondo en móvil, cards normales en desktop
2. ✅ **Espaciado dinámico** - Eliminado padding fijo excesivo, flujo de contenido natural  
3. ✅ **Layout modal mejorado** - Botones apilados verticalmente en móvil con orden correcto
4. ✅ **Consistencia de headers** - Anchos unificados entre admin y panel principal
5. ✅ **Visibilidad de footer** - Footer visible correctamente en móvil sin solapamiento
6. ✅ **Botón cerrar modal** - Posicionamiento correcto en esquina superior derecha

### Funcionalidades Implementadas (Agosto 2025)

### ✅ CRÍTICO RESUELTO: Respuestas Detalladas Funcionales (31/08/2025)
1. ✅ **Fix crítico aplicado** - Problema de field mismatch `question_id` vs `id` resuelto
2. ✅ **Búsqueda dual implementada** - Sistema busca por `question_id` primero, luego por `id`
3. ✅ **Respuestas detalladas 100% operativas** - Todas las preguntas se muestran con contenido completo
4. ✅ **Debug sistemático completado** - Issue root cause identificado y corregido
5. ✅ **Verificación completa con Playwright** - Todas las funcionalidades probadas y funcionales

### Optimización de Interfaz (29/08/2025)
1. ✅ **Navegación simplificada** - Eliminada barra superior, botón Inicio en header
2. ✅ **Selección de tests rediseñada** - 3 botones principales: Nuevo Test, Test Aleatorio, Repasar Fallos
3. ✅ **Tests basados en JSON** - Carga directa desde archivos tests/*.json
4. ✅ **Tests aleatorios mejorados** - Evita repeticiones, preguntas de múltiples fuentes
5. ✅ **Base de datos limpia** - Esquema actualizado y sesiones reiniciadas
6. ✅ **Interfaz de pregunta limpia** - Eliminada barra de categoría/dificultad para UI más simple
7. ✅ **Sistema dinámico completo** - End-to-end funcional con resultados detallados

### Funcionalidades Previas
1. ✅ **Resultados detallados completos** - Respuestas incorrectas con explicaciones y fuentes
2. ✅ **Información de fuente** - Documento, sección, página y referencia legal por pregunta
3. ✅ **Tests de repaso** - Generación automática con preguntas falladas de sesiones previas
4. ✅ **JavaScript robusto** - Funciones mejoradas para mostrar/ocultar y compartir resultados

## 🔧 Importante para Desarrollo
**CRITICAL**: Para aplicar cambios siempre ejecutar:
```bash
docker compose down && docker compose up --build
```

## 🚀 Próximas Funcionalidades Prioritarias

### ALTA PRIORIDAD (Solicitado por Usuario)

1. **🏛️ Sistema Multi-Base de Datos por Oposición** - ARQUITECTURAL CRÍTICO
   - **Problema**: Base de datos actual específica para Seguridad Social
   - **Solución**: Sistema para múltiples tipos de oposiciones
   - **Funcionalidades necesarias**:
     - Selección de base de datos al abrir la aplicación por primera vez
     - Botón en pantalla principal para cambiar entre bases de datos
     - Gestión independiente de estadísticas por oposición
     - Arquitectura escalable para nuevas oposiciones
   - **Implementación sugerida**:
     - Base de datos separada por oposición: `data/oposicion_[tipo].db`
     - Configuración persistente de oposición seleccionada
     - Interface de selección/cambio con preview de contenido
     - Migration automático de datos existentes

2. **🗑️ Eliminación Individual de Preguntas** - GESTIÓN CRÍTICA
   - Interface admin para eliminar preguntas específicas de bancos cargados
   - Navegador de preguntas con búsqueda y filtros
   - Botones de eliminación con confirmación 
   - Eliminación en cascada de respuestas/sesiones relacionadas
   - API endpoint: `DELETE /api/questions/{question_id}`

3. **📱 Navegación por Gestos Móviles** - UX ENHANCEMENT
   - Deslizar izquierda → siguiente pregunta
   - Deslizar derecha → pregunta anterior
   - Solo activo en versión móvil (≤767px)
   - Feedback visual durante el gesto
   - Integración con botones existentes

4. **📚 Actualización Completa de Documentación** - MAINTENANCE
   - README.md completamente renovado
   - Comentarios en línea en todo el código
   - Documentación API automática
   - Guía de usuario final
   - Instrucciones de despliegue actualizadas

### Mejoras Sistema Dinámico (Prioridad Media)
5. **Validación Admin Panel** - Mejorar validación de archivos JSON subidos
6. **Gestión de duplicados** - Interface para revisar y resolver preguntas duplicadas
7. **Estadísticas de bancos** - Vista de rendimiento por banco de preguntas
8. **Export/Import** - Backup y restauración de bancos de preguntas

### Mejoras UX/UI (Prioridad Baja)
9. **Gráficos y visualizaciones** - Chart.js para estadísticas avanzadas
10. **Modo oscuro** - Toggle para tema oscuro
11. **Confirmación de acciones** - Modales para eliminar/resetear datos
12. **Loading states** - Indicadores de carga para operaciones lentas

### Optimización Técnica
9. **Testing automatizado** - Tests unitarios y E2E para nuevas funcionalidades
10. **Optimizaciones de rendimiento** - Cache avanzado para consultas de preguntas
11. **Logs estructurados** - Mejor tracking de errores y uso del sistema
12. **Health checks mejorados** - Estado detallado del sistema

## Objetivo
Desarrollar una aplicación web FastAPI que permita realizar tests interactivos basados en los archivos JSON generados manualmente, con estadísticas persistentes en SQLite.

## Plan de Trabajo

### ✅ **FASE 1: Fundamentos y Estructura (MVP) - COMPLETADA**

#### ✅ **1.1 Preparación del Entorno**
- [x] Docker Compose configurado
- [x] Dockerfile con FastAPI + Python 3.11
- [x] Requirements.txt con dependencias mínimas
- [x] Test JSON de ejemplo creado

#### ✅ **1.2 Estructura Base de la Aplicación**
- [x] **`app/main.py`** - Punto de entrada FastAPI (818 líneas - COMPLETO)
- [x] **`app/schemas.py`** - Modelos Pydantic para validación (262 líneas)
- [x] **`app/database.py`** - Conexión SQLite con aiosqlite (326 líneas)
- [x] **`app/config.py`** - Configuración y variables de entorno (113 líneas)

#### ✅ **1.3 Base de Datos SQLite**
- [x] **Tabla `test_sessions`** - Sesiones de tests completados
- [x] **Tabla `session_answers`** - Respuestas individuales por pregunta
- [x] **Tabla `test_statistics`** - Estadísticas agregadas por test
- [x] **Script de inicialización** de BD
- [x] **Funciones CRUD** básicas con async/await

### ✅ **FASE 2: Backend API REST - COMPLETADA**

#### ✅ **2.1 Endpoints Core**
- [x] **`GET /`** - Página principal (estadísticas + botones)
- [x] **`GET /api/tests`** - Listar todos los tests disponibles
- [x] **`GET /api/tests/{test_id}`** - Obtener test específico
- [x] **`POST /api/sessions`** - Iniciar nueva sesión de test
- [x] **`GET /health`** - Health check endpoint

#### ✅ **2.2 Endpoints de Navegación**
- [x] **`GET /api/sessions/{session_id}/question/{question_index}`** - Pregunta individual
- [x] **`POST /api/sessions/{session_id}/answers`** - Guardar respuesta (sin validar)
- [x] **`POST /api/sessions/{session_id}/complete`** - Finalizar test y validar todas las respuestas
- [x] **`GET /results/{session_id}`** - Página de resultados finales

#### ✅ **2.3 Test Aleatorio**
- [x] **Algoritmo de selección** - X preguntas aleatorias de diferentes tests
- [x] **Configuración avanzada** - Filtros por categoría, dificultad, exclusiones
- [x] **Validación de unicidad** - Evitar preguntas repetidas
- [x] **Metadatos dinámicos** - Generar información del test aleatorio

#### ✅ **2.4 Estadísticas**
- [x] **`GET /api/stats`** - Estadísticas generales
- [x] **Cálculos automáticos** - Promedios, mejores puntuaciones, categorías más difíciles
- [x] **Estadísticas de sesiones** - Histórico completo en base de datos

### ✅ **FASE 3: Frontend HTML/CSS/JS - COMPLETADA**

#### ✅ **3.1 Vista Principal**
- [x] **`templates/index.html`** - Página de inicio (10KB - COMPLETA)
- [x] **Panel de estadísticas** - Cards con últimos resultados
- [x] **Botón "Nuevo Test"** - Lista de tests disponibles
- [x] **Botón "Test Aleatorio"** - Configuración avanzada
- [x] **Histórico reciente** - Últimas sesiones completadas

#### ✅ **3.2 Interfaz de Test**
- [x] **`templates/test.html`** - Vista de pregunta individual (13KB)
- [x] **Navegación pregunta por pregunta** - Una pregunta por pantalla
- [x] **Barra de progreso** - Indicador visual del avance
- [x] **Selección de respuesta** - Radio buttons estilizados
- [x] **Botones navegación** - Anterior/Siguiente/Finalizar
- [x] **Sin validación inmediata** - Solo guardar respuesta

#### ✅ **3.3 Resultados Finales**
- [x] **`templates/results.html`** - Página de resultados (17KB)
- [x] **Puntuación final** - Nota numérica y porcentaje
- [x] **Desglose por categorías** - Rendimiento por tema
- [x] **Respuestas incorrectas** - Revisión con explicaciones
- [x] **Botones de acción** - Repetir test, nuevo test, inicio

#### ✅ **3.4 Estilos CSS (Mobile First)**
- [x] **`templates/base.html`** - Template base con CSS integrado (12KB)
- [x] **Mobile First Design** - Diseño prioritario para smartphones
- [x] **Tema responsivo** - Paleta de colores moderna
- [x] **Progressive Enhancement** - Desde móvil hacia desktop
- [x] **Touch-friendly UI** - Botones grandes, fácil navegación táctil
- [x] **Componentes reutilizables** - Cards, botones, formularios optimizados

### ✅ **FASE 4: Funcionalidades Avanzadas - COMPLETADA**

#### ✅ **4.1 Test Aleatorio Avanzado - COMPLETADO**
- [x] **Configuración personalizada** - Número de preguntas
- [x] **Filtro por categorías** - Solo afiliación, solo cotización, etc.
- [x] **Filtro por dificultad** - Fácil, medio, difícil
- [x] **Exclusión de tests** - Evitar tests ya tomados
- [x] **Control de repeticiones** - Allow_repeats configurable

#### ✅ **4.2 Resultados Detallados Mejorados - COMPLETADO (2025-08)**
- [x] **Respuestas incorrectas** - Mostrar respuesta correcta claramente
- [x] **Explicaciones completas** - Información de cada pregunta cuando esté disponible
- [x] **Información de fuente** - Documento, sección, página, referencia legal
- [x] **Interfaz mejorada** - Estilos diferenciados para correcto/incorrecto
- [x] **Botón mostrar/ocultar** - JavaScript robusto para toggle de detalles

#### ✅ **4.3 Tests de Repaso - COMPLETADO (2025-08)**
- [x] **Generación automática** - Tests con solo preguntas falladas
- [x] **Integración con historial** - Botón "Repasar Errores" en sesiones
- [x] **Schema actualizado** - Soporte para failed_questions_only
- [x] **Filtrado inteligente** - Solo preguntas respondidas incorrectamente
- [x] **Interfaz integrada** - Sin configuración adicional requerida

#### ✅ **4.4 Sistema Dinámico de Preguntas - COMPLETADO (2025-08)**
- [x] **Base de datos rediseñada** - 8 tablas: questions, question_usage, dynamic_tests, test_sessions, user_answers, question_banks, test_stats, session_progress
- [x] **Banco de preguntas** - Carga automática desde archivos bank_*.json  
- [x] **3 modos dinámicos** - Random, Category, Difficulty con configuración
- [x] **Anti-repetición** - Algoritmo inteligente basado en uso por usuario
- [x] **Admin panel** - Upload y gestión de bancos de preguntas
- [x] **Validación automática** - Detección y manejo de preguntas duplicadas
- [x] **Schema consistency** - IDs estandarizados como string en toda la aplicación
- [x] **Type consistency fix** - Corregidas inconsistencias críticas ID (string vs int) en schemas.py
- [x] **Database documentation** - Documentado esquema completo de 8 tablas con tipos correctos

#### 🔲 **4.5 Estadísticas Avanzadas**
- [ ] **Gráficos básicos** - Chart.js para visualizaciones por banco
- [ ] **Evolución temporal** - Progreso a lo largo del tiempo
- [ ] **Comparativa por banco** - Qué bancos son más difíciles
- [ ] **Export de resultados** - Descargar CSV/JSON
- [ ] **Dashboard admin** - Vista de uso por banco y pregunta

#### 🔲 **4.6 Mejoras UX Mobile**
- [ ] **Confirmación de salida** - Modal de advertencia táctil
- [ ] **Autoguardado** - Guardar progreso automáticamente
- [ ] **Modo oscuro** - Toggle para tema oscuro (mejor para móvil nocturno)
- [ ] **Gestos táctiles** - Swipe para navegar entre preguntas
- [ ] **Orientación responsive** - Soporte portrait/landscape
- [ ] **Accesibilidad móvil** - ARIA labels, botones accesibles para touch
- [ ] **Loading states** - Spinners y feedback durante carga de tests

### 📋 **FASE 5: Optimización y Deployment**

#### 🔲 **5.1 Optimización Backend**
- [ ] **Cache en memoria** - Preguntas cargadas una vez, actualización inteligente
- [ ] **Validación de entrada mejorada** - Pydantic en todos los endpoints nuevos
- [ ] **Logs estructurados** - Seguimiento detallado de uso de preguntas y bancos
- [ ] **Health checks mejorados** - Estado de BD, bancos cargados, estadísticas
- [ ] **API rate limiting** - Protección contra abuso del sistema
- [ ] **Backup automático** - Copias de seguridad programadas de la BD

#### 🔲 **5.2 Testing y Validación**
- [ ] **Tests unitarios** - Pytest para algoritmo anti-repetición y generación dinámica
- [ ] **Tests de integración** - API endpoints del sistema dinámico
- [ ] **Validación JSON** - Schema compliance para bancos de preguntas
- [ ] **Tests E2E** - Flujo completo de tests dinámicos
- [ ] **Performance testing** - Carga con múltiples usuarios y bancos grandes

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

-- 8 tablas del sistema dinámico completo:
-- 1. questions - Banco de preguntas con question_id TEXT
-- 2. question_usage - Estadísticas de uso anti-repetición
-- 3. dynamic_tests - Tests generados dinámicamente
-- 4. test_sessions - Sesiones de tests completados
-- 5. user_answers - Respuestas individuales por pregunta
-- 6. question_banks - Metadatos de bancos JSON cargados
-- 7. test_stats - Estadísticas agregadas (compatibilidad)
-- 8. session_progress - Progreso actual de sesiones activas

CREATE TABLE user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id TEXT NOT NULL,  -- Cambio crítico: TEXT para consistencia
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

### ✅ MVP Mobile-First (Fase 1-3) - **COMPLETADO**
- ✅ Tests JSON se cargan correctamente
- ✅ Usuario puede completar un test navegando pregunta por pregunta EN MÓVIL
- ✅ Interface optimizada para touch y pantallas pequeñas
- ✅ Resultados se calculan y almacenan en SQLite
- ✅ Página principal muestra estadísticas básicas en formato mobile
- ✅ Test aleatorio funciona mezclando preguntas

### ✅ Funcionalidad Completa Mobile (Fase 4-5) - **COMPLETADO EN GRAN PARTE**
- ✅ Interface totalmente responsive (mobile → tablet → desktop)
- ✅ Navegación táctil fluida y natural
- ✅ Estadísticas detalladas optimizadas para móvil
- ✅ Tests rápidos y eficientes en dispositivos móviles
- ✅ Configuración avanzada accesible desde smartphone
- ⏳ **PENDIENTE**: Verificar funcionamiento sin errores críticos

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

## Arquitectura Multi-Oposición (Detalles de Implementación)

### 🏗️ Propuesta de Arquitectura
```
data/
├── seguridad_social.db          # Base de datos actual (migrada)
├── policia_nacional.db          # Nueva oposición
├── educacion.db                 # Otra oposición
├── config.json                  # Configuración de oposición activa
└── oposiciones_metadata.json    # Información de cada oposición
```

### 🔧 Cambios Necesarios en el Código
1. **database.py**:
   - Parámetro `db_name` en DatabaseManager
   - Función `list_available_databases()`
   - Función `switch_database(db_name)`

2. **main.py**:
   - Endpoint `GET /api/oposiciones` - Listar oposiciones disponibles
   - Endpoint `POST /api/switch-oposicion` - Cambiar base de datos activa
   - Middleware para verificar oposición seleccionada

3. **Frontend**:
   - Modal de selección inicial de oposición
   - Botón "Cambiar Oposición" en header principal
   - Preview de estadísticas antes de cambio

### 📊 Metadata de Oposiciones
```json
{
  "oposiciones": {
    "seguridad_social": {
      "name": "Administrativo - Seguridad Social",
      "description": "Oposiciones para Administrativo del Estado - Seguridad Social",
      "icon": "🏛️",
      "color": "#0f4c75",
      "created_at": "2025-09-01",
      "question_count": 850
    },
    "policia_nacional": {
      "name": "Policía Nacional",
      "description": "Oposiciones a Policía Nacional - Escala Básica",
      "icon": "👮",
      "color": "#1a365d",
      "created_at": "2025-09-02",
      "question_count": 0
    }
  },
  "active": "seguridad_social"
}
```

### 🎯 Experiencia de Usuario Propuesta
1. **Primera Vez**:
   - Modal de bienvenida con selección de tipo de oposición
   - Opciones visuales con iconos y descripciones
   - Botón "Crear Nueva Oposición" para casos personalizados

2. **Pantalla Principal**:
   - Indicador en header: "📚 Seguridad Social" 
   - Botón "Cambiar Oposición" junto al título
   - Estadísticas específicas de la oposición activa

3. **Cambio de Oposición**:
   - Modal con lista de oposiciones disponibles
   - Preview de estadísticas (preguntas, tests realizados)
   - Confirmación antes del cambio
   - Loading durante la migración

### 🔄 Migración de Datos Existentes
```python
# Pseudocódigo para migración automática
def migrate_existing_data():
    if os.path.exists('data/tests_stats.db'):
        # Renombrar base actual a seguridad_social.db
        os.rename('data/tests_stats.db', 'data/seguridad_social.db')
        
        # Crear metadata inicial
        create_metadata_file({
            "active": "seguridad_social",
            "oposiciones": {
                "seguridad_social": {
                    "name": "Administrativo - Seguridad Social",
                    "migrated_from": "tests_stats.db"
                }
            }
        })
```

## Prioridad de Implementación Actualizada

1. **🏛️ Multi-Database System** - Funcionalidad arquitectural fundamental
2. **🗑️ Individual Question Deletion** - Most requested management feature  
3. **📱 Mobile Swipe Navigation** - Enhances mobile UX significantly
4. **📚 Documentation Updates** - Important for maintainability
5. **Advanced Admin Features** - Nice-to-have improvements
6. **Performance Optimizations** - Only needed for large-scale usage