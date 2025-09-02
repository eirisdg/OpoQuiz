# 📚 Generic Test Generator

**Sistema completo de tests interactivos móvil-first para cualquier temario educativo**

## 🎯 Descripción

Aplicación web moderna y completamente funcional que permite realizar tests educativos sobre cualquier temario usando bancos de preguntas en formato JSON. Optimizada para dispositivos móviles con una experiencia de usuario pulida y profesional.

**✨ Características Principales:**
- **🔥 Sistema 100% Funcional** - Listo para producción con todas las características implementadas
- **📱 Interfaz Móvil-First Optimizada** - Navegación responsiva con botones fijos en móvil
- **🏦 Sistema Dinámico de Bancos** - Gestión centralizada de preguntas con carga automática
- **🎲 4 Modos de Test Inteligentes** - Aleatorio, Categoría, Dificultad, Repaso de Errores
- **⚡ Panel de Administración** - Subir y gestionar bancos de preguntas vía web
- **🧠 Anti-repetición Inteligente** - Algoritmo que evita preguntas recién contestadas
- **📊 Estadísticas Completas** - Análisis detallado de rendimiento y progreso
- **🚀 Despliegue Instantáneo** - Docker containerizado, listo en un comando

## 🚀 Inicio Rápido

### Requisitos
- Docker y Docker Compose instalados

### Instalación
1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd test-generator
   ```

2. **Añadir bancos de preguntas JSON**
   - Coloca archivos JSON en el directorio `tests/` con formato `bank_YYYYMMDD_XXX.json`
   - Usa `question-bank-template.json` como referencia
   - Sigue el formato del `test-schema.json` (actualizado para bancos)
   - Alternativamente, usa el **Panel Admin** desde la web

3. **Ejecutar la aplicación**
   ```bash
   docker compose up --build
   ```

4. **Acceder a la aplicación**
   - Abrir http://localhost:8080 en tu navegador
   - La interfaz está optimizada para dispositivos móviles

### Comandos Básicos
```bash
# Iniciar aplicación
docker compose up -d

# Ver logs
docker compose logs -f

# Parar aplicación
docker compose down

# Reiniciar completamente
docker compose down -v && docker compose up --build
```

## ✨ Funcionalidades Completas

### 📱 Experiencia Móvil Optimizada (Últimas Mejoras 2025-09)
- **🔄 Navegación Responsiva**: Botones fijos al fondo en móvil, cards normales en desktop
- **⚖️ Espaciado Dinámico**: Flujo natural sin padding excesivo
- **📋 Modales Mejorados**: Botones apilados correctamente con orden intuitivo
- **🎯 Headers Consistentes**: Diseño unificado entre admin y main panel
- **👀 Footer Visible**: Correcta visualización en todas las resoluciones
- **❌ Botones de Cierre**: Posicionamiento perfecto en esquinas

### 🎲 Sistema de Tests Inteligente
- **🎲 Test Aleatorio**: Preguntas de todos los bancos con anti-repetición avanzada
- **📂 Test por Categoría**: Filtros múltiples con selección intuitiva
- **⭐ Test por Dificultad**: Niveles Easy, Medium, Hard, Mixed configurables
- **🔄 Repaso de Errores**: Regeneración automática con preguntas falladas
- **⚡ Generación Dinámica**: Tests creados al instante según criterios

### 📊 Analytics y Tracking Avanzado
- **📈 Estadísticas Completas**: Dashboard con métricas detalladas
- **🎯 Resultados Detallados**: Análisis por categoría, tiempo, precisión
- **📝 Respuestas Explicadas**: Feedback completo con fuentes y explicaciones
- **📚 Información de Fuente**: Documento, sección, página, referencia legal
- **🔁 Tests de Repaso**: Generación automática basada en historial
- **💾 Persistencia Total**: Todas las sesiones guardadas permanentemente

## 📝 Cómo Crear Bancos de Preguntas

### Archivos de Referencia
La aplicación incluye archivos de referencia para trabajar con bancos de preguntas:

#### 📋 **`question-bank-template.json`** - Plantilla Base
- **Propósito**: Template completo para crear nuevos bancos de preguntas
- **Uso**: `cp question-bank-template.json tests/bank_YYYYMMDD_XXX.json`
- **Contiene**: Ejemplo con estructura optimizada y todas las propiedades
- **Recomendación**: **Usar este como base para todos los bancos nuevos**

#### 📐 **`test-schema.json`** - Especificación Técnica  
- **Propósito**: Documentación técnica del formato JSON de bancos
- **Uso**: Consulta para entender reglas y validaciones
- **Contiene**: Tipos de datos, campos requeridos, patrones de validación
- **Recomendación**: Consultar cuando tengas dudas sobre el formato

#### 🔧 **Panel de Administración Web**
- **URL**: `http://localhost:8080/admin` 
- **Funciones**: Subir archivos, gestionar bancos, ver estadísticas
- **Validación**: Automática al subir archivos JSON
- **Recomendación**: **Método más fácil para usuarios no técnicos**

