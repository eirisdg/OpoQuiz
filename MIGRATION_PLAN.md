# 🚀 Plan de Migración: Sistema de Preguntas Dinámicas

## 📋 Resumen del Cambio

**ANTES**: Tests JSON estáticos con preguntas fijas
**DESPUÉS**: Banco de preguntas + Generación dinámica con 3 modos

## 🎯 Nuevas Funcionalidades

### 🔄 Sistema de Preguntas
- **Archivos JSON**: Ahora son bancos de preguntas, no tests completos  
- **Carga dinámica**: Las preguntas se cargan en base de datos al iniciar
- **Tracking de uso**: Sistema anti-repetición basado en uso por usuario
- **Generación bajo demanda**: Tests creados dinámicamente según criterios

### 🎮 Nuevos Modos de Test
1. **🎲 Test Aleatorio**
   - Preguntas completamente aleatorias de todos los bancos
   - Configurable: 10-50 preguntas
   - Anti-repetición inteligente

2. **📂 Test por Categoría** 
   - Multi-selección de categorías con checkboxes
   - Basado en keywords y categorías de preguntas
   - Interface moderna con filtros visuales

3. **⭐ Test por Dificultad**
   - Dropdown: Easy, Medium, Hard, Mixed  
   - Preguntas filtradas por nivel
   - Balanceado automáticamente

### 📊 Algoritmo Anti-Repetición
```python
# Prioridad de selección de preguntas:
1. Menos veces usada por el usuario (times_used ASC)
2. Usada hace más tiempo (last_used ASC) 
3. Factor aleatorio para variedad
4. Respeta filtros de categoría/dificultad
```

### ⏱️ Cálculo de Duración del Test
- **Duración total**: Suma de `estimated_time_seconds` de cada pregunta seleccionada
- **Redondeado**: A minutos completos para mostrar al usuario
- **Configuración flexible**: Cada pregunta puede tener diferente tiempo estimado

### 🔢 Configuración de Preguntas por Test
- **Input dinámico**: Solicitar número de preguntas antes de generar test
- **Por defecto**: 50 preguntas si no se especifica
- **Límites**: Mínimo 5, máximo basado en preguntas disponibles
- **Validación**: No puede exceder total de preguntas en filtros aplicados

## 🗄️ Cambios en Base de Datos

### Nuevas Tablas (8 tablas completas)
- `questions`: Banco central de preguntas (question_id TEXT PRIMARY KEY)
- `question_usage`: Tracking de uso por usuario con anti-repetición
- `dynamic_tests`: Tests generados dinámicamente con metadatos
- `test_sessions`: Sesiones de tests completados
- `user_answers`: Respuestas individuales (question_id TEXT para consistencia)
- `question_banks`: Metadatos de bancos JSON cargados
- `test_stats`: Estadísticas agregadas (compatibilidad legacy)
- `session_progress`: Progreso actual de sesiones activas

### Datos Eliminados
- Tests estáticos previos
- Sesiones de tests antiguos
- Estadísticas de tests fijos

## 📝 Cambios en JSON Schema

### Nuevo Formato: Question Banks
```json
{
  "bank_id": "bank_YYYYMMDD_XXX",
  "title": "Banco de Preguntas - Tema",
  "questions": [
    {
      "id": "q_XXX",
      "question": "Pregunta...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": 0,
      "difficulty": "medium",
      "category": "categoria",
      "keywords": ["palabra1", "palabra2"],
      "estimated_time_seconds": 90
    }
  ]
}
```

### Campos Eliminados
- ❌ `points` (todas las preguntas valen igual)
- ❌ `estimated_duration` en test (ahora por pregunta)
- ❌ Estructura de test completo

### Campos Nuevos
- ✅ `estimated_time_seconds` por pregunta
- ✅ `keywords` array para filtrado avanzado
- ✅ `bank_id` para identificar fuente

## 🔄 Pasos de Migración

### ✅ COMPLETADO
1. **✅ Backup**: Guardado datos actuales (main.py.backup)
2. **✅ Limpiar BD**: Eliminado esquema actual
3. **✅ Actualizar Schema**: Nuevas tablas implementadas
   - `questions`: Banco central de preguntas con anti-repetición
   - `question_usage`: Tracking por usuario con estadísticas
   - `dynamic_tests`: Tests generados dinámicamente
   - `question_banks`: Metadatos de archivos JSON
