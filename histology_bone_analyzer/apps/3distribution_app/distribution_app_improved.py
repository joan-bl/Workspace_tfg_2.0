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
        
        # Concentración de dispersión angular (0.0-1.0, donde 1.0 = todas las osteonas apuntan en la misma dirección)
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
    
    # MÉTODOS DE SIMULACIÓN Y PRESETS
    def update_simulation_params(self):
        """Actualiza parámetros según el modo de simulación"""
        mode = self.simulation_mode.get()
        
        if mode == "aging":
            self.age_factor.set(1.8)
            self.pathology_factor.set(1.2)
        elif mode == "pathological":
            self.age_factor.set(1.0)
            self.pathology_factor.set(1.8)
        else:  # normal
            self.age_factor.set(1.0)
            self.pathology_factor.set(1.0)
        
        self.update_simulation_info()
    
    def preset_young_healthy(self):
        """Preset para hueso joven y sano"""
        self.age_factor.set(0.6)
        self.pathology_factor.set(1.0)
        self.simulation_mode.set("normal")
        
        # Ajustar densidades (hueso joven tiene más osteonas)
        self.density_diaphysis.set(70.0)
        self.density_metaphysis_proximal.set(45.0)
        self.density_metaphysis_distal.set(45.0)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_adult_normal(self):
        """Preset para hueso adulto normal"""
        self.age_factor.set(1.0)
        self.pathology_factor.set(1.0)
        self.simulation_mode.set("normal")
        
        # Valores por defecto
        self.density_diaphysis.set(60.0)
        self.density_metaphysis_proximal.set(40.0)
        self.density_metaphysis_distal.set(40.0)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_aged(self):
        """Preset para hueso envejecido"""
        self.age_factor.set(1.8)
        self.pathology_factor.set(1.3)
        self.simulation_mode.set("aging")
        
        # Densidades reducidas y tamaños aumentados
        self.density_diaphysis.set(45.0)
        self.density_metaphysis_proximal.set(30.0)
        self.density_metaphysis_distal.set(30.0)
        
        # Osteonas más grandes
        self.osteona_size_diaphysis.set(180.0)
        self.osteona_size_metaphysis_proximal.set(210.0)
        self.osteona_size_metaphysis_distal.set(210.0)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_osteoporosis_early(self):
        """Preset para osteoporosis temprana"""
        self.age_factor.set(1.5)
        self.pathology_factor.set(1.6)
        self.simulation_mode.set("pathological")
        
        # Cambios característicos de osteoporosis temprana
        self.density_diaphysis.set(50.0)
        self.density_metaphysis_proximal.set(35.0)
        self.density_metaphysis_distal.set(35.0)
        self.density_epiphysis_proximal.set(20.0)
        self.density_epiphysis_distal.set(20.0)
        
        # Mayor variabilidad
        self.variability_diaphysis.set(0.5)
        self.variability_metaphysis_proximal.set(0.7)
        self.variability_metaphysis_distal.set(0.7)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_osteoporosis_advanced(self):
        """Preset para osteoporosis avanzada"""
        self.age_factor.set(2.0)
        self.pathology_factor.set(2.0)
        self.simulation_mode.set("pathological")
        
        # Cambios severos
        self.density_diaphysis.set(35.0)
        self.density_metaphysis_proximal.set(25.0)
        self.density_metaphysis_distal.set(25.0)
        self.density_epiphysis_proximal.set(15.0)
        self.density_epiphysis_distal.set(15.0)
        
        # Osteonas muy grandes y muy variables
        self.osteona_size_diaphysis.set(200.0)
        self.osteona_size_metaphysis_proximal.set(230.0)
        self.osteona_size_metaphysis_distal.set(230.0)
        self.osteona_size_epiphysis_proximal.set(250.0)
        self.osteona_size_epiphysis_distal.set(250.0)
        
        # Máxima variabilidad
        self.variability_diaphysis.set(0.8)
        self.variability_metaphysis_proximal.set(0.9)
        self.variability_metaphysis_distal.set(0.9)
        self.variability_epiphysis_proximal.set(1.0)
        self.variability_epiphysis_distal.set(1.0)
        
        self.calculate()
        self.update_simulation_info()
    
    def update_simulation_info(self):
        """Actualiza la información de simulación"""
        self.sim_info_text.delete(1.0, tk.END)
        
        mode = self.simulation_mode.get()
        age = self.age_factor.get()
        pathology = self.pathology_factor.get()
        
        info_text = f"""INFORMACIÓN DE SIMULACIÓN ACTUAL

Modo de simulación: {mode.upper()}
Factor de edad: {age:.2f}
Factor patológico: {pathology:.2f}

INTERPRETACIÓN:
"""
        
        if mode == "normal":
            info_text += "• Simulando condiciones normales de hueso adulto sano\n"
        elif mode == "aging":
            info_text += "• Simulando efectos del envejecimiento natural\n"
            info_text += "• Reducción gradual de densidad osteonal\n"
            info_text += "• Aumento del tamaño de canales de Havers\n"
        else:  # pathological
            info_text += "• Simulando condiciones patológicas\n"
            info_text += "• Alteraciones significativas en microestructura\n"
            info_text += "• Posible osteoporosis u otras patologías\n"
        
        if age < 0.8:
            info_text += "\nFACTOR DE EDAD: Hueso joven\n"
            info_text += "• Mayor densidad osteonal\n"
            info_text += "• Mejor organización estructural\n"
        elif age > 1.5:
            info_text += "\nFACTOR DE EDAD: Hueso envejecido\n"
            info_text += "• Reducción de densidad osteonal\n"
            info_text += "• Aumento del tamaño de canales\n"
            info_text += "• Mayor variabilidad estructural\n"
        
        if pathology > 1.5:
            info_text += "\nFACTOR PATOLÓGICO: Alteraciones significativas\n"
            info_text += "• Posible pérdida de masa ósea\n"
            info_text += "• Deterioro de la microarquitectura\n"
            info_text += "• Aumento del riesgo de fractura\n"
        
        self.sim_info_text.insert(tk.END, info_text)
    
    # MÉTODOS DE CÁLCULO MEJORADOS
    def calculate(self):
        """Cálculo mejorado con factores de simulación"""
        try:
            # Obtener la longitud total
            total_length = self.femur_length.get()
            
            # Verificar que los porcentajes suman 100%
            total_percent = (
                self.epiphysis_proximal_percent.get() +
                self.metaphysis_proximal_percent.get() +
                self.diaphysis_percent.get() +
                self.metaphysis_distal_percent.get() +
                self.epiphysis_distal_percent.get()
            )
            
            if abs(total_percent - 100.0) > 0.01:
                messagebox.showwarning("Advertencia", 
                                      f"Los porcentajes suman {total_percent}%, no 100%")
                return
            
            # Aplicar factores de simulación
            age_factor = self.age_factor.get()
            pathology_factor = self.pathology_factor.get()
            
            # Calcular datos de secciones con factores aplicados
            self.sections_data = self.calculate_sections_with_factors(total_length, age_factor, pathology_factor)
            
            # Generar distribución mejorada
            self.generate_advanced_osteona_distribution()
            
            # Mostrar resultados
            self.display_results()
            
            # Actualizar visualización y análisis
            self.update_visualization()
            self.update_preview()
            self.update_simulation_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {str(e)}")
    
    def calculate_sections_with_factors(self, total_length, age_factor, pathology_factor):
        """Calcula datos de secciones aplicando factores de simulación"""
        # Calcular longitudes absolutas
        sections = [
            {
                "name": "Epífisis Proximal",
                "percent": self.epiphysis_proximal_percent.get(),
                "base_density": self.density_epiphysis_proximal.get(),
                "base_size": self.osteona_size_epiphysis_proximal.get(),
                "base_variability": self.variability_epiphysis_proximal.get(),
                "orientation": self.orientation_epiphysis_proximal.get(),
                "orientation_strength": self.orientation_strength_epiphysis_proximal.get(),
                "clustering": self.clustering_factor_epiphysis_proximal.get()
            },
            {
                "name": "Metáfisis Proximal",
                "percent": self.metaphysis_proximal_percent.get(),
                "base_density": self.density_metaphysis_proximal.get(),
                "base_size": self.osteona_size_metaphysis_proximal.get(),
                "base_variability": self.variability_metaphysis_proximal.get(),
                "orientation": self.orientation_metaphysis_proximal.get(),
                "orientation_strength": self.orientation_strength_metaphysis_proximal.get(),
                "clustering": self.clustering_factor_metaphysis_proximal.get()
            },
            {
                "name": "Diáfisis",
                "percent": self.diaphysis_percent.get(),
                "base_density": self.density_diaphysis.get(),
                "base_size": self.osteona_size_diaphysis.get(),
                "base_variability": self.variability_diaphysis.get(),
                "orientation": self.orientation_diaphysis.get(),
                "orientation_strength": self.orientation_strength_diaphysis.get(),
                "clustering": self.clustering_factor_diaphysis.get()
            },
            {
                "name": "Metáfisis Distal",
                "percent": self.metaphysis_distal_percent.get(),
                "base_density": self.density_metaphysis_distal.get(),
                "base_size": self.osteona_size_metaphysis_distal.get(),
                "base_variability": self.variability_metaphysis_distal.get(),
                "orientation": self.orientation_metaphysis_distal.get(),
                "orientation_strength": self.orientation_strength_metaphysis_distal.get(),
                "clustering": self.clustering_factor_metaphysis_distal.get()
            },
            {
                "name": "Epífisis Distal",
                "percent": self.epiphysis_distal_percent.get(),
                "base_density": self.density_epiphysis_distal.get(),
                "base_size": self.osteona_size_epiphysis_distal.get(),
                "base_variability": self.variability_epiphysis_distal.get(),
                "orientation": self.orientation_epiphysis_distal.get(),
                "orientation_strength": self.orientation_strength_epiphysis_distal.get(),
                "clustering": self.clustering_factor_epiphysis_distal.get()
            }
        ]
        
        # Calcular posiciones y aplicar factores
        current_pos = 0
        for section in sections:
            section["length_cm"] = total_length * (section["percent"] / 100)
            section["start_cm"] = current_pos
            section["end_cm"] = current_pos + section["length_cm"]
            current_pos = section["end_cm"]
            
            # Aplicar factores de simulación
            # El envejecimiento reduce densidad y aumenta tamaño
            density_factor = 1.0 / (age_factor * 0.5 + 0.5)
            size_factor = age_factor * 0.3 + 0.7
            
            # Factores patológicos
            pathology_density_factor = 1.0 / pathology_factor
            pathology_size_factor = pathology_factor * 0.4 + 0.6
            
            # Aplicar todos los factores
            section["density_per_cm2"] = section["base_density"] * density_factor * pathology_density_factor
            section["osteona_size_um"] = section["base_size"] * size_factor * pathology_size_factor
            section["variability"] = min(1.0, section["base_variability"] * (age_factor + pathology_factor) / 2)
        
        return {
            "total_length_cm": total_length,
            "age_factor": age_factor,
            "pathology_factor": pathology_factor,
            "simulation_mode": self.simulation_mode.get(),
            "sections": sections
        }
    
    def generate_advanced_osteona_distribution(self):
        """Generación avanzada de distribución con orientación y clustering"""
        distribution_data = []
        
        for section in self.sections_data["sections"]:
            # Calcular número de osteonas
            avg_width = 3.0  # cm
            section_area = section["length_cm"] * avg_width
            num_osteonas = int(section_area * section["density_per_cm2"])
            
            section_osteonas = []
            
            # Generar clusters si el factor de clustering es alto
            if section["clustering"] > 0.5:
                clusters = self.generate_clusters(section, num_osteonas)
                for cluster in clusters:
                    section_osteonas.extend(cluster)
            else:
                # Distribución normal
                for i in range(num_osteonas):
                    osteona = self.generate_single_osteona(section)
                    section_osteonas.append(osteona)
            
            distribution_data.extend(section_osteonas)
        
        self.distribution_data = distribution_data
    
    def generate_clusters(self, section, num_osteonas):
        """Genera clusters de osteonas"""
        clustering_factor = section["clustering"]
        num_clusters = max(1, int(num_osteonas * clustering_factor / 10))
        clusters = []
        
        osteonas_per_cluster = num_osteonas // num_clusters
        remaining_osteonas = num_osteonas % num_clusters
        
        for cluster_idx in range(num_clusters):
            cluster_size = osteonas_per_cluster + (1 if cluster_idx < remaining_osteonas else 0)
            
            # Posición central del cluster
            cluster_center_z = random.uniform(0, section["length_cm"])
            cluster_center_angle = random.uniform(0, 360)
            
            cluster_osteonas = []
            
            for i in range(cluster_size):
                # Generar posición relativa al centro del cluster
                offset_z = np.random.normal(0, section["length_cm"] * 0.1)
                offset_angle = np.random.normal(0, 30)  # 30 grados de dispersión
                
                pos_z = max(0, min(section["length_cm"], cluster_center_z + offset_z))
                angle = (cluster_center_angle + offset_angle) % 360
                
                # Aplicar orientación preferencial
                if section["orientation_strength"] > 0:
                    preferred_angle = section["orientation"]
                    strength = section["orientation_strength"]
                    
                    # Mezclar ángulo random con ángulo preferencial
                    angle = angle * (1 - strength) + preferred_angle * strength
                    angle = angle % 360
                
                # Tamaño con variación
                size_variation = 0.2 * section["variability"]
                size = section["osteona_size_um"] * (1 + random.uniform(-size_variation, size_variation))
                
                abs_pos_z = section["start_cm"] + pos_z
                
                osteona = {
                    "section_name": section["name"],
                    "position_z_cm": abs_pos_z,
                    "angle_degrees": angle,
                    "size_um": size,
                    "cluster_id": cluster_idx,
                    "is_clustered": True
                }
                
                cluster_osteonas.append(osteona)
            
            clusters.append(cluster_osteonas)
        
        return clusters
    
    def generate_single_osteona(self, section):
        """Genera una sola osteona con parámetros avanzados"""
        # Posición longitudinal
        pos_z = self.generate_position_advanced(0, section["length_cm"], section["variability"])
        
        # Ángulo con orientación preferencial
        if section["orientation_strength"] > 0:
            # Mezclar ángulo random con orientación preferencial
            random_angle = random.uniform(0, 360)
            preferred_angle = section["orientation"]
            strength = section["orientation_strength"]
            
            angle = random_angle * (1 - strength) + preferred_angle * strength
            angle = angle % 360
        else:
            angle = random.uniform(0, 360)
        
        # Tamaño con variación mejorada
        size_variation = 0.2 * section["variability"]
        size = section["osteona_size_um"] * (1 + random.uniform(-size_variation, size_variation))
        
        abs_pos_z = section["start_cm"] + pos_z
        
        return {
            "section_name": section["name"],
            "position_z_cm": abs_pos_z,
            "angle_degrees": angle,
            "size_um": size,
            "cluster_id": -1,
            "is_clustered": False
        }
    
    def generate_position_advanced(self, min_val, max_val, variability):
        """Generación de posición avanzada con más tipos de distribución"""
        if variability < 0.2:
            # Distribución muy uniforme
            return random.uniform(min_val, max_val)
        elif variability < 0.4:
            # Distribución normal centrada
            mean = (max_val + min_val) / 2
            std_dev = (max_val - min_val) / 8
            val = np.random.normal(mean, std_dev)
            return max(min_val, min(max_val, val))
        elif variability < 0.7:
            # Distribución beta (más realista para tejidos biológicos)
            alpha = 2
            beta = 2
            val = np.random.beta(alpha, beta)
            return min_val + val * (max_val - min_val)
        else:
            # Distribución multimodal (muy irregular)
            if random.random() < 0.6:  # 60% en los bordes
                if random.random() < 0.5:
                    return random.uniform(min_val, min_val + (max_val - min_val) * 0.3)
                else:
                    return random.uniform(max_val - (max_val - min_val) * 0.3, max_val)
            else:  # 40% en el centro
                center = (max_val + min_val) / 2
                return random.uniform(center - (max_val - min_val) * 0.2, center + (max_val - min_val) * 0.2)
    
    # MÉTODOS DE VISUALIZACIÓN MEJORADOS
    def update_visualization(self):
        """Visualización mejorada con 4 subplots"""
        if not self.sections_data or not self.distribution_data:
            return
        
        # Limpiar los ejes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
        
        # Subplot 1: Perfil del hueso con secciones (como antes)
        self.plot_bone_profile(self.ax1, colors)
        
        # Subplot 2: Distribución de osteonas con clustering
        self.plot_distribution_with_clusters(self.ax2, colors)
        
        # Subplot 3: Análisis de orientación
        self.plot_orientation_analysis(self.ax3)
        
        # Subplot 4: Distribución de tamaños
        self.plot_size_distribution(self.ax4, colors)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_bone_profile(self, ax, colors):
        """Grafica el perfil del hueso"""
        x_bone = np.linspace(0, self.sections_data["total_length_cm"], 1000)
        y_bone = np.zeros_like(x_bone)
        
        # Forma del fémur
        for i, x in enumerate(x_bone):
            rel_pos = x / self.sections_data["total_length_cm"]
            
            if rel_pos < 0.15:  # Epífisis proximal
                y_bone[i] = 2.5 * (1 - rel_pos/0.15) + 1
            elif rel_pos < 0.25:  # Metáfisis proximal
                y_bone[i] = 1 + (2.5 - 1) * (0.25 - rel_pos) / 0.1
            elif rel_pos < 0.75:  # Diáfisis
                y_bone[i] = 1
            elif rel_pos < 0.85:  # Metáfisis distal
                y_bone[i] = 1 + (3 - 1) * (rel_pos - 0.75) / 0.1
            else:  # Epífisis distal
                y_bone[i] = 3 + (rel_pos - 0.85) * 0.5 / 0.15
        
        ax.fill_between(x_bone, y_bone, -y_bone, color='#e0e0e0', alpha=0.5, label='Perfil del fémur')
        
        # Sombrear secciones
        current_pos = 0
        for i, section in enumerate(self.sections_data["sections"]):
            end_pos = section["end_cm"]
            section_mask = (x_bone >= current_pos) & (x_bone <= end_pos)
            
            ax.fill_between(x_bone[section_mask], y_bone[section_mask], -y_bone[section_mask], 
                           color=colors[i], alpha=0.7, label=section["name"])
            
            if current_pos > 0:
                ax.axvline(x=current_pos, color='black', linestyle='--', alpha=0.5)
            
            current_pos = end_pos
        
        ax.set_title('Perfil del Fémur y Secciones')
        ax.set_xlabel('Longitud (cm)')
        ax.set_ylabel('Ancho (cm)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8)
    
    def plot_distribution_with_clusters(self, ax, colors):
        """Grafica distribución con información de clustering"""
        positions = [osteona["position_z_cm"] for osteona in self.distribution_data]
        sizes = [osteona["size_um"] / 100 for osteona in self.distribution_data]
        is_clustered = [osteona["is_clustered"] for osteona in self.distribution_data]
        
        # Separar osteonas agrupadas y no agrupadas
        clustered_pos = [pos for pos, clustered in zip(positions, is_clustered) if clustered]
        unclustered_pos = [pos for pos, clustered in zip(positions, is_clustered) if not clustered]
        clustered_sizes = [size for size, clustered in zip(sizes, is_clustered) if clustered]
        unclustered_sizes = [size for size, clustered in zip(sizes, is_clustered) if not clustered]
        
        # Plotear por separado
        if unclustered_pos:
            ax.scatter(unclustered_pos, [0]*len(unclustered_pos), 
                      s=unclustered_sizes, alpha=0.6, c='blue', label='Osteonas distribuidas')
        
        if clustered_pos:
            ax.scatter(clustered_pos, [0.1]*len(clustered_pos), 
                      s=clustered_sizes, alpha=0.8, c='red', marker='^', label='Osteonas agrupadas')
        
        # Línea del hueso
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Líneas de separación de secciones
        for section in self.sections_data["sections"]:
            if section["start_cm"] > 0:
                ax.axvline(x=section["start_cm"], color='black', linestyle='--', alpha=0.5)
        
        ax.set_title('Distribución de Osteonas con Clustering')
        ax.set_xlabel('Posición Longitudinal (cm)')
        ax.set_ylabel('Nivel')
        ax.set_xlim(0, self.sections_data["total_length_cm"])
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7, axis='x')
    
    def plot_orientation_analysis(self, ax):
        """Análisis de orientación de osteonas"""
        angles = [osteona["angle_degrees"] for osteona in self.distribution_data]
        sections = [osteona["section_name"] for osteona in self.distribution_data]
        
        # Histograma circular usando bins de 30 grados
        bins = np.arange(0, 361, 30)
        hist, _ = np.histogram(angles, bins=bins)
        
        # Convertir a coordenadas polares
        theta = np.radians(bins[:-1] + 15)  # Centro de cada bin
        
        # Crear subplot polar
        ax.remove()
        ax = self.figure.add_subplot(2, 2, 3, projection='polar')
        self.ax3 = ax
        
        bars = ax.bar(theta, hist, width=np.radians(30), alpha=0.7, color='#BD0000')
        
        ax.set_title('Distribución de Orientaciones\n(Rosa de vientos)', pad=20)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
    
    def plot_size_distribution(self, ax, colors):
        """Distribución de tamaños por sección"""
        section_names = list(set([osteona["section_name"] for osteona in self.distribution_data]))
        
        for i, section_name in enumerate(section_names):
            sizes = [osteona["size_um"] for osteona in self.distribution_data 
                    if osteona["section_name"] == section_name]
            
            if sizes:
                ax.hist(sizes, bins=20, alpha=0.7, color=colors[i % len(colors)], 
                       label=section_name, density=True)
        
        ax.set_title('Distribución de Tamaños de Osteonas')
        ax.set_xlabel('Tamaño (μm)')
        ax.set_ylabel('Densidad')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def show_3d_visualization(self):
        """Muestra visualización 3D en ventana separada"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para visualizar.")
            return
        
        # Crear nueva ventana para 3D
        window_3d = tk.Toplevel(self.root)
        window_3d.title("Visualización 3D de Osteonas")
        window_3d.geometry("800x600")
        
        # Crear figura 3D
        from mpl_toolkits.mplot3d import Axes3D
        fig_3d = plt.figure(figsize=(12, 8))
        ax_3d = fig_3d.add_subplot(111, projection='3d')
        
        # Convertir coordenadas cilíndricas a cartesianas
        for osteona in self.distribution_data:
            z = osteona["position_z_cm"]
            angle_rad = np.radians(osteona["angle_degrees"])
            radius = 1.5  # Radio constante para visualización
            
            x = radius * np.cos(angle_rad)
            y = radius * np.sin(angle_rad)
            size = osteona["size_um"] / 50  # Escalar para visualización
            
            # Color por sección
            section_colors = {"Epífisis Proximal": 'red', "Metáfisis Proximal": 'blue', 
                            "Diáfisis": 'green', "Metáfisis Distal": 'orange', "Epífisis Distal": 'purple'}
            color = section_colors.get(osteona["section_name"], 'gray')
            
            ax_3d.scatter(x, y, z, s=size, c=color, alpha=0.6)
        
        ax_3d.set_xlabel('X (cm)')
        ax_3d.set_ylabel('Y (cm)')
        ax_3d.set_zlabel('Z - Posición Longitudinal (cm)')
        ax_3d.set_title('Distribución 3D de Osteonas en el Fémur')
        
        # Añadir canvas a la ventana
        canvas_3d = FigureCanvasTkAgg(fig_3d, master=window_3d)
        canvas_3d.get_tk_widget().pack(fill="both", expand=True)
        canvas_3d.draw()
    
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
            
            