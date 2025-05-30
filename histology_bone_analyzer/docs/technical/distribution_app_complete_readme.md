# 🦴 Distribution App Complete v2.0 - Sistema de Distribución de Osteonas

## Parte del Proyecto Phygital Human Bone 3.0 - Sistema Havers Analysis

### 📋 Descripción General

La **Distribution App Complete v2.0** es una herramienta para el análisis, simulación y generación paramétrica de microestructuras óseas del fémur humano. Esta aplicación incorpora simulación de condiciones patológicas, análisis biomecánico y capacidades de exportación para modelado 3D.

**Desarrollada como parte del proyecto Phygital Human Bone 3.0 en ELISAVA**, esta aplicación constituye el tercer componente del ecosistema Havers Analysis, diseñada para generar distribuciones biomiméticas que alimenten los procesos de diseño paramétrico.

---

## 🚀 Características Principales

### **Interfaz con 6 Pestañas Implementadas**

#### 🔧 **1. Parámetros Básicos**
- **Configuración del Fémur**:
  - Longitud total (cm) - Variable: `self.femur_length`
  - Valores por defecto: 45.0 cm

- **Proporciones Anatómicas** (porcentajes de longitud):
  - Epífisis Proximal: 15.0% - Variable: `self.epiphysis_proximal_percent`
  - Metáfisis Proximal: 10.0% - Variable: `self.metaphysis_proximal_percent`
  - Diáfisis: 50.0% - Variable: `self.diaphysis_percent`
  - Metáfisis Distal: 10.0% - Variable: `self.metaphysis_distal_percent`
  - Epífisis Distal: 15.0% - Variable: `self.epiphysis_distal_percent`

- **Densidades por Sección** (osteonas/cm²):
  - Epífisis Proximal: 25.0 - Variable: `self.density_epiphysis_proximal`
  - Metáfisis Proximal: 40.0 - Variable: `self.density_metaphysis_proximal`
  - Diáfisis: 60.0 - Variable: `self.density_diaphysis`
  - Metáfisis Distal: 40.0 - Variable: `self.density_metaphysis_distal`
  - Epífisis Distal: 25.0 - Variable: `self.density_epiphysis_distal`

- **Tamaños de Osteonas** (μm):
  - Epífisis Proximal: 220.0 - Variable: `self.osteona_size_epiphysis_proximal`
  - Metáfisis Proximal: 190.0 - Variable: `self.osteona_size_metaphysis_proximal`
  - Diáfisis: 150.0 - Variable: `self.osteona_size_diaphysis`
  - Metáfisis Distal: 190.0 - Variable: `self.osteona_size_metaphysis_distal`
  - Epífisis Distal: 220.0 - Variable: `self.osteona_size_epiphysis_distal`

- **Factores de Variabilidad** (0.0-1.0):
  - Epífisis Proximal: 0.7 - Variable: `self.variability_epiphysis_proximal`
  - Metáfisis Proximal: 0.5 - Variable: `self.variability_metaphysis_proximal`
  - Diáfisis: 0.3 - Variable: `self.variability_diaphysis`
  - Metáfisis Distal: 0.5 - Variable: `self.variability_metaphysis_distal`
  - Epífisis Distal: 0.7 - Variable: `self.variability_epiphysis_distal`

#### ⚙️ **2. Parámetros Avanzados**
- **Orientación Preferencial** (0-360°):
  - Variables por sección: `self.orientation_[sección]`
  - Valores por defecto: 0.0° para todas las secciones

- **Fuerza de Orientación** (0.0-1.0):
  - Variables: `self.orientation_strength_[sección]`
  - Valores por defecto:
    - Epífisis: 0.2
    - Metáfisis: 0.4
    - Diáfisis: 0.8

- **Factores de Clustering** (0.0-1.0):
  - Variables: `self.clustering_factor_[sección]`
  - Valores por defecto:
    - Epífisis: 0.3
    - Metáfisis: 0.2
    - Diáfisis: 0.1

#### 🩺 **3. Simulación**
- **Modos de Simulación**:
  - Normal, Envejecimiento, Patológico
  - Variable: `self.simulation_mode`

