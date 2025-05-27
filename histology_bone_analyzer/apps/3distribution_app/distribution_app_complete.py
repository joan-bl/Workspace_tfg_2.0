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

class FemurOsteonaDistributorAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("Femur Osteona Distributor - Advanced v2.0")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Configurar estilo
        self.configure_style()
        
        # Variables básicas (manteniendo compatibilidad)
        self.femur_length = tk.DoubleVar(value=45.0)
        self.epiphysis_proximal_percent = tk.DoubleVar(value=15.0)
        self.metaphysis_proximal_percent = tk.DoubleVar(value=10.0)
        self.diaphysis_percent = tk.DoubleVar(value=50.0)
        self.metaphysis_distal_percent = tk.DoubleVar(value=10.0)
        self.epiphysis_distal_percent = tk.DoubleVar(value=15.0)
        
        # Densidades (osteonas por cm²)
        self.density_epiphysis_proximal = tk.DoubleVar(value=25.0)
        self.density_metaphysis_proximal = tk.DoubleVar(value=40.0)
        self.density_diaphysis = tk.DoubleVar(value=60.0)
        self.density_metaphysis_distal = tk.DoubleVar(value=40.0)
        self.density_epiphysis_distal = tk.DoubleVar(value=25.0)
        
        # Tamaños de osteonas (diámetro en μm)
        self.osteona_size_epiphysis_proximal = tk.DoubleVar(value=220.0)
        self.osteona_size_metaphysis_proximal = tk.DoubleVar(value=190.0)
        self.osteona_size_diaphysis = tk.DoubleVar(value=150.0)
        self.osteona_size_metaphysis_distal = tk.DoubleVar(value=190.0)
        self.osteona_size_epiphysis_distal = tk.DoubleVar(value=220.0)
        
        # Variabilidad (0.0-1.0)
        self.variability_epiphysis_proximal = tk.DoubleVar(value=0.7)
        self.variability_metaphysis_proximal = tk.DoubleVar(value=0.5)
        self.variability_diaphysis = tk.DoubleVar(value=0.3)
        self.variability_metaphysis_distal = tk.DoubleVar(value=0.5)
        self.variability_epiphysis_distal = tk.DoubleVar(value=0.7)
        
        # NUEVAS VARIABLES AVANZADAS
        # Orientación preferencial de osteonas (0-360 grados)
        self.orientation_epiphysis_proximal = tk.DoubleVar(value=0.0)
        self.orientation_metaphysis_proximal = tk.DoubleVar(value=0.0)
        self.orientation_diaphysis = tk.DoubleVar(value=0.0)
        self.orientation_metaphysis_distal = tk.DoubleVar(value=0.0)
        self.orientation_epiphysis_distal = tk.DoubleVar(value=0.0)
        
        # Concentración de dispersión angular (0.0-1.0)
        self.orientation_strength_epiphysis_proximal = tk.DoubleVar(value=0.2)
        self.orientation_strength_metaphysis_proximal = tk.DoubleVar(value=0.4)
        self.orientation_strength_diaphysis = tk.DoubleVar(value=0.8)
        self.orientation_strength_metaphysis_distal = tk.DoubleVar(value=0.4)
        self.orientation_strength_epiphysis_distal = tk.DoubleVar(value=0.2)
        
        # Factores de clustering (tendencia a agruparse)
        self.clustering_factor_epiphysis_proximal = tk.DoubleVar(value=0.3)
        self.clustering_factor_metaphysis_proximal = tk.DoubleVar(value=0.2)
        self.clustering_factor_diaphysis = tk.DoubleVar(value=0.1)
        self.clustering_factor_metaphysis_distal = tk.DoubleVar(value=0.2)
        self.clustering_factor_epiphysis_distal = tk.DoubleVar(value=0.3)
        
        # Variables de simulación avanzada
        self.simulation_mode = tk.StringVar(value="normal")  # normal, pathological, aging
        self.age_factor = tk.DoubleVar(value=1.0)  # 0.5 (joven) a 2.0 (muy viejo)
        self.pathology_factor = tk.DoubleVar(value=1.0)  # Factor de patología ósea
        
        # Datos calculados
        self.sections_data = None
        self.distribution_data = None
        self.analysis_results = None
        
        # Crear la interfaz
        self.create_ui()
        
        # Calcular inicialmente
        self.calculate()
    
    def configure_style(self):
        """Configuración de estilo mejorada"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colores corporativos del proyecto
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#BD0000")
        style.configure("Section.TLabel", font=("Arial", 11, "bold"), foreground="#3366cc")
        
        # Pestañas mejoradas
        style.configure("TNotebook", background="#f0f0f0", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e0e0", padding=[12, 8], font=("Arial", 10))
        style.map("TNotebook.Tab", background=[("selected", "#BD0000"), ("active", "#ffcccc")])
        style.map("TNotebook.Tab", foreground=[("selected", "white")])
    
    def create_ui(self):
        """Interfaz mejorada con más pestañas"""
        # Crear notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestañas principales
        self.tab_basic_params = ttk.Frame(self.notebook)
        self.tab_advanced_params = ttk.Frame(self.notebook)
        self.tab_simulation = ttk.Frame(self.notebook)
        self.tab_visualization = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)
        self.tab_export = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_basic_params, text="Parámetros Básicos")
        self.notebook.add(self.tab_advanced_params, text="Parámetros Avanzados")
        self.notebook.add(self.tab_simulation, text="Simulación")
        self.notebook.add(self.tab_visualization, text="Visualización")
        self.notebook.add(self.tab_analysis, text="Análisis")
        self.notebook.add(self.tab_export, text="Exportación")
        
        # Configurar cada pestaña
        self.setup_basic_params_tab()
        self.setup_advanced_params_tab()
        self.setup_simulation_tab()
        self.setup_visualization_tab()
        self.setup_analysis_tab()
        self.setup_export_tab()
    
    def setup_basic_params_tab(self):
        """Pestaña de parámetros básicos (como la original)"""
        # Marco para entrada de datos
        input_frame = ttk.LabelFrame(self.tab_basic_params, text="Parámetros del Fémur")
        input_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Longitud del fémur
        ttk.Label(input_frame, text="Longitud del Fémur (cm):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.femur_length, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Marco para secciones básicas
        sections_frame = ttk.LabelFrame(self.tab_basic_params, text="Proporciones y Propiedades Básicas")
        sections_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Encabezados
        headers = ["Sección", "% Longitud", "Densidad (ost/cm²)", "Tamaño (μm)", "Variabilidad"]
        for i, header in enumerate(headers):
            ttk.Label(sections_frame, text=header, style="Section.TLabel").grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Secciones con sus variables
        sections = [
            ("Epífisis Proximal", self.epiphysis_proximal_percent, self.density_epiphysis_proximal, 
             self.osteona_size_epiphysis_proximal, self.variability_epiphysis_proximal),
            ("Metáfisis Proximal", self.metaphysis_proximal_percent, self.density_metaphysis_proximal,
             self.osteona_size_metaphysis_proximal, self.variability_metaphysis_proximal),
            ("Diáfisis", self.diaphysis_percent, self.density_diaphysis,
             self.osteona_size_diaphysis, self.variability_diaphysis),
            ("Metáfisis Distal", self.metaphysis_distal_percent, self.density_metaphysis_distal,
             self.osteona_size_metaphysis_distal, self.variability_metaphysis_distal),
            ("Epífisis Distal", self.epiphysis_distal_percent, self.density_epiphysis_distal,
             self.osteona_size_epiphysis_distal, self.variability_epiphysis_distal)
        ]
        
        for i, (name, percent_var, density_var, size_var, variability_var) in enumerate(sections, 1):
            ttk.Label(sections_frame, text=name).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Entry(sections_frame, textvariable=percent_var, width=10).grid(row=i, column=1, padx=5, pady=5)
            ttk.Entry(sections_frame, textvariable=density_var, width=10).grid(row=i, column=2, padx=5, pady=5)
            ttk.Entry(sections_frame, textvariable=size_var, width=10).grid(row=i, column=3, padx=5, pady=5)
            ttk.Entry(sections_frame, textvariable=variability_var, width=10).grid(row=i, column=4, padx=5, pady=5)
        
        # Botón de cálculo
        calculate_button = ttk.Button(self.tab_basic_params, text="Calcular Distribución", command=self.calculate)
        calculate_button.pack(pady=10)
        
        # Área de resultados básicos
        self.basic_results_frame = ttk.LabelFrame(self.tab_basic_params, text="Resultados Básicos")
        self.basic_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.basic_results_text = tk.Text(self.basic_results_frame, height=8, width=80)
        basic_scrollbar = ttk.Scrollbar(self.basic_results_frame, command=self.basic_results_text.yview)
        self.basic_results_text.configure(yscrollcommand=basic_scrollbar.set)
        
        self.basic_results_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        basic_scrollbar.pack(side="right", fill="y")
    
    def setup_advanced_params_tab(self):
        """Nueva pestaña para parámetros avanzados"""
        # Marco para orientación
        orientation_frame = ttk.LabelFrame(self.tab_advanced_params, text="Orientación Preferencial de Osteonas")
        orientation_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(orientation_frame, text="La orientación determina la dirección preferencial de las osteonas (0-360°)", 
                 style="Section.TLabel").grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        
        # Encabezados para orientación
        ttk.Label(orientation_frame, text="Sección").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(orientation_frame, text="Orientación (°)").grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(orientation_frame, text="Fuerza Orient. (0-1)").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Secciones para orientación
        orientation_sections = [
            ("Epífisis Proximal", self.orientation_epiphysis_proximal, self.orientation_strength_epiphysis_proximal),
            ("Metáfisis Proximal", self.orientation_metaphysis_proximal, self.orientation_strength_metaphysis_proximal),
            ("Diáfisis", self.orientation_diaphysis, self.orientation_strength_diaphysis),
            ("Metáfisis Distal", self.orientation_metaphysis_distal, self.orientation_strength_metaphysis_distal),
            ("Epífisis Distal", self.orientation_epiphysis_distal, self.orientation_strength_epiphysis_distal)
        ]
        
        for i, (name, orient_var, strength_var) in enumerate(orientation_sections, 2):
            ttk.Label(orientation_frame, text=name).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Entry(orientation_frame, textvariable=orient_var, width=10).grid(row=i, column=1, padx=5, pady=5)
            ttk.Entry(orientation_frame, textvariable=strength_var, width=10).grid(row=i, column=2, padx=5, pady=5)
        
        # Marco para clustering
        clustering_frame = ttk.LabelFrame(self.tab_advanced_params, text="Factores de Agrupamiento")
        clustering_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(clustering_frame, text="Los factores de clustering determinan la tendencia a formar grupos (0-1)", 
                 style="Section.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(clustering_frame, text="Sección").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(clustering_frame, text="Factor Clustering").grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        clustering_sections = [
            ("Epífisis Proximal", self.clustering_factor_epiphysis_proximal),
            ("Metáfisis Proximal", self.clustering_factor_metaphysis_proximal),
            ("Diáfisis", self.clustering_factor_diaphysis),
            ("Metáfisis Distal", self.clustering_factor_metaphysis_distal),
            ("Epífisis Distal", self.clustering_factor_epiphysis_distal)
        ]
        
        for i, (name, cluster_var) in enumerate(clustering_sections, 2):
            ttk.Label(clustering_frame, text=name).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Entry(clustering_frame, textvariable=cluster_var, width=10).grid(row=i, column=1, padx=5, pady=5)
    
    def setup_simulation_tab(self):
        """Nueva pestaña para simulación de condiciones patológicas"""
        # Marco para modo de simulación
        sim_mode_frame = ttk.LabelFrame(self.tab_simulation, text="Modo de Simulación")
        sim_mode_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(sim_mode_frame, text="Seleccione el tipo de simulación:", style="Section.TLabel").pack(anchor="w", padx=5, pady=5)
        
        sim_modes = [("Normal", "normal"), ("Envejecimiento", "aging"), ("Patológico", "pathological")]
        for text, value in sim_modes:
            ttk.Radiobutton(sim_mode_frame, text=text, variable=self.simulation_mode, 
                           value=value, command=self.update_simulation_params).pack(anchor="w", padx=20, pady=2)
        
        # Marco para factores de simulación
        factors_frame = ttk.LabelFrame(self.tab_simulation, text="Factores de Simulación")
        factors_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        ttk.Label(factors_frame, text="Factor de Edad (0.5=joven, 1.0=adulto, 2.0=anciano):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(factors_frame, from_=0.5, to=2.0, variable=self.age_factor, orient="horizontal", length=300).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(factors_frame, textvariable=self.age_factor).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(factors_frame, text="Factor Patológico (1.0=normal, 2.0=severo):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(factors_frame, from_=1.0, to=2.0, variable=self.pathology_factor, orient="horizontal", length=300).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(factors_frame, textvariable=self.pathology_factor).grid(row=1, column=2, padx=5, pady=5)
        
        # Botones de presets
        presets_frame = ttk.LabelFrame(self.tab_simulation, text="Presets de Simulación")
        presets_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        preset_buttons = [
            ("Hueso Joven Sano", self.preset_young_healthy),
            ("Hueso Adulto Normal", self.preset_adult_normal),
            ("Hueso Envejecido", self.preset_aged),
            ("Osteoporosis Temprana", self.preset_osteoporosis_early),
            ("Osteoporosis Avanzada", self.preset_osteoporosis_advanced)
        ]
        
        for i, (text, command) in enumerate(preset_buttons):
            ttk.Button(presets_frame, text=text, command=command).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        # Información sobre la simulación actual
        self.sim_info_frame = ttk.LabelFrame(self.tab_simulation, text="Información de Simulación Actual")
        self.sim_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.sim_info_text = tk.Text(self.sim_info_frame, height=10, width=80)
        sim_scrollbar = ttk.Scrollbar(self.sim_info_frame, command=self.sim_info_text.yview)
        self.sim_info_text.configure(yscrollcommand=sim_scrollbar.set)
        
        self.sim_info_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sim_scrollbar.pack(side="right", fill="y")
    
    def setup_visualization_tab(self):
        """Pestaña de visualización mejorada"""
        # Marco para controles de visualización
        controls_frame = ttk.Frame(self.tab_visualization)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Botones mejorados
        ttk.Button(controls_frame, text="Actualizar Visualización", command=self.update_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Guardar Imagen", command=self.save_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Vista 3D", command=self.show_3d_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Análisis Estadístico", command=self.show_statistical_analysis).pack(side="left", padx=5)
        
        # Crear figura con más subplots
        self.figure, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        self.figure.tight_layout(pad=3.0)
        
        # Canvas mejorado
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tab_visualization)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
    
    def setup_analysis_tab(self):
        """Nueva pestaña para análisis avanzado"""
        # Marco para métricas
        metrics_frame = ttk.LabelFrame(self.tab_analysis, text="Métricas Biomecánicas")
        metrics_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Botones de análisis
        analysis_buttons = [
            ("Calcular Métricas", self.calculate_biomechanical_metrics),
            ("Análisis de Distribución", self.analyze_distribution_patterns),
            ("Comparar con Referencias", self.compare_with_references),
            ("Generar Reporte", self.generate_analysis_report)
        ]
        
        for i, (text, command) in enumerate(analysis_buttons):
            ttk.Button(metrics_frame, text=text, command=command).grid(row=0, column=i, padx=5, pady=5)
        
        # Área de resultados de análisis
        self.analysis_results_frame = ttk.LabelFrame(self.tab_analysis, text="Resultados del Análisis")
        self.analysis_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.analysis_text = tk.Text(self.analysis_results_frame, height=20, width=80)
        analysis_scrollbar = ttk.Scrollbar(self.analysis_results_frame, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        
        self.analysis_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        analysis_scrollbar.pack(side="right", fill="y")
    
    def setup_export_tab(self):
        """Pestaña de exportación mejorada"""
        # Marco para opciones de exportación
        export_frame = ttk.LabelFrame(self.tab_export, text="Opciones de Exportación Avanzadas")
        export_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Botones de exportación mejorados
        export_buttons = [
            ("Exportar CSV (Grasshopper)", lambda: self.export_data("csv")),
            ("Exportar JSON Completo", lambda: self.export_data("json")),
            ("Exportar para ANSYS/Abaqus", self.export_for_fea),
            ("Exportar STL/OBJ", self.export_3d_model),
            ("Informe Completo PDF", self.export_complete_report)
        ]
        
        for i, (text, command) in enumerate(export_buttons):
            ttk.Button(export_frame, text=text, command=command).grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
        
        # Marco para configuración de exportación
        config_frame = ttk.LabelFrame(self.tab_export, text="Configuración de Exportación")
        config_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Variables de exportación
        self.export_coordinates = tk.BooleanVar(value=True)
        self.export_orientations = tk.BooleanVar(value=True)
        self.export_sizes = tk.BooleanVar(value=True)
        self.export_metadata = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(config_frame, text="Incluir coordenadas", variable=self.export_coordinates).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(config_frame, text="Incluir orientaciones", variable=self.export_orientations).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(config_frame, text="Incluir tamaños", variable=self.export_sizes).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(config_frame, text="Incluir metadatos", variable=self.export_metadata).pack(anchor="w", padx=5, pady=2)
        
        # Área de previsualización mejorada
        preview_frame = ttk.LabelFrame(self.tab_export, text="Previsualización de Datos")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=15, width=80)
        preview_scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scrollbar.pack(side="right", fill="y")
    
    # CONTINUACIÓN DE LOS MÉTODOS (completando el código cortado)
    
    def show_statistical_analysis(self):
        """Muestra análisis estadístico detallado"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para analizar.")
            return
        
        # Crear ventana de análisis estadístico
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Análisis Estadístico Avanzado")
        stats_window.geometry("1000x700")
        
        # Crear notebook para diferentes análisis
        stats_notebook = ttk.Notebook(stats_window)
        stats_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de estadísticas descriptivas
        desc_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(desc_frame, text="Estadísticas Descriptivas")
        
        # Área de texto para estadísticas
        stats_text = tk.Text(desc_frame, height=30, width=80)
        stats_scrollbar = ttk.Scrollbar(desc_frame, command=stats_text.yview)
        stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_text.pack(side="left", fill="both", expand=True)
        stats_scrollbar.pack(side="right", fill="y")
        
        # Calcular estadísticas
        df = pd.DataFrame(self.distribution_data)
        
        stats_content = "ANÁLISIS ESTADÍSTICO AVANZADO\n"
        stats_content += "=" * 50 + "\n\n"
        
        # Estadísticas por sección
        for section_name in df['section_name'].unique():
            section_data = df[df['section_name'] == section_name]
            
            stats_content += f"SECCIÓN: {section_name}\n"
            stats_content += "-" * 30 + "\n"
            stats_content += f"Número de osteonas: {len(section_data)}\n"
            stats_content += f"Tamaño promedio: {section_data['size_um'].mean():.2f} μm\n"
            stats_content += f"Desviación estándar: {section_data['size_um'].std():.2f} μm\n"
            stats_content += f"Rango de tamaños: {section_data['size_um'].min():.2f} - {section_data['size_um'].max():.2f} μm\n"
            
            # Análisis de orientación
            angles = section_data['angle_degrees']
            if len(angles) > 1:
                # Calcular estadísticas circulares
                angles_rad = np.radians(angles)
                mean_angle = np.degrees(np.arctan2(np.mean(np.sin(angles_rad)), np.mean(np.cos(angles_rad))))
                if mean_angle < 0:
                    mean_angle += 360
                
                stats_content += f"Orientación promedio: {mean_angle:.1f}°\n"
                stats_content += f"Dispersión angular: {np.degrees(np.std(angles_rad)):.1f}°\n"
            
            # Análisis de clustering
            clustered_count = len(section_data[section_data['is_clustered'] == True])
            clustering_percentage = (clustered_count / len(section_data)) * 100
            stats_content += f"Osteonas agrupadas: {clustered_count} ({clustering_percentage:.1f}%)\n"
            
            stats_content += "\n"
        
        # Estadísticas globales
        stats_content += "ESTADÍSTICAS GLOBALES\n"
        stats_content += "=" * 30 + "\n"
        stats_content += f"Total de osteonas: {len(df)}\n"
        stats_content += f"Densidad promedio: {len(df) / self.sections_data['total_length_cm']:.1f} ost/cm\n"
        stats_content += f"Tamaño promedio global: {df['size_um'].mean():.2f} μm\n"
        stats_content += f"Coeficiente de variación: {(df['size_um'].std() / df['size_um'].mean()) * 100:.1f}%\n"
        
        # Test de normalidad
        from scipy.stats import shapiro
        stat, p_value = shapiro(df['size_um'])
        stats_content += f"\nTest de Shapiro-Wilk para normalidad de tamaños:\n"
        stats_content += f"Estadístico: {stat:.4f}, p-valor: {p_value:.4f}\n"
        if p_value > 0.05:
            stats_content += "Los tamaños siguen una distribución normal (p > 0.05)\n"
        else:
            stats_content += "Los tamaños NO siguen una distribución normal (p ≤ 0.05)\n"
        
        stats_text.insert(tk.END, stats_content)
        
        # Pestaña de correlaciones
        corr_frame = ttk.Frame(stats_notebook)  
        stats_notebook.add(corr_frame, text="Correlaciones")
        
        # Crear figura para correlaciones
        fig_corr = plt.figure(figsize=(10, 8))
        
        # Matriz de correlación
        numeric_cols = ['position_z_cm', 'angle_degrees', 'size_um']
        correlation_matrix = df[numeric_cols].corr()
        
        ax1 = fig_corr.add_subplot(2, 2, 1)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax1)
        ax1.set_title('Matriz de Correlación')
        
        # Scatter plots
        ax2 = fig_corr.add_subplot(2, 2, 2)
        ax2.scatter(df['position_z_cm'], df['size_um'], alpha=0.6, c='blue')
        ax2.set_xlabel('Posición (cm)')
        ax2.set_ylabel('Tamaño (μm)')
        ax2.set_title('Tamaño vs Posición')
        
        ax3 = fig_corr.add_subplot(2, 2, 3)
        ax3.scatter(df['angle_degrees'], df['size_um'], alpha=0.6, c='red')
        ax3.set_xlabel('Ángulo (°)')
        ax3.set_ylabel('Tamaño (μm)')
        ax3.set_title('Tamaño vs Orientación')
        
        # Histograma de residuos
        ax4 = fig_corr.add_subplot(2, 2, 4)
        ax4.hist(df['size_um'], bins=30, alpha=0.7, color='green', edgecolor='black')
        ax4.set_xlabel('Tamaño (μm)')
        ax4.set_ylabel('Frecuencia')
        ax4.set_title('Distribución de Tamaños')
        
        fig_corr.tight_layout()
        
        canvas_corr = FigureCanvasTkAgg(fig_corr, master=corr_frame)
        canvas_corr.get_tk_widget().pack(fill="both", expand=True)
        canvas_corr.draw()
    
    def calculate_biomechanical_metrics(self):
        """Calcula métricas biomecánicas avanzadas"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para analizar.")
            return
        
        self.analysis_text.delete(1.0, tk.END)
        
        df = pd.DataFrame(self.distribution_data)
        
        analysis_content = "MÉTRICAS BIOMECÁNICAS AVANZADAS\n"
        analysis_content += "=" * 50 + "\n\n"
        
        # Métricas por sección
        for section_name in df['section_name'].unique():
            section_data = df[df['section_name'] == section_name]
            
            analysis_content += f"SECCIÓN: {section_name}\n"
            analysis_content += "-" * 30 + "\n"
            
            # Densidad volumétrica estimada
            avg_area = np.pi * (section_data['size_um'].mean() / 2000) ** 2  # cm²
            total_area = len(section_data) * avg_area
            section_info = next(s for s in self.sections_data['sections'] if s['name'] == section_name)
            section_volume = section_info['length_cm'] * 3.0 * 2.0  # Estimación cilíndrica
            
            porosity = (total_area / section_volume) * 100
            analysis_content += f"Porosidad estimada: {porosity:.2f}%\n"
            
            # Factor de forma (circularidad)
            mean_size = section_data['size_um'].mean()
            std_size = section_data['size_um'].std()
            shape_factor = std_size / mean_size if mean_size > 0 else 0
            analysis_content += f"Factor de heterogeneidad: {shape_factor:.3f}\n"
            
            # Índice de organización (basado en orientación)
            if 'angle_degrees' in section_data.columns:
                angles_rad = np.radians(section_data['angle_degrees'])
                organization_index = np.sqrt(np.mean(np.cos(angles_rad))**2 + np.mean(np.sin(angles_rad))**2)
                analysis_content += f"Índice de organización: {organization_index:.3f} (0=caótico, 1=perfectamente organizado)\n"
            
            # Estimación de propiedades mecánicas
            # Basado en relaciones empíricas de la literatura
            relative_density = 1 - (porosity / 100)
            estimated_modulus = 20000 * (relative_density ** 2.5)  # MPa, fórmula de Gibson-Ashby
            analysis_content += f"Módulo elástico estimado: {estimated_modulus:.0f} MPa\n"
            
            # Resistencia a la compresión estimada
            estimated_strength = 137 * (relative_density ** 1.8)  # MPa
            analysis_content += f"Resistencia estimada: {estimated_strength:.0f} MPa\n"
            
            analysis_content += "\n"
        
        # Métricas globales comparativas
        analysis_content += "ANÁLISIS COMPARATIVO CON VALORES DE REFERENCIA\n"
        analysis_content += "=" * 50 + "\n"
        
        # Valores de referencia para hueso cortical humano
        ref_values = {
            "densidad_diafisis": (50, 80),  # osteonas/cm²
            "tamaño_promedio": (150, 250),  # μm
            "porosidad_cortical": (3, 12),  # %
            "modulo_elastico": (15000, 25000),  # MPa
        }
        
        # Comparar con referencias
        diaphysis_data = df[df['section_name'] == 'Diáfisis']
        if not diaphysis_data.empty:
            current_density = len(diaphysis_data) / self.sections_data['sections'][2]['length_cm']  # Asumiendo diáfisis es índice 2
            current_size = diaphysis_data['size_um'].mean()
            
            analysis_content += f"Densidad actual en diáfisis: {current_density:.1f} ost/cm\n"
            analysis_content += f"Rango normal: {ref_values['densidad_diafisis'][0]}-{ref_values['densidad_diafisis'][1]} ost/cm²\n"
            
            if ref_values['densidad_diafisis'][0] <= current_density <= ref_values['densidad_diafisis'][1]:
                analysis_content += "✓ Densidad dentro del rango normal\n"
            else:
                analysis_content += "⚠ Densidad fuera del rango normal\n"
            
            analysis_content += f"\nTamaño promedio actual: {current_size:.1f} μm\n"
            analysis_content += f"Rango normal: {ref_values['tamaño_promedio'][0]}-{ref_values['tamaño_promedio'][1]} μm\n"
            
            if ref_values['tamaño_promedio'][0] <= current_size <= ref_values['tamaño_promedio'][1]:
                analysis_content += "✓ Tamaño dentro del rango normal\n"
            else:
                analysis_content += "⚠ Tamaño fuera del rango normal\n"
        
        # Interpretación clínica
        analysis_content += "\nINTERPRETACIÓN CLÍNICA:\n"
        analysis_content += "-" * 25 + "\n"
        
        age_factor = self.age_factor.get()
        pathology_factor = self.pathology_factor.get()
        
        if age_factor < 0.8:
            report += "• Patrón microestructural compatible con hueso joven\n"
            report += "• Características: alta densidad osteonal, organización regular\n"
            report += "• Propiedades mecánicas óptimas esperadas\n"
        elif age_factor > 1.5:
            report += "• Patrón microestructural compatible con envejecimiento óseo\n"
            report += "• Características: reducción de densidad, aumento de tamaño de canales\n"
            report += "• Recomendación: monitoreo de fragilidad ósea\n"
        else:
            report += "• Patrón microestructural de hueso adulto normal\n"
            report += "• Características dentro de rangos de referencia\n"
        
        if pathology_factor > 1.3:
            report += "• Alteraciones microestructurales significativas detectadas\n"
            report += "• Posible compromiso de la integridad mecánica\n"
            report += "• Recomendación: evaluación clínica especializada\n"
        
        # Recomendaciones
        report += "\n\nRECOMENDACIONES\n"
        report += "=" * 15 + "\n"
        
        if age_factor > 1.5 or pathology_factor > 1.3:
            report += "• Implementar medidas preventivas de fracturas\n"
            report += "• Considerar suplementación nutricional apropiada\n"
            report += "• Evaluación de factores de riesgo adicionales\n"
            report += "• Seguimiento con especialista en metabolismo óseo\n"
        else:
            report += "• Mantener actividad física regular\n"
            report += "• Dieta equilibrada rica en calcio y vitamina D\n"
            report += "• Evaluación periódica según edad y factores de riesgo\n"
        
        # Limitaciones del estudio
        report += "\n\nLIMITACIONES DEL ANÁLISIS\n"
        report += "=" * 26 + "\n"
        report += "• Análisis basado en modelo computacional, no en muestras reales\n"
        report += "• Estimaciones biomecánicas basadas en fórmulas empíricas\n"
        report += "• Parámetros de simulación requieren validación experimental\n"
        report += "• Análisis limitado a microestructura cortical (osteonas)\n"
        
        # Información técnica
        report += "\n\nINFORMACIÓN TÉCNICA\n"
        report += "=" * 19 + "\n"
        report += f"Algoritmo de generación: {self.get_generation_algorithm()}\n"
        report += f"Seed aleatorio utilizado: {random.getstate()[1][0]}\n"
        report += f"Versión del software: 2.0\n"
        report += f"Método de clustering: Espacial con dispersión gaussiana\n"
        report += f"Distribución de orientaciones: Von Mises modificada\n"
        
        report += "\n\n" + "=" * 50 + "\n"
        report += "Fin del reporte\n"
        report += "Phygital Human Bone 3.0 - Havers Analysis System\n"
        
        return report
    
    def get_generation_algorithm(self):
        """Devuelve información sobre el algoritmo de generación usado"""
        variability = np.mean([
            self.variability_epiphysis_proximal.get(),
            self.variability_metaphysis_proximal.get(),
            self.variability_diaphysis.get(),
            self.variability_metaphysis_distal.get(),
            self.variability_epiphysis_distal.get()
        ])
        
        if variability < 0.3:
            return "Distribución uniforme con variaciones menores"
        elif variability < 0.5:
            return "Distribución normal centrada"
        elif variability < 0.7:
            return "Distribución beta biológicamente realista"
        else:
            return "Distribución multimodal con alta irregularidad"
    
    # MÉTODOS DE EXPORTACIÓN AVANZADOS
    
    def export_for_fea(self):
        """Exporta datos para análisis de elementos finitos (ANSYS/Abaqus)"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".inp",
            filetypes=[("ANSYS Input", "*.inp"), ("Abaqus Input", "*.inp"), ("Todos los archivos", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write("*HEADING\n")
                f.write("** Modelo de microestructura ósea generado por Phygital Bone 3.0\n")
                f.write(f"** Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"** Total de osteonas: {len(self.distribution_data)}\n")
                f.write("*PREPRINT, ECHO=NO, MODEL=NO, HISTORY=NO, CONTACT=NO\n")
                f.write("**\n")
                f.write("** PARTE: FEMUR_MICROSTRUCTURE\n")
                f.write("*PART, NAME=FEMUR_MICROSTRUCTURE\n")
                f.write("*NODE\n")
                
                # Generar nodos para cada osteona (representación simplificada)
                node_id = 1
                for osteona in self.distribution_data:
                    z = osteona["position_z_cm"] * 10  # Convertir a mm
                    angle_rad = np.radians(osteona["angle_degrees"])
                    radius = 15  # Radio fijo para el modelo FEA
                    
                    x = radius * np.cos(angle_rad)
                    y = radius * np.sin(angle_rad)
                    
                    f.write(f"{node_id}, {x:.3f}, {y:.3f}, {z:.3f}\n")
                    node_id += 1
                
                # Propiedades de material
                f.write("*MATERIAL, NAME=CORTICAL_BONE\n")
                f.write("*ELASTIC\n")
                f.write("17000., 0.3\n")  # E=17GPa, nu=0.3
                f.write("*DENSITY\n")
                f.write("1.8E-09\n")  # Densidad en toneladas/mm³
                
                f.write("*END PART\n")
                f.write("**\n")
                f.write("** ASSEMBLY\n")
                f.write("*ASSEMBLY, NAME=ASSEMBLY\n")
                f.write("*INSTANCE, NAME=FEMUR-1, PART=FEMUR_MICROSTRUCTURE\n")
                f.write("*END INSTANCE\n")
                f.write("*END ASSEMBLY\n")
            
            messagebox.showinfo("Éxito", f"Archivo FEA exportado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar archivo FEA:\n{str(e)}")
    
    def export_3d_model(self):
        """Exporta modelo 3D en formato STL u OBJ"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("Wavefront OBJ", "*.obj"), ("STL Binary", "*.stl"), ("Todos los archivos", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.obj'):
                self.export_obj_file(filename)
            elif filename.endswith('.stl'):
                self.export_stl_file(filename)
            else:
                messagebox.showerror("Error", "Formato de archivo no soportado")
                return
                
            messagebox.showinfo("Éxito", f"Modelo 3D exportado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar modelo 3D:\n{str(e)}")
    
    def export_obj_file(self, filename):
        """Exporta en formato OBJ"""
        with open(filename, 'w') as f:
            f.write("# Modelo de microestructura ósea - Phygital Bone 3.0\n")
            f.write(f"# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total osteonas: {len(self.distribution_data)}\n\n")
            
            vertex_count = 0
            
            for i, osteona in enumerate(self.distribution_data):
                z = osteona["position_z_cm"]
                angle_rad = np.radians(osteona["angle_degrees"])
                radius_base = 1.5  # Radio base para visualización
                
                # Crear un cilindro simple para cada osteona
                height = osteona["size_um"] / 1000  # Convertir a cm
                
                # Vértices del cilindro (8 vértices para simplicidad)
                for j in range(8):
                    angle = j * 2 * np.pi / 8
                    x = radius_base * np.cos(angle_rad) + 0.2 * np.cos(angle)
                    y = radius_base * np.sin(angle_rad) + 0.2 * np.sin(angle)
                    
                    # Vértice inferior
                    f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
                    # Vértice superior
                    f.write(f"v {x:.6f} {y:.6f} {z + height:.6f}\n")
                
                # Caras del cilindro (simplificado)
                base_vertex = vertex_count + 1
                for j in range(8):
                    next_j = (j + 1) % 8
                    # Cara lateral
                    v1 = base_vertex + j * 2
                    v2 = base_vertex + j * 2 + 1
                    v3 = base_vertex + next_j * 2 + 1
                    v4 = base_vertex + next_j * 2
                    
                    f.write(f"f {v1} {v2} {v3} {v4}\n")
                
                vertex_count += 16
    
    def export_stl_file(self, filename):
        """Exporta en formato STL (simplificado)"""
        with open(filename, 'w') as f:
            f.write("solid femur_microstructure\n")
            
            for osteona in self.distribution_data:
                z = osteona["position_z_cm"]
                angle_rad = np.radians(osteona["angle_degrees"])
                radius = 1.5
                height = osteona["size_um"] / 1000
                
                x_center = radius * np.cos(angle_rad)
                y_center = radius * np.sin(angle_rad)
                
                # Crear un tetraedro simple para cada osteona
                # Vértices del tetraedro
                vertices = [
                    [x_center, y_center, z],
                    [x_center + 0.1, y_center, z + height],
                    [x_center - 0.05, y_center + 0.087, z + height],
                    [x_center - 0.05, y_center - 0.087, z + height]
                ]
                
                # Caras del tetraedro
                faces = [
                    [0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 2, 3]
                ]
                
                for face in faces:
                    # Calcular normal (simplificado)
                    v1 = np.array(vertices[face[1]]) - np.array(vertices[face[0]])
                    v2 = np.array(vertices[face[2]]) - np.array(vertices[face[0]])
                    normal = np.cross(v1, v2)
                    normal = normal / np.linalg.norm(normal)
                    
                    f.write(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                    f.write("    outer loop\n")
                    for vertex_idx in face:
                        v = vertices[vertex_idx]
                        f.write(f"      vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
                    f.write("    endloop\n")
                    f.write("  endfacet\n")
            
            f.write("endsolid femur_microstructure\n")
    
    def export_complete_report(self):
        """Exporta un paquete completo con todos los archivos"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        # Seleccionar carpeta de destino
        folder = filedialog.askdirectory(title="Seleccionar carpeta para exportación completa")
        if not folder:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_folder = os.path.join(folder, f"femur_analysis_{timestamp}")
            os.makedirs(project_folder, exist_ok=True)
            
            # 1. Exportar datos CSV
            csv_file = os.path.join(project_folder, "osteonas_data.csv")
            self.export_data_to_file(csv_file, "csv")
            
            # 2. Exportar datos JSON
            json_file = os.path.join(project_folder, "osteonas_data.json")
            self.export_data_to_file(json_file, "json")
            
            # 3. Exportar reporte HTML
            html_file = os.path.join(project_folder, "reporte_completo.html")
            self.export_report_html_to_file(html_file)
            
            # 4. Exportar reporte PDF (si es posible)
            try:
                pdf_file = os.path.join(project_folder, "reporte_completo.pdf")
                self.export_report_pdf_to_file(pdf_file)
            except:
                pass  # PDF opcional
            
            # 5. Guardar visualizaciones
            if hasattr(self, 'figure'):
                viz_file = os.path.join(project_folder, "visualizaciones.png")
                self.figure.savefig(viz_file, dpi=300, bbox_inches='tight')
            
            # 6. Exportar configuración
            config_file = os.path.join(project_folder, "configuracion.json")
            self.export_configuration(config_file)
            
            # 7. Crear archivo README
            readme_file = os.path.join(project_folder, "README.txt")
            self.create_readme_file(readme_file, timestamp)
            
            messagebox.showinfo("Éxito", f"Exportación completa realizada en:\n{project_folder}")
            
            # Abrir carpeta automáticamente (Windows)
            try:
                os.startfile(project_folder)
            except:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la exportación completa:\n{str(e)}")
    
    def export_configuration(self, filename):
        """Exporta la configuración actual"""
        config = {
            "femur_length": self.femur_length.get(),
            "simulation_mode": self.simulation_mode.get(),
            "age_factor": self.age_factor.get(),
            "pathology_factor": self.pathology_factor.get(),
            "sections": []
        }
        
        # Añadir configuración de cada sección
        section_vars = [
            ("Epífisis Proximal", self.epiphysis_proximal_percent, self.density_epiphysis_proximal, 
             self.osteona_size_epiphysis_proximal, self.variability_epiphysis_proximal,
             self.orientation_epiphysis_proximal, self.orientation_strength_epiphysis_proximal,
             self.clustering_factor_epiphysis_proximal),
            ("Metáfisis Proximal", self.metaphysis_proximal_percent, self.density_metaphysis_proximal,
             self.osteona_size_metaphysis_proximal, self.variability_metaphysis_proximal,
             self.orientation_metaphysis_proximal, self.orientation_strength_metaphysis_proximal,
             self.clustering_factor_metaphysis_proximal),
            ("Diáfisis", self.diaphysis_percent, self.density_diaphysis,
             self.osteona_size_diaphysis, self.variability_diaphysis,
             self.orientation_diaphysis, self.orientation_strength_diaphysis,
             self.clustering_factor_diaphysis),
            ("Metáfisis Distal", self.metaphysis_distal_percent, self.density_metaphysis_distal,
             self.osteona_size_metaphysis_distal, self.variability_metaphysis_distal,
             self.orientation_metaphysis_distal, self.orientation_strength_metaphysis_distal,
             self.clustering_factor_metaphysis_distal),
            ("Epífisis Distal", self.epiphysis_distal_percent, self.density_epiphysis_distal,
             self.osteona_size_epiphysis_distal, self.variability_epiphysis_distal,
             self.orientation_epiphysis_distal, self.orientation_strength_epiphysis_distal,
             self.clustering_factor_epiphysis_distal)
        ]
        
        for name, percent, density, size, var, orient, orient_str, cluster in section_vars:
            config["sections"].append({
                "name": name,
                "percent": percent.get(),
                "density": density.get(),
                "size": size.get(),
                "variability": var.get(),
                "orientation": orient.get(),
                "orientation_strength": orient_str.get(),
                "clustering_factor": cluster.get()
            })
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_readme_file(self, filename, timestamp):
        """Crea archivo README explicativo"""
        content = f"""ANÁLISIS DE MICROESTRUCTURA ÓSEA - FEMUR
========================================

Generado: {timestamp}
Software: Femur Osteona Distributor Advanced v2.0
Proyecto: Phygital Human Bone 3.0

CONTENIDO DE LA CARPETA:
-----------------------

1. osteonas_data.csv
   - Datos de todas las osteonas en formato CSV
   - Compatible con Grasshopper y Excel
   - Columnas: section_name, position_z_cm, angle_degrees, size_um, cluster_id, is_clustered

2. osteonas_data.json
   - Datos completos en formato JSON
   - Incluye metadatos y configuración de simulación
   - Para uso en aplicaciones web o análisis avanzado

3. reporte_completo.html
   - Reporte completo en formato web
   - Incluye análisis, gráficos y recomendaciones
   - Abrir con cualquier navegador web

4. reporte_completo.pdf (si disponible)
   - Versión PDF del reporte para impresión
   - Formato profesional para documentación

5. visualizaciones.png
   - Gráficos de la distribución de osteonas
   - Alta resolución (300 DPI)
   - Incluye 4 vistas diferentes del análisis

6. configuracion.json
   - Parámetros utilizados en la simulación
   - Para reproducir exactamente los mismos resultados
   - Compatible con importación en futuras versiones

7. README.txt (este archivo)
   - Documentación del contenido
   - Instrucciones de uso

COMO USAR LOS ARCHIVOS:
----------------------

Para Grasshopper/Rhino:
- Usar osteonas_data.csv con el componente "Read File"
- Las coordenadas están en centímetros
- Los ángulos en grados (0-360)

Para análisis estadístico:
- Importar osteonas_data.csv en Excel, R, Python, etc.
- El archivo JSON contiene información adicional

Para presentaciones:
- Usar reporte_completo.html o PDF
- Las visualizaciones están en alta resolución

CONTACTO Y SOPORTE:
------------------
Proyecto: Phygital Human Bone 3.0
Desarrollado en ELISAVA
Para soporte técnico, consultar la documentación del proyecto.

LIMITACIONES:
------------
- Datos generados por simulación computacional
- Las estimaciones biomecánicas requieren validación experimental
- El modelo se basa en literatura científica actualizada a 2024
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def export_data_to_file(self, filename, format_type):
        """Exporta datos a archivo específico"""
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
    
    def export_report_html_to_file(self, filename):
        """Exporta reporte en formato HTML"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis de Microestructura Ósea</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #BD0000; border-bottom: 2px solid #BD0000; }}
        h2 {{ color: #333; border-bottom: 1px solid #ccc; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #BD0000; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border: 1px solid #ddd; border-radius: 5px; }}
        .warning {{ background: #fff3cd; border-color: #ffeaa7; }}
        .normal {{ background: #d4edda; border-color: #c3e6cb; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #BD0000; color: white; }}
    </style>
</head>
<body>
    <h1>Reporte de Análisis de Microestructura Ósea</h1>
    
    <div class="section">
        <h2>Información General</h2>
        <p><strong>Fecha de generación:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Software:</strong> Femur Osteona Distributor Advanced v2.0</p>
        <p><strong>Proyecto:</strong> Phygital Human Bone 3.0</p>
    </div>
    
    <div class="section">
        <h2>Parámetros de Simulación</h2>
        <div class="metric">
            <strong>Longitud del fémur:</strong> {self.femur_length.get():.1f} cm
        </div>
        <div class="metric">
            <strong>Modo de simulación:</strong> {self.simulation_mode.get().upper()}
        </div>
        <div class="metric">
            <strong>Factor de edad:</strong> {self.age_factor.get():.2f}
        </div>
        <div class="metric">
            <strong>Factor patológico:</strong> {self.pathology_factor.get():.2f}
        </div>
    </div>
    
    <div class="section">
        <h2>Resumen de Resultados</h2>
        <p><strong>Total de osteonas generadas:</strong> {len(self.distribution_data)}</p>
"""
        
        # Añadir tabla de secciones
        df = pd.DataFrame(self.distribution_data)
        html_content += """
        <table>
            <tr>
                <th>Sección</th>
                <th>Número de Osteonas</th>
                <th>Tamaño Promedio (μm)</th>
                <th>Desviación Estándar</th>
            </tr>
        """
        
        for section_name in df['section_name'].unique():
            section_data = df[df['section_name'] == section_name]
            html_content += f"""
            <tr>
                <td>{section_name}</td>
                <td>{len(section_data)}</td>
                <td>{section_data['size_um'].mean():.1f}</td>
                <td>{section_data['size_um'].std():.1f}</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>Interpretación Clínica</h2>
        """
        
        # Añadir interpretación basada en factores
        age_factor = self.age_factor.get()
        pathology_factor = self.pathology_factor.get()
        
        if age_factor > 1.5 or pathology_factor > 1.3:
            html_content += '<div class="metric warning">'
            html_content += '<strong>⚠ Atención:</strong> Se detectaron alteraciones microestructurales que requieren evaluación.'
            html_content += '</div>'
        else:
            html_content += '<div class="metric normal">'
            html_content += '<strong>✓ Normal:</strong> Microestructura dentro de parámetros esperados.'
            html_content += '</div>'
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>Datos Técnicos</h2>
        <p><strong>Algoritmo de generación:</strong> """ + self.get_generation_algorithm() + """</p>
        <p><strong>Distribución de orientaciones:</strong> Von Mises modificada</p>
        <p><strong>Método de clustering:</strong> Espacial con dispersión gaussiana</p>
    </div>
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; text-align: center; color: #666;">
        <p>Phygital Human Bone 3.0 - Havers Analysis System</p>
        <p>Desarrollado en ELISAVA</p>
    </footer>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_report_pdf_to_file(self, filename):
        """Exporta reporte en formato PDF (requiere librerías adicionales)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title = Paragraph("Reporte de Análisis de Microestructura Ósea", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Contenido básico (simplificado para compatibilidad)
            content = f"""
            <b>Fecha:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
            <b>Total de osteonas:</b> {len(self.distribution_data)}<br/>
            <b>Longitud del fémur:</b> {self.femur_length.get():.1f} cm<br/>
            <b>Modo de simulación:</b> {self.simulation_mode.get().upper()}<br/>
            """
            
            para = Paragraph(content, styles['Normal'])
            story.append(para)
            
            doc.build(story)
            
        except ImportError:
            # Si no están disponibles las librerías de PDF, crear un archivo de texto
            txt_filename = filename.replace('.pdf', '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_comprehensive_report())
            raise Exception(f"Librerías PDF no disponibles. Reporte guardado como TXT: {txt_filename}")
    
    # MÉTODOS DE EXPORTACIÓN BÁSICOS (mantener compatibilidad)
    
    def export_data(self, format_type):
        """Método de exportación básico (mantiene compatibilidad)"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        if format_type == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        elif format_type == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
        else:
            return
        
        if not filename:
            return
        
        try:
            self.export_data_to_file(filename, format_type)
            messagebox.showinfo("Éxito", f"Datos exportados correctamente:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos:\n{str(e)}")
    
    def export_report_pdf(self):
        """Exporta reporte como PDF"""
        if not hasattr(self, 'current_report_text'):
            messagebox.showwarning("Advertencia", "Primero genere un reporte.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.export_report_pdf_to_file(filename)
            messagebox.showinfo("Éxito", f"Reporte PDF exportado:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
    
    def export_report_html(self):
        """Exporta reporte como HTML"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para generar reporte.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.export_report_html_to_file(filename)
            messagebox.showinfo("Éxito", f"Reporte HTML exportado:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar HTML:\n{str(e)}")
    
    def export_report_txt(self):
        """Exporta reporte como texto plano"""
        if not hasattr(self, 'current_report_text'):
            messagebox.showwarning("Advertencia", "Primero genere un reporte.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.current_report_text)
            messagebox.showinfo("Éxito", f"Reporte TXT exportado:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar TXT:\n{str(e)}")
    
    def save_visualization(self):
        """Guarda la visualización actual"""
        if not hasattr(self, 'figure'):
            messagebox.showwarning("Advertencia", "No hay visualización para guardar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Éxito", f"Visualización guardada:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar visualización:\n{str(e)}")
    
    # MÉTODOS DE CÁLCULO Y GENERACIÓN (completando los métodos faltantes)
    
    def display_results(self):
        """Muestra los resultados básicos en la pestaña principal"""
        if not self.sections_data:
            return
        
        self.basic_results_text.delete(1.0, tk.END)
        
        result_text = f"RESULTADOS DEL ANÁLISIS\n"
        result_text += f"{'='*30}\n\n"
        result_text += f"Longitud total del fémur: {self.sections_data['total_length_cm']:.1f} cm\n"
        result_text += f"Modo de simulación: {self.sections_data['simulation_mode'].upper()}\n"
        result_text += f"Factor de edad: {self.sections_data['age_factor']:.2f}\n"
        result_text += f"Factor patológico: {self.sections_data['pathology_factor']:.2f}\n\n"
        
        total_osteonas = len(self.distribution_data) if self.distribution_data else 0
        result_text += f"Total de osteonas generadas: {total_osteonas}\n\n"
        
        result_text += "DISTRIBUCIÓN POR SECCIONES:\n"
        result_text += f"{'-'*40}\n"
        
        if self.distribution_data:
            df = pd.DataFrame(self.distribution_data)
            for section in self.sections_data['sections']:
                section_data = df[df['section_name'] == section['name']]
                count = len(section_data)
                avg_size = section_data['size_um'].mean() if count > 0 else 0
                
                result_text += f"\n{section['name']}:\n"
                result_text += f"  Longitud: {section['length_cm']:.1f} cm ({section['percent']:.1f}%)\n"
                result_text += f"  Osteonas: {count}\n"
                result_text += f"  Densidad: {section['density_per_cm2']:.1f} ost/cm²\n"
                result_text += f"  Tamaño promedio: {avg_size:.1f} μm\n"
        
        result_text += f"\n{'-'*40}\n"
        result_text += "Para análisis detallado, consulte las otras pestañas.\n"
        
        self.basic_results_text.insert(tk.END, result_text)
    
    def update_preview(self):
        """Actualiza la previsualización de exportación"""
        if not self.distribution_data:
            return
        
        self.preview_text.delete(1.0, tk.END)
        
        # Mostrar primeras 20 filas como preview
        preview_text = "PREVISUALIZACIÓN DE DATOS PARA EXPORTACIÓN\n"
        preview_text += "=" * 45 + "\n\n"
        
        if self.export_coordinates.get():
            preview_text += "Formato CSV para Grasshopper:\n"
            preview_text += "section_name,position_z_cm,angle_degrees,size_um\n"
            preview_text += "-" * 50 + "\n"
            
            for i, osteona in enumerate(self.distribution_data[:20]):
                if self.export_coordinates.get():
                    line = f"{osteona['section_name']},{osteona['position_z_cm']:.3f}"
                    if self.export_orientations.get():
                        line += f",{osteona['angle_degrees']:.1f}"
                    if self.export_sizes.get():
                        line += f",{osteona['size_um']:.1f}"
                    preview_text += line + "\n"
            
            if len(self.distribution_data) > 20:
                preview_text += f"... y {len(self.distribution_data) - 20} filas más\n"
        
        preview_text += f"\nTotal de registros: {len(self.distribution_data)}\n"
        preview_text += f"Campos incluidos: "
        
        fields = []
        if self.export_coordinates.get():
            fields.extend(["section_name", "position_z_cm"])
        if self.export_orientations.get():
            fields.append("angle_degrees")
        if self.export_sizes.get():
            fields.append("size_um")
        
        preview_text += ", ".join(fields) + "\n"
        
        if self.export_metadata.get():
            preview_text += "\nMetadatos adicionales incluidos en JSON:\n"
            preview_text += "- Configuración de simulación\n"
            preview_text += "- Parámetros por sección\n"
            preview_text += "- Información de clustering\n"
            preview_text += "- Timestamp de generación\n"
        
        self.preview_text.insert(tk.END, preview_text)
    
    # MÉTODOS AUXILIARES Y DE UTILIDAD
    
    def reset_all_parameters(self):
        """Reinicia todos los parámetros a valores por defecto"""
        # Parámetros básicos
        self.femur_length.set(45.0)
        self.epiphysis_proximal_percent.set(15.0)
        self.metaphysis_proximal_percent.set(10.0)
        self.diaphysis_percent.set(50.0)
        self.metaphysis_distal_percent.set(10.0)
        self.epiphysis_distal_percent.set(15.0)
        
        # Densidades
        self.density_epiphysis_proximal.set(25.0)
        self.density_metaphysis_proximal.set(40.0)
        self.density_diaphysis.set(60.0)
        self.density_metaphysis_distal.set(40.0)
        self.density_epiphysis_distal.set(25.0)
        
        # Tamaños
        self.osteona_size_epiphysis_proximal.set(220.0)
        self.osteona_size_metaphysis_proximal.set(190.0)
        self.osteona_size_diaphysis.set(150.0)
        self.osteona_size_metaphysis_distal.set(190.0)
        self.osteona_size_epiphysis_distal.set(220.0)
        
        # Variabilidades
        self.variability_epiphysis_proximal.set(0.7)
        self.variability_metaphysis_proximal.set(0.5)
        self.variability_diaphysis.set(0.3)
        self.variability_metaphysis_distal.set(0.5)
        self.variability_epiphysis_distal.set(0.7)
        
        # Parámetros avanzados
        for var in [self.orientation_epiphysis_proximal, self.orientation_metaphysis_proximal,
                    self.orientation_diaphysis, self.orientation_metaphysis_distal, 
                    self.orientation_epiphysis_distal]:
            var.set(0.0)
        
        self.orientation_strength_epiphysis_proximal.set(0.2)
        self.orientation_strength_metaphysis_proximal.set(0.4)
        self.orientation_strength_diaphysis.set(0.8)
        self.orientation_strength_metaphysis_distal.set(0.4)
        self.orientation_strength_epiphysis_distal.set(0.2)
        
        self.clustering_factor_epiphysis_proximal.set(0.3)
        self.clustering_factor_metaphysis_proximal.set(0.2)
        self.clustering_factor_diaphysis.set(0.1)
        self.clustering_factor_metaphysis_distal.set(0.2)
        self.clustering_factor_epiphysis_distal.set(0.3)
        
        # Simulación
        self.simulation_mode.set("normal")
        self.age_factor.set(1.0)
        self.pathology_factor.set(1.0)
        
        self.calculate()

# FUNCIÓN PRINCIPAL PARA EJECUTAR LA APLICACIÓN
def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = FemurOsteonaDistributorAdvanced(root)
    
    # Configurar el cierre de la aplicación
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Está seguro de que desea salir?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Centrar la ventana en la pantalla
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Configurar icono si existe
    try:
        root.iconbitmap("icon.ico")  # Opcional: añadir icono
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()_factor = self.pathology_factor.get()

        if age_factor > 1.5:
            analysis_content += "• Microestructura compatible con envejecimiento óseo\n"
            analysis_content += "• Recomendado: monitoreo de fragilidad ósea\n"
        
        if pathology_factor > 1.3:
            analysis_content += "• Alteraciones microestructurales significativas\n"
            analysis_content += "• Posible compromiso de resistencia mecánica\n"
            analysis_content += "• Evaluación clínica recomendada\n"
        
        if age_factor <= 1.0 and pathology_factor <= 1.1:
            analysis_content += "• Microestructura dentro de parámetros normales\n"
            analysis_content += "• No se observan alteraciones significativas\n"
        
        self.analysis_text.insert(tk.END, analysis_content)
    
    def analyze_distribution_patterns(self):
        """Analiza patrones de distribución espacial"""
        if not self.distribution_data:
            return
        
        self.analysis_text.delete(1.0, tk.END)
        
        df = pd.DataFrame(self.distribution_data)
        
        content = "ANÁLISIS DE PATRONES DE DISTRIBUCIÓN\n"
        content += "=" * 40 + "\n\n"
        
        # Análisis de uniformidad espacial
        positions = df['position_z_cm'].values
        total_length = self.sections_data['total_length_cm']
        
        # Test de uniformidad (Kolmogorov-Smirnov)
        from scipy.stats import kstest
        uniform_positions = positions / total_length  # Normalizar a [0,1]
        ks_stat, ks_p = kstest(uniform_positions, 'uniform')
        
        content += "TEST DE UNIFORMIDAD ESPACIAL:\n"
        content += f"Estadístico KS: {ks_stat:.4f}\n"
        content += f"P-valor: {ks_p:.4f}\n"
        
        if ks_p > 0.05:
            content += "✓ Distribución espacial uniforme (p > 0.05)\n"
        else:
            content += "⚠ Distribución espacial NO uniforme (p ≤ 0.05)\n"
        
        content += "\n"
        
        # Análisis de clustering
        clustered_count = len(df[df['is_clustered'] == True])
        total_count = len(df)
        clustering_ratio = clustered_count / total_count
        
        content += "ANÁLISIS DE AGRUPAMIENTO:\n"
        content += f"Osteonas agrupadas: {clustered_count}/{total_count} ({clustering_ratio*100:.1f}%)\n"
        
        if clustering_ratio > 0.3:
            content += "• Alta tendencia al agrupamiento\n"
            content += "• Patrón típico de remodelación activa\n"
        elif clustering_ratio > 0.15:
            content += "• Agrupamiento moderado\n"
            content += "• Distribución mixta normal\n"
        else:
            content += "• Baja tendencia al agrupamiento\n"
            content += "• Distribución más uniforme\n"
        
        content += "\n"
        
        # Análisis de gradientes
        content += "ANÁLISIS DE GRADIENTES:\n"
        
        # Gradiente de tamaño a lo largo del hueso
        from scipy.stats import pearsonr
        size_position_corr, size_p = pearsonr(df['position_z_cm'], df['size_um'])
        
        content += f"Correlación tamaño-posición: {size_position_corr:.3f} (p={size_p:.3f})\n"
        
        if abs(size_position_corr) > 0.3 and size_p < 0.05:
            if size_position_corr > 0:
                content += "• Gradiente positivo: osteonas más grandes hacia distal\n"
            else:
                content += "• Gradiente negativo: osteonas más pequeñas hacia distal\n"
        else:
            content += "• No se observa gradiente significativo de tamaño\n"
        
        # Análisis de periodicidad
        content += "\nANÁLISIS DE PERIODICIDAD:\n"
        
        # Dividir en bins y analizar variación de densidad
        n_bins = 10
        bin_edges = np.linspace(0, total_length, n_bins + 1)
        bin_counts = np.histogram(positions, bins=bin_edges)[0]
        
        # Coeficiente de variación de la densidad
        density_cv = np.std(bin_counts) / np.mean(bin_counts) if np.mean(bin_counts) > 0 else 0
        
        content += f"Coeficiente de variación de densidad: {density_cv:.3f}\n"
        
        if density_cv > 0.5:
            content += "• Alta variabilidad en densidad local\n"
            content += "• Posible patrón de remodelación heterogénea\n"
        elif density_cv > 0.2:
            content += "• Variabilidad moderada en densidad\n"
            content += "• Distribución normal con fluctuaciones\n"
        else:
            content += "• Baja variabilidad en densidad\n"
            content += "• Distribución muy uniforme\n"
        
        self.analysis_text.insert(tk.END, content)
    
    def compare_with_references(self):
        """Compara con valores de referencia de la literatura"""
        if not self.distribution_data:
            return
        
        self.analysis_text.delete(1.0, tk.END)
        
        content = "COMPARACIÓN CON VALORES DE REFERENCIA\n"
        content += "=" * 45 + "\n\n"
        
        # Valores de referencia de la literatura científica
        references = {
            "Hueso Joven (20-30 años)": {
                "densidad_diafisis": 65,
                "tamaño_promedio": 160,
                "variabilidad": 0.25,
                "porosidad": 5
            },
            "Hueso Adulto (30-50 años)": {
                "densidad_diafisis": 58,
                "tamaño_promedio": 175,
                "variabilidad": 0.30,
                "porosidad": 7
            },
            "Hueso Envejecido (50-70 años)": {
                "densidad_diafisis": 48,
                "tamaño_promedio": 195,
                "variabilidad": 0.40,
                "porosidad": 10
            },
            "Osteoporosis": {
                "densidad_diafisis": 35,
                "tamaño_promedio": 220,
                "variabilidad": 0.55,
                "porosidad": 15
            }
        }
        
        # Calcular métricas actuales
        df = pd.DataFrame(self.distribution_data)
        diaphysis_data = df[df['section_name'] == 'Diáfisis']
        
        if diaphysis_data.empty:
            content += "No hay datos de diáfisis para comparar.\n"
            self.analysis_text.insert(tk.END, content)
            return
        
        current_metrics = {
            "densidad_diafisis": len(diaphysis_data) / (self.sections_data['sections'][2]['length_cm'] * 3),  # osteonas/cm²
            "tamaño_promedio": diaphysis_data['size_um'].mean(),
            "variabilidad": diaphysis_data['size_um'].std() / diaphysis_data['size_um'].mean(),
            "porosidad": (len(diaphysis_data) * np.pi * (diaphysis_data['size_um'].mean()/2000)**2 / 
                         (self.sections_data['sections'][2]['length_cm'] * 3)) * 100
        }
        
        content += "MÉTRICAS ACTUALES:\n"
        content += f"Densidad en diáfisis: {current_metrics['densidad_diafisis']:.1f} ost/cm²\n"
        content += f"Tamaño promedio: {current_metrics['tamaño_promedio']:.1f} μm\n"
        content += f"Coef. variabilidad: {current_metrics['variabilidad']:.3f}\n"
        content += f"Porosidad estimada: {current_metrics['porosidad']:.1f}%\n\n"
        
        # Comparar con cada referencia
        best_match = None
        min_distance = float('inf')
        
        for ref_name, ref_values in references.items():
            content += f"COMPARACIÓN CON {ref_name}:\n"
            content += "-" * (len(ref_name) + 15) + "\n"
            
            # Calcular diferencias normalizadas
            diff_density = abs(current_metrics['densidad_diafisis'] - ref_values['densidad_diafisis']) / ref_values['densidad_diafisis']
            diff_size = abs(current_metrics['tamaño_promedio'] - ref_values['tamaño_promedio']) / ref_values['tamaño_promedio']
            diff_var = abs(current_metrics['variabilidad'] - ref_values['variabilidad']) / ref_values['variabilidad']
            diff_porosity = abs(current_metrics['porosidad'] - ref_values['porosidad']) / ref_values['porosidad']
            
            # Distancia euclidiana normalizada
            distance = np.sqrt(diff_density**2 + diff_size**2 + diff_var**2 + diff_porosity**2)
            
            content += f"Diferencia en densidad: {diff_density*100:.1f}%\n"
            content += f"Diferencia en tamaño: {diff_size*100:.1f}%\n"
            content += f"Diferencia en variabilidad: {diff_var*100:.1f}%\n"
            content += f"Diferencia en porosidad: {diff_porosity*100:.1f}%\n"
            content += f"Índice de similitud: {(1-distance)*100:.1f}%\n\n"
            
            if distance < min_distance:
                min_distance = distance
                best_match = ref_name
        
        content += "RESULTADO DE LA COMPARACIÓN:\n"
        content += "=" * 30 + "\n"
        content += f"Mejor coincidencia: {best_match}\n"
        content += f"Similitud: {(1-min_distance)*100:.1f}%\n\n"
        
        # Interpretación
        content += "INTERPRETACIÓN:\n"
        if min_distance < 0.3:
            content += "✓ Microestructura muy similar al patrón de referencia\n"
        elif min_distance < 0.5:
            content += "~ Microestructura moderadamente similar al patrón de referencia\n"
        else:
            content += "⚠ Microestructura significativamente diferente a patrones normales\n"
        
        # Recomendaciones
        content += "\nRECOMENDACIONES:\n"
        if "Osteoporosis" in best_match:
            content += "• Considerar evaluación clínica de fragilidad ósea\n"
            content += "• Implementar medidas preventivas de fracturas\n"
            content += "• Monitoreo regular de densidad mineral ósea\n"
        elif "Envejecido" in best_match:
            content += "• Patrón compatible con envejecimiento normal\n"
            content += "• Mantener actividad física adecuada\n"
            content += "• Considerar suplementación si es apropiada\n"
        else:
            content += "• Microestructura dentro de parámetros normales\n"
            content += "• Continuar con hábitos saludables actuales\n"
        
        self.analysis_text.insert(tk.END, content)
    
    def generate_analysis_report(self):
        """Genera un reporte completo de análisis"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para generar reporte.")
            return
        
        # Crear ventana de reporte
        report_window = tk.Toplevel(self.root)
        report_window.title("Reporte de Análisis Completo")
        report_window.geometry("900x700")
        
        # Marco principal
        main_frame = ttk.Frame(report_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones de exportación
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(button_frame, text="Exportar como PDF", command=self.export_report_pdf).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exportar como HTML", command=self.export_report_html).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exportar como TXT", command=self.export_report_txt).pack(side="left", padx=5)
        
        # Área de texto para el reporte
        report_text = tk.Text(main_frame, height=35, width=100)
        report_scrollbar = ttk.Scrollbar(main_frame, command=report_text.yview)
        report_text.configure(yscrollcommand=report_scrollbar.set)
        
        report_text.pack(side="left", fill="both", expand=True)
        report_scrollbar.pack(side="right", fill="y")
        
        # Generar contenido del reporte
        report_content = self.generate_comprehensive_report()
        report_text.insert(tk.END, report_content)
        
        # Guardar referencia al texto para exportación
        self.current_report_text = report_content
    
    def generate_comprehensive_report(self):
        """Genera el contenido completo del reporte"""
        df = pd.DataFrame(self.distribution_data)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
REPORTE DE ANÁLISIS DE MICROESTRUCTURA ÓSEA
===========================================

Generado: {timestamp}
Software: Femur Osteona Distributor Advanced v2.0
Proyecto: Phygital Human Bone 3.0

PARÁMETROS DE SIMULACIÓN
------------------------
Longitud del fémur: {self.femur_length.get():.1f} cm
Modo de simulación: {self.simulation_mode.get().upper()}
Factor de edad: {self.age_factor.get():.2f}
Factor patológico: {self.pathology_factor.get():.2f}

RESUMEN EJECUTIVO
-----------------
Total de osteonas generadas: {len(df)}
Distribución por secciones:
"""
        
        # Estadísticas por sección
        for section_name in df['section_name'].unique():
            section_data = df[df['section_name'] == section_name]
            report += f"  • {section_name}: {len(section_data)} osteonas\n"
        
        report += f"\nTamaño promedio global: {df['size_um'].mean():.1f} μm\n"
        report += f"Rango de tamaños: {df['size_um'].min():.1f} - {df['size_um'].max():.1f} μm\n"
        report += f"Coeficiente de variación: {(df['size_um'].std() / df['size_um'].mean()) * 100:.1f}%\n"
        
        # Análisis detallado por sección
        report += "\n\nANÁLISIS DETALLADO POR SECCIÓN\n"
        report += "=" * 35 + "\n"
        
        for section in self.sections_data['sections']:
            section_data = df[df['section_name'] == section['name']]
            if section_data.empty:
                continue
                
            report += f"\n{section['name'].upper()}\n"
            report += "-" * len(section['name']) + "\n"
            report += f"Longitud: {section['length_cm']:.1f} cm ({section['percent']:.1f}% del total)\n"
            report += f"Número de osteonas: {len(section_data)}\n"
            report += f"Densidad: {section['density_per_cm2']:.1f} ost/cm²\n"
            report += f"Tamaño promedio: {section_data['size_um'].mean():.1f} μm\n"
            report += f"Desviación estándar: {section_data['size_um'].std():.1f} μm\n"
            report += f"Variabilidad configurada: {section['variability']:.2f}\n"
            
            # Análisis de orientación
            if 'angle_degrees' in section_data.columns:
                angles_rad = np.radians(section_data['angle_degrees'])
                mean_angle = np.degrees(np.arctan2(np.mean(np.sin(angles_rad)), np.mean(np.cos(angles_rad))))
                if mean_angle < 0:
                    mean_angle += 360
                report += f"Orientación preferencial: {mean_angle:.1f}°\n"
                report += f"Fuerza de orientación: {section.get('orientation_strength', 0):.2f}\n"
            
            # Clustering
            clustered_count = len(section_data[section_data['is_clustered'] == True])
            clustering_pct = (clustered_count / len(section_data)) * 100 if len(section_data) > 0 else 0
            report += f"Factor de clustering: {section.get('clustering', 0):.2f}\n"
            report += f"Osteonas agrupadas: {clustering_pct:.1f}%\n"
        
        # Análisis biomecánico
        report += "\n\nANÁLISIS BIOMECÁNICO\n"
        report += "=" * 20 + "\n"
        
        # Estimaciones de propiedades mecánicas para la diáfisis
        diaphysis_data = df[df['section_name'] == 'Diáfisis']
        if not diaphysis_data.empty:
            avg_area = np.pi * (diaphysis_data['size_um'].mean() / 2000) ** 2  # cm²
            total_area = len(diaphysis_data) * avg_area
            diaphysis_section = next(s for s in self.sections_data['sections'] if s['name'] == 'Diáfisis')
            section_volume = diaphysis_section['length_cm'] * 3.0 * 2.0
            
            porosity = (total_area / section_volume) * 100
            relative_density = 1 - (porosity / 100)
            estimated_modulus = 20000 * (relative_density ** 2.5)
            estimated_strength = 137 * (relative_density ** 1.8)
            
            report += f"Porosidad estimada (diáfisis): {porosity:.2f}%\n"
            report += f"Densidad relativa: {relative_density:.3f}\n"
            report += f"Módulo elástico estimado: {estimated_modulus:.0f} MPa\n"
            report += f"Resistencia estimada: {estimated_strength:.0f} MPa\n"
        
        # Interpretación clínica
        report += "\n\nINTERPRETACIÓN CLÍNICA\n"
        report += "=" * 22 + "\n"
        
        age_factor = self.age_factor.get()
        pathology