# 🔬 Detection App v2.0 - Sistema de Detección de Canales de Havers

## Parte del Proyecto Phygital Human Bone 3.0 - Sistema Havers Analysis

### 📋 Descripción General

**Detection App v2.0** es una aplicación Python diseñada para la detección, medición y análisis automatizado de canales de Havers en imágenes histológicas de hueso mediante visión computacional e inteligencia artificial. Como componente fundamental del proyecto **Phygital Human Bone 3.0**, esta herramienta automatiza el proceso tradicional de identificación de microestructuras óseas.

**Desarrollada en ELISAVA como parte del ecosistema Havers Analysis**, esta aplicación constituye el primer componente de la cadena de análisis, proporcionando detecciones que alimentan las aplicaciones Breaking App y Distribution App.

---

## ✨ Características Principales

### 🤖 **Modelo de Inteligencia Artificial**
- **Modelo YOLO cargado** desde rutas configurables
- **Umbral de confianza**: 0.4 (configurable)
- **Detección automática de GPU** con fallback a CPU
- **Procesamiento por lotes** de segmentos de imagen

### 🖼️ **Procesamiento de Imágenes**
- **Soporte para múltiples formatos**: JPG, JPEG, PNG, TIFF, TIF, BMP
- **Redimensionamiento automático** cuando la imagen excede 178,956,970 píxeles
- **Segmentación en 150 fragmentos** organizados en matriz 15×10
- **Interpolación LANCZOS4** para redimensionamiento de alta calidad
- **Validación automática** de formato y legibilidad de imágenes

### 📊 **Análisis Cuantitativo**
- **Métricas por canal detectado**:
  - Coordenadas exactas (X, Y) en imagen original
  - Área elíptica calculada (π × semi-eje mayor × semi-eje menor)
  - Categorización por tamaño (Pequeño, Medio, Grande)
  - ID de segmento de origen
  - Timestamp de detección

- **Estadísticas calculadas**:
  - Media, mediana, desviación estándar de áreas
  - Valores mínimo y máximo
  - Conteo total de detecciones
  - Distribución por categorías de tamaño
  - Distancia media entre centros (vectorizada)

### 🎨 **Visualizaciones**
- **Mapa de coordenadas**: Scatter plot con codificación por colores según área
- **Mapa de calor**: Histograma 2D con 100 bins de resolución
- **Superposición sobre imagen original** con transparencia
- **Barras de color** informativas con escalas
- **Exportación en PNG** a 600 DPI

### 💾 **Gestión de Datos**
- **Exportación Excel multi-hoja**:
  - Hoja principal con datos ordenados por área
  - Hoja de estadísticas automática
  - Metadatos de procesamiento
  - Categorización automática por tamaño

- **Sistema de backup**: Copia automática en directorio técnico
- **Logging detallado**: Archivo de log con información de procesamiento

### 🖥️ **Interfaz de Usuario**
- **Diseño de 3 pestañas**:
  - 📊 **Resumen**: Métricas principales en tarjetas visuales
  - 📈 **Estadísticas**: Reporte detallado con análisis completo
  - 🛠️ **Acciones**: Botones de acceso rápido a resultados