- **Factores Configurables**:
  - Factor de Edad: 0.5-2.0 - Variable: `self.age_factor`
  - Factor Patológico: 1.0-2.0 - Variable: `self.pathology_factor`

- **Presets Implementados**:
  - `preset_young_healthy()`: age_factor=0.6, pathology_factor=0.9
  - `preset_adult_normal()`: age_factor=1.0, pathology_factor=1.0
  - `preset_aged()`: age_factor=1.8, pathology_factor=1.2
  - `preset_osteoporosis_early()`: age_factor=1.4, pathology_factor=1.5
  - `preset_osteoporosis_advanced()`: age_factor=2.0, pathology_factor=1.8

#### 📊 **4. Visualización**
- **4 Gráficos Simultáneos**:
  - `plot_femur_profile()`: Perfil anatómico con secciones coloreadas
  - `plot_osteona_distribution()`: Scatter plot diferenciando clustering
  - `plot_orientation_analysis()`: Rosa de vientos polar
  - `plot_size_distribution()`: Histogramas por sección

- **Controles Implementados**:
  - "Actualizar Visualización" - `update_visualization()`
  - "Guardar Imagen" - `save_visualization()`
  - "Vista 3D" - `show_3d_visualization()`
  - "Análisis Estadístico" - `show_statistical_analysis()`

#### 🔬 **5. Análisis**
- **Métricas Implementadas**:
  - `calculate_biomechanical_metrics()`: Porosidad, módulo elástico, resistencia
  - `analyze_distribution_patterns()`: Análisis de clustering y gradientes
  - `compare_with_references()`: Comparación con valores de literatura
  - `generate_analysis_report()`: Reporte completo

#### 📤 **6. Exportación**
- **Formatos Disponibles**:
  - CSV: `export_data("csv")`
  - JSON: `export_data("json")`
  - TXT: `export_report_txt()`

- **Configuración de Exportación**:
  - `self.export_coordinates`: BooleanVar(True)
  - `self.export_orientations`: BooleanVar(True)
  - `self.export_sizes`: BooleanVar(True)
  - `self.export_metadata`: BooleanVar(True)

---

## 🔬 Algoritmos Implementados

### **Generación de Distribución**
```python
def generate_osteona_distribution(self):
    """Genera la distribución de osteonas"""
    for section in self.sections_data['sections']:
        area_section = section['length_cm'] * 3.0  # Ancho asumido 3cm
        num_osteonas = int(area_section * section['density_per_cm2'])
        
        # Sistema de clustering implementado
        if section['clustering'] > 0.3:
            num_clusters = max(1, int(num_osteonas * section['clustering'] * 0.1))
            # Generar centros de cluster y distribución gaussiana
```

### **Algoritmos de Distribución Adaptativos**
```python
def create_osteona(self, section, position_z, is_clustered=False):
    """Crea una osteona individual con algoritmos adaptativos"""
    base_size = section['size_um']
    variability = section['variability']
    
    if variability < 0.2:
        # Distribución uniforme para baja variabilidad
        size = random.uniform(base_size * 0.9, base_size * 1.1)
    elif variability < 0.4:
        # Distribución normal
        size = np.random.normal(base_size, base_size * variability * 0.2)
    elif variability < 0.7:
        # Distribución beta (más realista biológicamente)
        alpha, beta = 2, 2
        size = base_size * (0.5 + 0.5 * np.random.beta(alpha, beta))
    else:
        # Distribución multimodal para alta variabilidad
        if random.random() < 0.7:
            size = np.random.normal(base_size, base_size * 0.15)
        else:
            size = np.random.normal(base_size * 1.5, base_size * 0.3)
```

### **Orientación Von Mises**
```python
# En create_osteona()
if orientation_strength > 0.1:
    # Von Mises distribution para orientación preferencial
    concentration = orientation_strength * 10
    angle = np.random.vonmises(np.radians(base_orientation), concentration)
    angle_degrees = np.degrees(angle) % 360
else:
    # Orientación aleatoria
    angle_degrees = random.uniform(0, 360)
```

---

## 🔧 Instalación y Configuración

### **Dependencias del Código**
```python
# Imports principales del archivo
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os
import json
from PIL import Image, ImageTk
import random
from datetime import datetime
import math
from scipy import stats
import seaborn as sns
```

