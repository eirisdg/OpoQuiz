# 📚 Generic Test Generator

Sistema de generación y realización de tests interactivos para cualquier temario de oposiciones.

## 🎯 Descripción

Aplicación web móvil-first que permite realizar tests sobre cualquier temario utilizando un formato JSON estándar. Ideal para preparación de oposiciones, exámenes universitarios, certificaciones profesionales, etc. Los tests se almacenan como archivos JSON y las estadísticas se guardan en SQLite local.

## 🎯 Objetivos

- **Interfaz HTML interactiva** móvil-first para realizar tests
- **Tests basados en JSON** con formato estándar flexible
- **Navegación sin validación inmediata** - evaluación solo al finalizar
- **Tests aleatorios** combinando preguntas de múltiples tests
- **Histórico de resultados** persistente en SQLite
- **Despliegue containerizado** ultra-simple con Docker
- **Template JSON genérico** para cualquier temario

## ✨ Características Principales

### 🎲 Gestión de Tests
- **Formato estándar**: JSON estructurado compatible con cualquier temario
- **Tests aleatorios**: Combina preguntas de múltiples tests existentes
- **Tipos de pregunta**: Opción múltiple (4 opciones, 1 correcta)
- **Cantidad flexible**: 5-50 preguntas por test
- **Fácil importación**: Simplemente añade archivos JSON al directorio tests/

### 📱 Interfaz Móvil-First
- **Diseño responsive**: Optimizado primero para móviles, luego escritorio
- **Botones táctiles**: 44px mínimo siguiendo estándares de usabilidad móvil
- **Navegación intuitiva**: Progreso visual, navegación entre preguntas
- **Sin validación inmediata**: Las respuestas se evalúan solo al finalizar
- **Navegación libre**: Permite ir hacia adelante y atrás, cambiar respuestas
- **Resultados detallados**: Puntuación, tiempo, análisis por categorías

### 💾 Almacenamiento y Persistencia
- **Tests como JSON**: Archivos estáticos en directorio `tests/` con ID único
- **Base de datos SQLite**: Integrada para estadísticas y seguimiento de progreso
- **Sesiones persistentes**: Permite continuar tests interrumpidos
- **Estadísticas completas**: Análisis por categoría, dificultad, rendimiento histórico

## 📋 Estructura JSON de Tests (Genérica)

### Campos Principales del Test
```json
{
  "test_id": "test_20250828_001",
  "title": "Examen de Derecho Administrativo - Tema 1",
  "description": "Test sobre conceptos básicos del derecho administrativo",
  "category": "derecho_administrativo",
  "difficulty": "medium",
  "estimated_duration": 15,
  "passing_grade": 70,
  "questions": [...],
  "scoring": {
    "total_points": 10,
    "difficulty_weights": { "easy": 1, "medium": 1, "hard": 2 }
  },
  "metadata": {
    "generated_by": "Claude Code",
    "source_documents": ["BOE-2023-001.pdf", "Manual_Tema1.pdf"],
    "legal_system": "Spanish Administrative Law",
    "subject": "Oposiciones Administrativo del Estado"
  }
}
```

### Estructura de Pregunta Individual
```json
{
  "id": 1,
  "question": "¿Cuál es el principio fundamental que rige...?",
  "options": [
    "Principio de legalidad",
    "Principio de oportunidad", 
    "Principio de discrecionalidad",
    "Principio de jerarquía"
  ],
  "correct_answer": 0,
  "explanation": "El principio de legalidad establece que...",
  "source_info": {
    "document": "Manual_Derecho_Administrativo.pdf",
    "section": "Tema 1: Principios Generales",
    "page": 15,
    "legal_reference": "Artículo 9.3 CE"
  },
  "difficulty": "medium",
  "category": "principios_generales",
  "keywords": ["legalidad", "principios", "derecho administrativo"],
  "points": 1
}
```

## 🏗️ Arquitectura del Sistema

