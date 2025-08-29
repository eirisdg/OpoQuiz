# 📚 Generic Test Generator

Sistema de generación y realización de tests interactivos para cualquier temario educativo.

## 🎯 Descripción

Aplicación web móvil-first que permite realizar tests sobre cualquier temario utilizando un formato JSON estándar. Ideal para preparación de oposiciones, exámenes universitarios, certificaciones profesionales, etc. 

**Características principales:**
- **Interfaz móvil-first simplificada** con navegación optimizada
- **Sistema dinámico de preguntas** con banco de datos centralizado
- **3 modos de test inteligentes**: Aleatorio, por Categoría, por Dificultad
- **Panel de administración** para subir y gestionar bancos de preguntas
- **Anti-repetición inteligente** que evita preguntas recién respondidas
- **Duración calculada** basada en tiempo estimado por pregunta (30-300s)
- **Estadísticas avanzadas** de uso y rendimiento por usuario
- **Despliegue simple** con Docker y carga automática

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

## ✨ Funcionalidades

### 📚 Tests Interactivos
- **Navegación optimizada**: Sin barra superior, botón Inicio en header
- **Selección simplificada**: 3 opciones principales claramente diferenciadas
- **Carga desde JSON**: Tests directamente desde archivos en tests/
- **Interfaz táctil**: Optimizada para smartphones y tablets

### 🎲 Modos de Test Dinámicos
- **🎲 Test Aleatorio**: Preguntas aleatorias de todos los bancos con anti-repetición inteligente
- **📂 Test por Categoría**: Selección múltiple de categorías con filtros avanzados
- **⭐ Test por Dificultad**: Tests filtrados por nivel (Easy, Medium, Hard, Mixed)
- **🔄 Repasar Fallos**: Test con preguntas previamente falladas por el usuario
- **🔧 Panel Admin**: Gestión completa de bancos de preguntas

### 📊 Estadísticas y Seguimiento
- **Resultados detallados**: Puntuación, tiempo, análisis por categorías
- **Respuestas completas**: Ver respuestas incorrectas con explicaciones y fuentes
- **Información de fuente**: Documento, sección, página y referencia legal
- **Tests de repaso**: Genera automáticamente tests con preguntas falladas
- **Histórico completo**: Todas las sesiones guardadas automáticamente
- **Análisis de rendimiento**: Identifica áreas de mejora

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

### Página Principal
- Dashboard con estadísticas generales
- Lista de tests disponibles
- Opción para generar tests aleatorios
- Histórico de sesiones recientes

### Realizando un Test
1. Seleccionar test desde la página principal
2. Navegar pregunta por pregunta
3. Seleccionar respuestas sin prisa
4. Finalizar cuando estés listo
5. Revisar resultados detallados

### Tests Aleatorios
- Combina preguntas de múltiples tests
- Configura número de preguntas deseadas
- Filtra por categorías o dificultad
- Genera variedad en tu práctica

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

## 📞 Soporte

Para problemas técnicos o preguntas sobre desarrollo:
- Consulta `CLAUDE.md` para guía técnica detallada
- Revisa `TODO.md` para el estado actual del proyecto
- Los logs están disponibles con: `docker compose logs -f`

---

**🎯 Este generador de tests es completamente genérico y puede utilizarse para cualquier temario de oposiciones o materia de estudio. Simplemente añade tus tests en formato JSON y el sistema estará listo para usar.**