### **Configuración de Directorios**
```python
def ensure_directories(self):
    """Asegura que existan los directorios necesarios"""
    directories = [
        os.path.join(self.base_dir, "data", "sample_results", "distribution_app"),
        os.path.join(self.base_dir, "docs", "technical")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
```

### **Instalación**
```bash
# 1. Clonar repositorio
git clone https://github.com/joan-bl/Workspace_tfg_2.0.git

# 2. Navegar al directorio
cd Workspace_tfg_2.0/histology_bone_analyzer/apps/3distribution_app/

# 3. Instalar dependencias
pip install tkinter numpy matplotlib pandas pillow scipy seaborn

# 4. Ejecutar aplicación
python distribution_app_complete.py
```

---

## 🚀 Flujo de Trabajo

### **1. Inicialización**
```python
def __init__(self, root):
    # Configuración inicial
    self.femur_length = tk.DoubleVar(value=45.0)
    # ... todas las variables inicializadas con valores por defecto
    
    # Crear interfaz y calcular inicialmente
    self.create_ui()
    self.calculate()
```

### **2. Cálculo Principal**
```python
def calculate(self):
    """Método principal de cálculo"""
    # Calcular longitudes de secciones
    total_length = self.femur_length.get()
    
    # Aplicar factores de simulación
    age_factor = self.age_factor.get()
    pathology_factor = self.pathology_factor.get()
    
    for section in sections:
        if age_factor != 1.0:
            section['density_per_cm2'] *= (2.0 - age_factor)
            section['size_um'] *= age_factor
            section['variability'] = min(1.0, section['variability'] * age_factor)
        
        if pathology_factor != 1.0:
            section['density_per_cm2'] *= (2.0 - pathology_factor * 0.5)
            section['size_um'] *= pathology_factor
            section['variability'] = min(1.0, section['variability'] * pathology_factor)
```

### **3. Actualización de Simulación**
```python
def update_simulation_params(self):
    """Actualiza parámetros según el modo de simulación"""
    mode = self.simulation_mode.get()
    
    if mode == "aging":
        self.age_factor.set(1.5)
        self.pathology_factor.set(1.1)
    elif mode == "pathological":
        self.age_factor.set(1.2)
        self.pathology_factor.set(1.6)
    else:  # normal
        self.age_factor.set(1.0)
        self.pathology_factor.set(1.0)
```

---

## 📊 Análisis Biomecánico Implementado

### **Cálculo de Métricas**
```python
def calculate_biomechanical_metrics(self):
    """Calcula métricas biomecánicas avanzadas"""
    # Densidad volumétrica estimada
    avg_area = np.pi * (section_data['size_um'].mean() / 2000) ** 2  # cm²
    total_area = len(section_data) * avg_area
    section_volume = section_info['length_cm'] * 3.0 * 2.0  # Estimación cilíndrica
    
    porosity = (total_area / section_volume) * 100
    
    # Estimación de propiedades mecánicas usando Gibson-Ashby
    relative_density = 1 - (porosity / 100)
    estimated_modulus = 20000 * (relative_density ** 2.5)  # MPa
    estimated_strength = 137 * (relative_density ** 1.8)  # MPa
```

### **Análisis de Patrones**
```python
def analyze_distribution_patterns(self):
    """Analiza patrones de distribución espacial"""
    clustered_count = len(df[df['is_clustered'] == True])
    total_count = len(df)
    clustering_ratio = clustered_count / total_count
    
    # Análisis de correlaciones
    try:
        from scipy.stats import pearsonr
        size_position_corr, size_p = pearsonr(df['position_z_cm'], df['size_um'])
    except ImportError:
        # Fallback si scipy no disponible
```

---

## 🎨 Visualizaciones Implementadas

### **Rosa de Vientos Polar**
```python
def plot_orientation_analysis(self):
    """Gráfico de análisis de orientación (rosa de vientos)"""
    angles = np.radians(df['angle_degrees'])
    
    # Crear rosa de vientos
    n_bins = 16
    theta_bins = np.linspace(0, 2*np.pi, n_bins+1)
    hist, _ = np.histogram(angles, bins=theta_bins)
    
    # Gráfico polar
    self.ax3.remove()
    self.ax3 = self.figure.add_subplot(2, 2, 3, projection='polar')
    theta_centers = (theta_bins[:-1] + theta_bins[1:]) / 2
    bars = self.ax3.bar(theta_centers, hist, width=2*np.pi/n_bins, alpha=0.7)
```