### Componente Único Docker - Test Generator Service
- **Tecnología**: Python + FastAPI (máxima simplicidad)
- **Puerto**: 8080
- **Funciones integradas**:
  - Servir interfaz web HTML/CSS/JS responsive
  - API REST para gestión de tests y sesiones
  - Navegación de preguntas sin validación inmediata
  - Generación de tests aleatorios
  - SQLite integrado para estadísticas
  - Gestión de sesiones de usuario persistentes

### 📁 Estructura de Almacenamiento
```
test-generator/
├── app/                    # Aplicación FastAPI
│   ├── main.py            # Punto de entrada con todas las rutas
│   ├── database.py        # Gestión SQLite con aiosqlite
│   ├── schemas.py         # Modelos Pydantic genéricos
│   └── config.py          # Configuración de la aplicación
├── templates/             # Templates HTML móvil-first
│   ├── base.html         # Template base responsive
│   ├── index.html        # Página principal con estadísticas
│   ├── test.html         # Interfaz de realización de tests
│   └── results.html      # Página de resultados detallados
├── tests/                 # Tests JSON (montado como volumen)
├── data/                  # SQLite database (volumen persistente)
├── docker-compose.yml     # Orquestación ultra-simple
├── Dockerfile            # Imagen Python ligera
├── requirements.txt      # Dependencias mínimas
├── test-template.json    # Template genérico de referencia
└── test-schema.json      # Schema de validación
```

### 🔄 Flujo de Funcionamiento

#### Añadir Tests
1. **Crear archivo JSON** siguiendo el template genérico
2. **Guardar en directorio** `tests/`
3. **Sistema detecta** automáticamente nuevos tests

#### Realización de Tests
1. **Usuario accede** a interfaz móvil (puerto 8080)
2. **Página principal** muestra estadísticas y tests disponibles
3. **Selección de test** específico o generación aleatoria
4. **Navegación libre** entre preguntas sin validación inmediata
5. **Finalización voluntaria** y evaluación completa
6. **Resultados detallados** con análisis por categorías
7. **Almacenamiento** en SQLite para histórico

## 📱 Características Móvil-First

### Diseño Responsivo
- **Breakpoints**: 768px (móvil-tablet), 1024px (tablet-escritorio)
- **Touch targets**: Mínimo 44px para botones y elementos interactivos
- **Navegación**: Botones grandes y fáciles de pulsar
- **Tipografía**: Tamaños escalables y legibles en pantallas pequeñas

### Optimizaciones Táctiles
- **Feedback visual** en toques y selecciones
- **Scrolling suave** entre secciones
- **Carga progresiva** para conexiones móviles lentas
- **Estado offline** básico para continuar tests iniciados

## 🔧 API Endpoints Principales

### Tests y Sesiones
```
GET  /                          # Página principal con estadísticas
GET  /test/{session_id}         # Interfaz de realización de test
GET  /results/{session_id}      # Resultados detallados

GET  /api/tests                 # Listar tests disponibles
POST /api/sessions              # Iniciar nueva sesión (normal o aleatoria)
GET  /api/sessions/{id}/question/{index}  # Obtener pregunta específica
POST /api/sessions/{id}/answers # Guardar respuesta
POST /api/sessions/{id}/complete # Finalizar test
GET  /api/stats                 # Estadísticas generales
```

### Tests Aleatorios
```json
POST /api/sessions
{
  "test_id": "random",
  "is_random_test": true,
  "random_config": {
    "num_questions": 15,
    "categories": ["derecho_administrativo", "derecho_civil"],
    "difficulties": ["medium", "hard"],
    "exclude_test_ids": ["test_already_taken"],
    "allow_repeats": false
  }
}
```

## 🐳 Comandos de Docker

```bash
# Construir y arrancar el servicio
docker compose up --build -d

# Ver logs en tiempo real
docker compose logs -f test-generator

# Acceso a la aplicación
curl http://localhost:8080                    # Página principal
curl http://localhost:8080/docs              # Documentación API automática
curl http://localhost:8080/api/tests         # Lista de tests via API
curl http://localhost:8080/api/stats         # Estadísticas generales

# Gestión del contenedor
docker compose ps                            # Estado
docker compose down                          # Parar
docker compose down -v && docker compose up --build  # Rebuild completo
```