### Estructura Básica
```json
{
  "bank_id": "bank_20250829_001",
  "title": "Banco de Preguntas - Tu Temario",
  "description": "Banco de preguntas sobre tu temario específico",
  "questions": [
    {
      "id": "q_001",
      "question": "¿Tu pregunta aquí?",
      "options": [
        "Opción A",
        "Opción B", 
        "Opción C",
        "Opción D"
      ],
      "correct_answer": 0,
      "explanation": "Explicación de por qué es correcta",
      "difficulty": "medium",
      "category": "tu_categoria",
      "keywords": ["palabra1", "palabra2"],
      "estimated_time_seconds": 90,
      "source_info": {
        "document": "Manual_Temario.pdf",
        "section": "Capítulo 1",
        "page": 15,
        "legal_reference": "Artículo 1.1"
      }
    }
  ]
}
```

### Pasos para Añadir Tests

#### Método Recomendado (usando template)
```bash
# 1. Copiar el template base
cp test-template.json tests/test_20250829_003.json

# 2. Editar el archivo copiado
# - Cambiar test_id, title, description
# - Modificar o añadir preguntas
# - Ajustar category, difficulty, etc.

# 3. Reiniciar la aplicación
docker compose down && docker compose up --build

# 4. Verificar en http://localhost:8080
```

#### Validación Automática
- ✅ **Categorías flexibles**: Cualquier string es válido
- ✅ **Formatos múltiples**: El sistema normaliza diferentes estructuras
- ✅ **Campos opcionales**: Los campos faltantes se completan automáticamente
- ✅ **Carga automática**: Los tests se cargan desde `tests/*.json` al iniciar

## 🌟 Uso de la Aplicación

### 🏠 Página Principal
- **📊 Dashboard Inteligente**: Estadísticas en tiempo real de progreso
- **🎯 4 Modos de Test**: Selección clara con iconos identificativos
- **📈 Métricas Clave**: Preguntas disponibles, tests completados, puntuación media
- **📚 Historial Reciente**: Últimas sesiones con opción de repaso de errores

### 🎮 Realizando Tests
1. **🔧 Configuración**: Selecciona modo y parámetros (número de preguntas, filtros)
2. **📱 Navegación Intuitiva**: Una pregunta por pantalla con progreso visual
3. **✅ Selección de Respuestas**: Interface táctil optimizada para móvil
4. **⏱️ Sin Presión de Tiempo**: Responde a tu ritmo, autosave automático
5. **📊 Resultados Completos**: Análisis detallado con explicaciones y fuentes

### 🎲 Modos de Test Avanzados
- **🎲 Aleatorio**: Mezclado inteligente con anti-repetición por uso
- **📂 Por Categoría**: Filtrado múltiple con selección de checkbox
- **⭐ Por Dificultad**: Tests específicos por nivel de complejidad  
- **🔄 Repaso Errores**: Enfoque dirigido en preguntas previamente falladas

## 📊 Casos de Uso

**Preparación de Oposiciones**
- Administrativo del Estado, Policía, Educación, Sanidad

**Exámenes Académicos**  
- Universidad, Formación Profesional, Certificaciones

**Formación Corporativa**
- Compliance, Seguridad laboral, Procesos internos

## ⚙️ Configuración

### Variables de Entorno (Opcional)
```env
PORT=8080                           # Puerto de la aplicación
DEFAULT_PASSING_GRADE=70           # Nota mínima para aprobar
RANDOM_TEST_DEFAULT_QUESTIONS=10   # Preguntas por defecto en tests aleatorios
```

### Personalización
- **Archivos de referencia**: `test-template.json` y `test-schema.json`
- **Documentación técnica**: Ver `CLAUDE.md` para desarrollo
- **Seguimiento de tareas**: Ver `TODO.md` para el estado del proyecto

## 🎯 Estado del Proyecto

### ✅ **Sistema 100% Funcional y Optimizado**
- **Núcleo**: Todas las funcionalidades principales implementadas y probadas
- **Mobile UX**: Interfaz móvil completamente optimizada (Septiembre 2025)
- **Database**: Sistema de persistencia estable con anti-repetición inteligente
- **API**: Endpoints REST completos y documentados
- **Testing**: Verificación manual completa de todos los flujos críticos

### 🚀 **Próximas Mejoras Prioritarias**
1. **🗑️ Eliminación Individual de Preguntas** - Interface admin para borrar preguntas específicas
2. **📱 Navegación por Gestos** - Swipe izquierda/derecha para móvil
3. **📚 Documentación API** - Generación automática y guías de usuario

### 📊 **Arquitectura Técnica**
- **Backend**: FastAPI + SQLite async + Pydantic schemas
- **Frontend**: HTML5 + CSS3 responsive + JavaScript vanilla
- **Database**: 8 tablas optimizadas con indexing y relaciones
- **Deploy**: Docker containerizado con compose
- **Testing**: Manual verification con Playwright MCP

## 📞 Soporte y Desarrollo

### 📖 Documentación Técnica
- **`CLAUDE.md`**: Guía completa de arquitectura y desarrollo
- **`TODO.md`**: Estado actual y roadmap detallado
- **Logs**: `docker compose logs -f test-generator`
- **Health Check**: `http://localhost:8080/health`

### 🛠️ Para Desarrolladores
```bash
# Desarrollo con hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Acceso a la base de datos
sqlite3 data/tests_stats.db

# API Documentation
http://localhost:8080/docs
```

---

**🎯 Sistema de Test Generator completamente funcional y listo para producción. Perfecto para cualquier temario educativo - simplemente añade tus bancos de preguntas JSON y ¡comienza a estudiar!**