### **Visualización 3D**
```python
def show_3d_visualization(self):
    """Muestra visualización 3D en ventana separada"""
    fig_3d = plt.figure(figsize=(10, 8))
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    
    # Generar coordenadas aleatorias para visualización 3D
    y_coords = np.random.uniform(-1.5, 1.5, len(df))
    x_coords = np.random.uniform(-1.5, 1.5, len(df))
    
    scatter = ax_3d.scatter(x_coords, y_coords, df['position_z_cm'], 
                          c=df['size_um'], cmap='viridis', 
                          s=df['size_um']/5, alpha=0.6)
```

---

## 📤 Exportación Implementada

### **Exportación CSV/JSON**
```python
def export_data(self, format_type):
    """Método de exportación básico"""
    if format_type == "csv":
        df = pd.DataFrame(self.distribution_data)
        df.to_csv(filename, index=False)
    elif format_type == "json":
        export_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "software": "Femur Osteona Distributor Advanced v2.0",
                "total_osteonas": len(self.distribution_data),
                "femur_length_cm": self.femur_length.get(),
                "simulation_mode": self.simulation_mode.get(),
                "age_factor": self.age_factor.get(),
                "pathology_factor": self.pathology_factor.get()
            },
            "sections_configuration": self.sections_data,
            "osteonas": self.distribution_data
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
```

### **Estructura de Datos Exportados**
```python
# Estructura de osteona individual
osteona = {
    'section_name': section['name'],
    'position_z_cm': position_z,
    'angle_degrees': angle_degrees,
    'size_um': size,
    'is_clustered': is_clustered,
    'cluster_id': random.randint(1, 10) if is_clustered else None
}
```

---

## ⚙️ Configuración de Estilo

### **Tema Visual Corporativo**
```python
def configure_style(self):
    """Configuración de estilo mejorada"""
    style = ttk.Style()
    style.theme_use("clam")
    
    # Colores corporativos del proyecto
    style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 10, "bold"))
    style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#BD0000")
    style.configure("Section.TLabel", font=("Arial", 11, "bold"), foreground="#3366cc")
```

---

## 🔄 Integración con Ecosistema

### **Preparación para Grasshopper**
- Exportación CSV con coordenadas, orientaciones y tamaños
- Formato compatible con componente "Read File"
- Metadatos incluidos para trazabilidad

### **Compatibilidad de Datos**
- Estructura de datos consistente con otras apps del ecosistema
- Timestamps para correlación temporal
- Configuración exportada para reproducibilidad

---

## 🚧 Limitaciones

### **Limitaciones Técnicas**
- Simulación 2D (exportable a 3D)
- Ancho del fémur asumido (3 cm)
- Estimaciones biomecánicas basadas en fórmulas empíricas

### **Consideraciones de Uso**
- Resultados para investigación, no diagnóstico clínico
- Validación experimental requerida para parámetros específicos
- Variabilidad individual limitada a factores implementados

---

## 👥 Desarrollo

### **Equipo Principal**
- **Joan Blanch Jiménez**: Desarrollo principal de la aplicación
- **Dr. Juan Crespo Santiago**: Dirección científica
- **Marco Gesualdo**: Co-tutoría

### **Institución**
- **ELISAVA** - Escuela Universitaria de Diseño e Ingeniería de Barcelona
- **Proyecto**: Phygital Human Bone 3.0

---

## 🔗 Enlaces

- **Repositorio**: [https://github.com/joan-bl/Workspace_tfg_2.0](https://github.com/joan-bl/Workspace_tfg_2.0)
- **Directorio**: `/histology_bone_analyzer/apps/3distribution_app/`

---

## 📄 Licencia

MIT License - Ver archivo LICENSE en el repositorio principal.

---

*Distribution App Complete v2.0* - Generación paramétrica de distribuciones de osteonas

*Desarrollado como parte del proyecto Phygital Human Bone 3.0*

*Última actualización: Enero 2025*