- **Barras de progreso** en tiempo real durante procesamiento
- **Tema visual**: Negro (#000000), Rojo (#BD0000), Blanco
- **Ventana redimensionable** con tamaño mínimo 700×500
- **Centrado automático** en pantalla

---

## 🏗️ Arquitectura del Sistema

La aplicación está estructurada en clases modulares:

```
Detection App v2.0
├── DetectionApp              # Clase principal de la aplicación
├── YOLOModelManager         # Gestión del modelo YOLO
├── ImageProcessor           # Procesamiento de imágenes
├── DataAnalyzer            # Análisis estadístico y visualizaciones
├── DataManager             # Gestión de datos y exportación
├── UIManager               # Interfaz de usuario
├── Config                  # Configuración centralizada
├── DirectoryManager        # Gestión de directorios
└── MemoryManager          # Optimización de memoria
```

### **Configuración Centralizada**
```python
@dataclass
class Config:
    CONFIDENCE_THRESHOLD: float = 0.4
    MAX_PIXELS: int = 178956970
    NUM_SEGMENTS: int = 150
    SEGMENT_COLS: int = 15
    DPI: int = 600
    HEATMAP_BINS: int = 100
    FIGURE_SIZE: Tuple[int, int] = (16, 16)
```

---

## 🔧 Tecnologías y Dependencias

### **Dependencias Requeridas**
```python
# Según el código fuente
ultralytics          # Framework YOLO
torch               # Backend PyTorch
torchvision         # Transformaciones de imágenes
opencv-python       # Procesamiento de imágenes
numpy              # Operaciones numéricas
pandas             # Análisis de datos
matplotlib         # Visualizaciones
tkinter            # Interfaz gráfica (incluido en Python)
Pillow             # Manipulación de imágenes
pathlib            # Manejo de rutas
logging            # Sistema de logging
```

### **Estructura de Directorios**
```
histology_bone_analyzer/
├── data/sample_results/detection_app/
│   ├── images_segmented/          # Segmentos temporales
│   ├── segmented_results/         # Resultados anotados
│   ├── results/                   # Visualizaciones
│   ├── excel/                     # Datos Excel
│   └── detection_app.log          # Log de operaciones
├── data/sample_images/            # Imágenes de muestra
├── docs/technical/                # Documentación y backups
├── models/                        # Modelo YOLO (weights.pt)
└── apps/1detection_app/
    └── improved_detection_app.py  # Aplicación principal
```

---

## 🚀 Instalación y Ejecución

### **Instalación**
```bash
# 1. Clonar repositorio
git clone https://github.com/joan-bl/Workspace_tfg_2.0.git

# 2. Navegar al directorio
cd Workspace_tfg_2.0/histology_bone_analyzer/apps/1detection_app/

# 3. Instalar dependencias
pip install ultralytics torch torchvision opencv-python numpy pandas matplotlib pillow

# 4. Verificar modelo YOLO
# El modelo debe estar en: ../../../models/weights.pt
# O en: ../../../workspace/runs/detect/train/weights/weights.pt
```

### **Ejecución**
```bash
python improved_detection_app.py
```

### **Verificación del Sistema**
Al iniciar, la aplicación muestra:
- Estado del modelo YOLO cargado
- Uso actual de memoria del sistema (si psutil disponible)
- Disponibilidad de aceleración GPU
- Configuración de parámetros activos

---

## 🚀 Flujo de Trabajo

### **1. Inicialización**
- Verificación y creación de directorios necesarios
- Carga del modelo YOLO desde rutas configuradas
- Configuración de la interfaz de usuario

### **2. Procesamiento de Imagen**
1. **Selección**: Diálogo para elegir imagen histológica
2. **Validación**: Verificación de formato y legibilidad
3. **Redimensionamiento**: Si excede MAX_PIXELS (178,956,970)
4. **Segmentación**: División en 150 fragmentos (15×10)
5. **Detección**: Procesamiento secuencial con YOLO
6. **Análisis**: Cálculo de métricas y estadísticas

### **3. Generación de Resultados**
- Cálculo de coordenadas globales y áreas
- Categorización automática por tamaños
- Generación de visualizaciones
- Exportación a Excel multi-hoja
- Creación de backup automático

---

## 📊 Funcionalidades Implementadas

### **Procesamiento de Imágenes**
```python
# Funciones principales del ImageProcessor
- validate_image()           # Validación de formato
- resize_image_if_needed()   # Redimensionamiento automático
- divide_image_optimized()   # Segmentación en fragmentos
```

### **Análisis de Datos**
```python
# Funciones del DataAnalyzer
- calculate_distance_matrix_optimized()  # Distancias entre centros
- generate_visualization_optimized()     # Mapas y gráficos
- _calculate_statistics()               # Estadísticas descriptivas
```

### **Gestión del Modelo YOLO**
```python
# Funciones del YOLOModelManager
- find_model_path()                    # Búsqueda de modelo
- load_model()                         # Carga con configuración
- process_all_segments_sequentially()  # Procesamiento garantizado
```

---

## 🎯 Características Técnicas

### **Gestión de Memoria**
- Limpieza automática de memoria cada 10 segmentos
- Liberación proactiva de recursos GPU/CPU
- Garbage collection automático

### **Categorización de Canales**
Según el código, la categorización se basa en el área:
- Implementada en `pd.cut()` con 3 categorías: Pequeño, Medio, Grande
- Labels automáticos aplicados a los datos

### **Exportación Excel**
Estructura multi-hoja implementada:
- **Detecciones**: Datos principales ordenados por área
- **Estadísticas**: Métricas calculadas automáticamente  
- **Metadatos**: Información de procesamiento y timestamp

### **Sistema de Logging**
- Archivo: `detection_app.log` en directorio de resultados
- Niveles: INFO, WARNING, ERROR
- Formato con timestamp y función de origen

---

## 🔄 Integración con Ecosistema

### **Output para Breaking App**
La aplicación genera archivos Excel compatibles con Breaking App:
- Columnas requeridas: 'Center X', 'Center Y', 'Ellipse Area (pixels^2)'
- Nombres alternativos soportados: 'X', 'Y', 'Area'

### **Metadatos Exportados**
- Timestamp de procesamiento
- Configuración utilizada
- Estadísticas de calidad
- Información de la imagen procesada

---

## ⚙️ Configuración Avanzada

### **Parámetros Modificables**
Los parámetros se pueden ajustar en la clase `Config`:
- `CONFIDENCE_THRESHOLD`: Umbral de confianza YOLO
- `MAX_PIXELS`: Límite para redimensionamiento
- `NUM_SEGMENTS`: Número de segmentos de división
- `DPI`: Calidad de exportación de imágenes

### **Rutas del Modelo**
El sistema busca el modelo YOLO en:
1. `C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg_2.0\histology_bone_analyzer\models\weights.pt`
2. `C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg_2.0\workspace\runs\detect\train\weights\weights.pt`

---

## 📁 Gestión de Archivos

### **Limpieza Automática**
- Los segmentos temporales se limpian antes de cada procesamiento
- Se mantienen solo los resultados finales y visualizaciones

### **Numeración de Resultados**
- Los segmentos de resultado usan numeración con padding de 3 dígitos (001, 002, etc.)
- Garantiza orden correcto en el sistema de archivos

### **Backup Automático**
- Copia de seguridad del Excel principal en directorio técnico
- Nombre: `bounding_box_centers_backup.xlsx`

---

## 🚧 Limitaciones Conocidas

### **Limitaciones Técnicas**
- Requiere modelo YOLO pre-entrenado en ubicaciones específicas
- Procesamiento limitado por memoria disponible del sistema
- Análisis bidimensional únicamente
- Dependiente de calidad de imagen histológica

### **Requisitos de Sistema**
- Python 3.9 o superior (según imports modernos)
- GPU recomendada para procesamiento YOLO
- Memoria suficiente para imágenes grandes
- Espacio de almacenamiento para resultados

---

## 👥 Desarrollo

### **Equipo Principal**
- **Joan Blanch Jiménez**: Desarrollo principal
- **Dr. Juan Crespo Santiago**: Dirección científica  
- **Marco Gesualdo**: Co-tutoría

### **Institución**
- **ELISAVA** - Escuela Universitaria de Diseño e Ingeniería de Barcelona
- **Proyecto**: Phygital Human Bone 3.0

---

## 🔗 Enlaces

- **Repositorio**: [https://github.com/joan-bl/Workspace_tfg_2.0](https://github.com/joan-bl/Workspace_tfg_2.0)
- **Directorio**: `/histology_bone_analyzer/apps/1detection_app/`

---

## 📄 Licencia

MIT License - Ver archivo LICENSE en el repositorio principal.

---

*Detection App v2.0* - Automatización de detección de canales de Havers

*Desarrollado como parte del proyecto Phygital Human Bone 3.0*

*Última actualización: Enero 2025*