## ⚙️ Variables de Entorno

```env
# Aplicación
APP_NAME="Generic Test Generator"
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Rutas (montadas como volúmenes Docker)
TESTS_DIR=/app/tests
DATABASE_PATH=/app/data/tests.db
TEMPLATES_DIR=/app/templates

# Configuración de tests
DEFAULT_PASSING_GRADE=70
SESSION_TIMEOUT=3600
RANDOM_TEST_DEFAULT_QUESTIONS=10
RANDOM_TEST_MAX_QUESTIONS=20

# UI móvil-first
MOBILE_BREAKPOINT=768
TOUCH_BUTTON_MIN_SIZE=44
DEFAULT_THEME=generic

# Seguridad y rendimiento
CORS_ENABLED=false
MAX_CONCURRENT_SESSIONS=50
```

## 📊 Casos de Uso Genéricos

### Preparación de Oposiciones
- **Administrativo del Estado**: Tests de derecho administrativo, constitucional
- **Cuerpo Nacional de Policía**: Legislación, procedimientos policiales
- **Educación**: Pedagogía, normativa educativa, temarios específicos
- **Sanidad**: Legislación sanitaria, protocolos clínicos

### Exámenes Académicos
- **Universidad**: Tests de repaso por asignaturas
- **Formación Profesional**: Tests de módulos específicos
- **Certificaciones**: Preparación para certificaciones profesionales

### Formación Corporativa
- **Compliance**: Tests de cumplimiento normativo
- **Seguridad laboral**: Protocolos y procedimientos
- **Procesos internos**: Formación en metodologías empresariales

## 🔧 Desarrollo y Personalización

### Creación de Tests
1. Seguir el **template JSON genérico** para máxima compatibilidad
2. Validar con **test-schema.json** antes de usar
3. Guardar en directorio `tests/` con nomenclatura estándar
4. El sistema detectará automáticamente los nuevos tests

### Personalización Visual
- **CSS responsivo** en `templates/base.html`
- **Variables CSS** para cambiar colores y tipografías fácilmente
- **Themes configurables** via variables de entorno
- **Logos y branding** intercambiables

### Extensibilidad
- **API REST completa** para integraciones externas
- **Base de datos SQLite** fácilmente migrable
- **Formato JSON** compatible con otras herramientas
- **Docker** para despliegue en cualquier entorno

## 🚀 Estado del Desarrollo

### ✅ Completado
- [x] Estructura base de la aplicación FastAPI
- [x] Base de datos SQLite con gestión completa de sesiones
- [x] Templates HTML móvil-first responsivos
- [x] Sistema de navegación sin validación inmediata  
- [x] Generación de tests aleatorios
- [x] API REST completa
- [x] Template y schema JSON genéricos
- [x] Dockerización ultra-simple
- [x] Documentación actualizada para uso genérico

### 📈 Próximas Mejoras
- [ ] Panel de administración web para gestión de tests
- [ ] Sistema de backup automático
- [ ] Múltiples temas visuales personalizables  
- [ ] Exportación de resultados (PDF, CSV)
- [ ] Estadísticas avanzadas con gráficos
- [ ] Modo offline básico para móviles

## 📚 Archivos de Referencia

### Templates y Esquemas
- **`test-template.json`**: ⭐ Template genérico completo para cualquier temario
- **`test-schema.json`**: Schema de validación JSON universal
- **`tests/`**: Directorio para archivos JSON de tests
- **`storage-structure.md`**: Documentación completa de almacenamiento

### Código Fuente Principal
- **`app/main.py`**: Aplicación FastAPI completa con todas las rutas
- **`app/database.py`**: Gestión SQLite con soporte completo para sesiones
- **`app/schemas.py`**: Modelos Pydantic genéricos y flexibles
- **`templates/base.html`**: Template HTML base móvil-first
- **`docker-compose.yml`**: Orquestación ultra-simple de un solo servicio

---

**🎯 Este generador de tests es completamente genérico y puede utilizarse para cualquier temario de oposiciones o materia de estudio. Simplemente añade tus tests en formato JSON y el sistema estará listo para usar.**