4. **✅ Convertir JSON**: Archivos adaptados al formato bank_*.json
5. **✅ Cargar Preguntas**: Sistema de carga automática con duplicate checking
6. **✅ Panel Admin**: Sistema de upload de archivos con validación
7. **✅ API Endpoints**: Nuevos endpoints para generación dinámica

### ✅ IMPLEMENTADO COMPLETAMENTE
8. **✅ Sistema Anti-Repetición**: Algoritmo basado en `times_used` y `last_used`
9. **✅ Validación de Duplicados**: Comprobación automática al cargar bancos
10. **✅ Upload Dinámico**: Carga de archivos JSON desde panel admin
11. **✅ Tests Dinámicos**: 3 modos funcionando (random, category, difficulty)
12. **✅ Cálculo de Duración**: Basado en tiempo estimado por pregunta
13. **✅ Interface Simplificada**: Eliminación de botón "Tests Disponibles", navegación optimizada
14. **✅ Integración con Repasar Errores**: Funciona con sistema dinámico
15. **✅ Interfaz de Pregunta Limpia**: Eliminada barra de metadatos (categoría/dificultad) para UI más simple
16. **✅ Sistema End-to-End**: Completo desde generación hasta resultados detallados
17. **✅ Schema Type Consistency**: Corregidas inconsistencias críticas ID (string vs int) en schemas.py  
18. **✅ Database Schema Review**: Documentado esquema completo de 8 tablas con tipos correctos
19. **✅ JSON Schema Updated**: test-schema.json actualizado para reflejar estructura y tipos actuales

## 📚 Documentación Actualizada

- **README.md**: Nuevos modos de test y formato JSON
- **CLAUDE.md**: Arquitectura técnica actualizada
- **TODO.md**: Estado y funcionalidades completadas
- **Nuevo template**: `question-bank-template.json`

## 🎯 Beneficios Esperados

✅ **Flexibilidad**: Tests dinámicos vs estáticos  
✅ **Variedad**: Evita repetición excesiva de preguntas  
✅ **Personalización**: Filtros por categoría y dificultad  
✅ **Escalabilidad**: Fácil añadir nuevas preguntas  
✅ **Inteligencia**: Sistema aprende patrones de uso  
✅ **UX Mejorada**: Interface más rica y configurable
✅ **Navegación Optimizada**: Interface simplificada sin botones innecesarios
✅ **Interface Limpia**: Preguntas sin distracciones de metadatos durante el test
✅ **Sistema Completo**: End-to-end funcional con debugging completo

## ✅ ÚLTIMOS FIXES CRÍTICOS APLICADOS (31/08/2025)

### 🔧 Fix Respuestas Detalladas - COMPLETADO ✅
- **PROBLEMA**: Respuestas detalladas no se mostraban en página de resultados
- **ROOT CAUSE**: Field mismatch entre `question_id` (answers) vs `id` (preguntas dinámicas)
- **SOLUCIÓN APLICADA**: 
  - Implementada búsqueda dual: `question_id` first, `id` fallback
  - Corregida lógica en `main.py:635-637`
  - Testing completo con Playwright verificado ✅
- **RESULTADO**: Respuestas detalladas 100% funcionales con contenido completo

### 🔧 Fixes Anteriores Críticos - COMPLETADOS ✅  
1. **Docker Permissions Fix** - Eliminado `:ro` flag para upload de archivos
2. **Missing Function Fix** - Implementado `generate_dynamic_random_test()`
3. **Type Consistency Fix** - Corregidas conversiones int() en question_id strings
4. **JavaScript Template Fix** - Corregidos quotes en question_id en templates
5. **Admin Panel Enhancement** - Añadidos endpoints para gestión de sesiones completadas

## 🚧 Próximas Mejoras Pendientes

### Funcionalidades Admin
- **Dashboard de estadísticas** por banco de preguntas
- **Gestión avanzada de duplicados** con interface para resolución manual
- **Export/Import masivo** de bancos de preguntas
- **Validación mejorada** con reporting detallado de errores

### Optimizaciones Técnicas  
- **Performance** con cache inteligente de preguntas frecuentes
- **Monitoreo** de uso por banco y pregunta individual
- **Backup automático** del sistema de preguntas
- **Health checks avanzados** para el estado del sistema

### Mejoras de Interfaz
- **Visualizaciones** con gráficos de rendimiento por banco
- **Modo oscuro** para mejor experiencia nocturna
- **Loading states** para operaciones de carga