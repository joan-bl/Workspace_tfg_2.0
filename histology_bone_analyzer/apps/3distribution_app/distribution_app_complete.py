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
        
        # Configurar directorio base actualizado
        self.base_dir = r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg_2.0\histology_bone_analyzer"
        self.ensure_directories()
        
        # Configurar estilo
        self.configure_style()
        
        # Variables básicas
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
        
        # Variables avanzadas
        self.orientation_epiphysis_proximal = tk.DoubleVar(value=0.0)
        self.orientation_metaphysis_proximal = tk.DoubleVar(value=0.0)
        self.orientation_diaphysis = tk.DoubleVar(value=0.0)
        self.orientation_metaphysis_distal = tk.DoubleVar(value=0.0)
        self.orientation_epiphysis_distal = tk.DoubleVar(value=0.0)
        
        self.orientation_strength_epiphysis_proximal = tk.DoubleVar(value=0.2)
        self.orientation_strength_metaphysis_proximal = tk.DoubleVar(value=0.4)
        self.orientation_strength_diaphysis = tk.DoubleVar(value=0.8)
        self.orientation_strength_metaphysis_distal = tk.DoubleVar(value=0.4)
        self.orientation_strength_epiphysis_distal = tk.DoubleVar(value=0.2)
        
        self.clustering_factor_epiphysis_proximal = tk.DoubleVar(value=0.3)
        self.clustering_factor_metaphysis_proximal = tk.DoubleVar(value=0.2)
        self.clustering_factor_diaphysis = tk.DoubleVar(value=0.1)
        self.clustering_factor_metaphysis_distal = tk.DoubleVar(value=0.2)
        self.clustering_factor_epiphysis_distal = tk.DoubleVar(value=0.3)
        
        # Variables de simulación
        self.simulation_mode = tk.StringVar(value="normal")
        self.age_factor = tk.DoubleVar(value=1.0)
        self.pathology_factor = tk.DoubleVar(value=1.0)
        
        # Datos calculados
        self.sections_data = None
        self.distribution_data = None
        self.analysis_results = None
        
        # Crear la interfaz
        self.create_ui()
        
        # Calcular inicialmente
        self.calculate()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ============================================================================
    # FUNCIONES DE CIERRE CORRECTO DE LA APLICACIÓN
    # ============================================================================

    def on_closing(self):
        """
        Maneja el cierre correcto de la aplicación Distribution App.
        Libera recursos y permite que la terminal vuelva a estar disponible.
        """
        try:
            # Confirmar cierre si hay trabajo en progreso
            if hasattr(self, 'distribution_data') and self.distribution_data:
                if messagebox.askokcancel("Salir", 
                                        "¿Está seguro de que desea salir?\n"
                                        "Los datos no guardados se perderán."):
                    self._cleanup_and_exit()
                else:
                    return  # Usuario canceló el cierre
            else:
                self._cleanup_and_exit()
        except Exception as e:
            print(f"Error durante el cierre: {e}")
            # Forzar cierre incluso si hay error
            self._force_exit()

    def _cleanup_and_exit(self):
        """
        Limpia recursos y cierra la aplicación correctamente.
        """
        try:
            # Limpiar figuras de matplotlib para evitar warnings
            if hasattr(self, 'figure'):
                plt.close(self.figure)
            
            # Limpiar cualquier ventana adicional abierta
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            
            # Cerrar ventana principal
            self.root.quit()      # Sale del mainloop
            self.root.destroy()   # Destruye la ventana
            
            print("Distribution App cerrada correctamente.")
            
        except Exception as e:
            print(f"Error en cleanup: {e}")
            self._force_exit()

    def _force_exit(self):
        """
        Fuerza el cierre de la aplicación en caso de error.
        """
        try:
            self.root.quit()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass
        
        # Como último recurso, usar sys.exit()
        import sys
        sys.exit(0)
    
    def ensure_directories(self):
        """Asegura que existan los directorios necesarios"""
        directories = [
            os.path.join(self.base_dir, "data", "sample_results", "distribution_app"),
            os.path.join(self.base_dir, "docs", "technical")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
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
        """Interfaz mejorada con 6 pestañas"""
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
        """Pestaña de parámetros básicos"""
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
        """Pestaña de parámetros avanzados"""
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
        """Pestaña para simulación de condiciones patológicas"""
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
        """Pestaña de visualización"""
        # Marco para controles de visualización
        controls_frame = ttk.Frame(self.tab_visualization)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Botones de visualización
        ttk.Button(controls_frame, text="Actualizar Visualización", command=self.update_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Guardar Imagen", command=self.save_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Vista 3D", command=self.show_3d_visualization).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Análisis Estadístico", command=self.show_statistical_analysis).pack(side="left", padx=5)
        
        # Crear figura con subplots
        self.figure, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        self.figure.tight_layout(pad=3.0)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tab_visualization)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
    
    def setup_analysis_tab(self):
        """Pestaña para análisis avanzado"""
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
        """Pestaña de exportación"""
        # Marco para opciones de exportación
        export_frame = ttk.LabelFrame(self.tab_export, text="Opciones de Exportación")
        export_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Botones de exportación
        export_buttons = [
            ("Exportar CSV (Grasshopper)", lambda: self.export_data("csv")),
            ("Exportar JSON Completo", lambda: self.export_data("json")),
            ("Informe Completo TXT", self.export_report_txt)
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
        
        # Área de previsualización
        preview_frame = ttk.LabelFrame(self.tab_export, text="Previsualización de Datos")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=15, width=80)
        preview_scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scrollbar.pack(side="right", fill="y")
    
    # ============================================================================
    # MÉTODOS DE SIMULACIÓN Y PRESETS
    # ============================================================================
    
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
        
        self.update_simulation_info()
    
    def preset_young_healthy(self):
        """Preset para hueso joven sano"""
        self.age_factor.set(0.6)
        self.pathology_factor.set(0.9)
        self.simulation_mode.set("normal")
        
        # Aumentar densidades
        self.density_diaphysis.set(75.0)
        self.density_metaphysis_proximal.set(50.0)
        self.density_metaphysis_distal.set(50.0)
        
        # Reducir tamaños
        self.osteona_size_diaphysis.set(140.0)
        self.osteona_size_metaphysis_proximal.set(170.0)
        self.osteona_size_metaphysis_distal.set(170.0)
        
        # Reducir variabilidad
        self.variability_diaphysis.set(0.2)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_adult_normal(self):
        """Preset para hueso adulto normal"""
        self.age_factor.set(1.0)
        self.pathology_factor.set(1.0)
        self.simulation_mode.set("normal")
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_aged(self):
        """Preset para hueso envejecido"""
        self.age_factor.set(1.8)
        self.pathology_factor.set(1.2)
        self.simulation_mode.set("aging")
        
        # Reducir densidades
        self.density_diaphysis.set(45.0)
        self.density_metaphysis_proximal.set(30.0)
        self.density_metaphysis_distal.set(30.0)
        
        # Aumentar tamaños
        self.osteona_size_diaphysis.set(180.0)
        self.osteona_size_metaphysis_proximal.set(220.0)
        self.osteona_size_metaphysis_distal.set(220.0)

        # Aumentar variabilidad
        self.variability_diaphysis.set(0.5)
        self.variability_metaphysis_proximal.set(0.7)
        self.variability_metaphysis_distal.set(0.7)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_osteoporosis_early(self):
        """Preset para osteoporosis temprana"""
        self.age_factor.set(1.4)
        self.pathology_factor.set(1.5)
        self.simulation_mode.set("pathological")
        
        # Reducir densidades moderadamente
        self.density_diaphysis.set(40.0)
        self.density_metaphysis_proximal.set(25.0)
        self.density_metaphysis_distal.set(25.0)
        self.density_epiphysis_proximal.set(18.0)
        self.density_epiphysis_distal.set(18.0)
        
        # Aumentar tamaños
        self.osteona_size_diaphysis.set(190.0)
        self.osteona_size_epiphysis_proximal.set(250.0)
        self.osteona_size_epiphysis_distal.set(250.0)
        
        # Aumentar variabilidad significativamente
        self.variability_epiphysis_proximal.set(0.8)
        self.variability_metaphysis_proximal.set(0.7)
        self.variability_diaphysis.set(0.6)
        self.variability_metaphysis_distal.set(0.7)
        self.variability_epiphysis_distal.set(0.8)
        
        self.calculate()
        self.update_simulation_info()
    
    def preset_osteoporosis_advanced(self):
        """Preset para osteoporosis avanzada"""
        self.age_factor.set(2.0)
        self.pathology_factor.set(1.8)
        self.simulation_mode.set("pathological")
        
        # Reducir densidades severamente
        self.density_diaphysis.set(30.0)
        self.density_metaphysis_proximal.set(18.0)
        self.density_metaphysis_distal.set(18.0)
        self.density_epiphysis_proximal.set(12.0)
        self.density_epiphysis_distal.set(12.0)
        
        # Aumentar tamaños considerablemente
        self.osteona_size_diaphysis.set(210.0)
        self.osteona_size_metaphysis_proximal.set(240.0)
        self.osteona_size_metaphysis_distal.set(240.0)
        self.osteona_size_epiphysis_proximal.set(280.0)
        self.osteona_size_epiphysis_distal.set(280.0)
        
        # Máxima variabilidad
        for var in [self.variability_epiphysis_proximal, self.variability_metaphysis_proximal,
                   self.variability_diaphysis, self.variability_metaphysis_distal, 
                   self.variability_epiphysis_distal]:
            var.set(0.9)
        
        # Aumentar clustering (agrupamiento patológico)
        self.clustering_factor_epiphysis_proximal.set(0.6)
        self.clustering_factor_metaphysis_proximal.set(0.5)
        self.clustering_factor_diaphysis.set(0.4)
        self.clustering_factor_metaphysis_distal.set(0.5)
        self.clustering_factor_epiphysis_distal.set(0.6)
        
        self.calculate()
        self.update_simulation_info()
    
    def update_simulation_info(self):
        """Actualiza la información de simulación"""
        self.sim_info_text.delete(1.0, tk.END)
        
        info_text = f"""CONFIGURACIÓN ACTUAL DE SIMULACIÓN
{'='*50}

Modo de simulación: {self.simulation_mode.get().upper()}
Factor de edad: {self.age_factor.get():.2f}
Factor patológico: {self.pathology_factor.get():.2f}

INTERPRETACIÓN:
"""
        
        age_factor = self.age_factor.get()
        pathology_factor = self.pathology_factor.get()
        
        if age_factor < 0.8:
            info_text += "• Patrón microestructural compatible con hueso joven\n"
            info_text += "• Características: alta densidad osteonal, organización regular\n"
            info_text += "• Propiedades mecánicas óptimas esperadas\n"
        elif age_factor > 1.5:
            info_text += "• Patrón microestructural compatible con envejecimiento óseo\n"
            info_text += "• Características: reducción de densidad, aumento de tamaño de canales\n"
            info_text += "• Recomendación: monitoreo de fragilidad ósea\n"
        else:
            info_text += "• Patrón microestructural de hueso adulto normal\n"
            info_text += "• Características dentro de rangos de referencia\n"
        
        if pathology_factor > 1.3:
            info_text += "• Alteraciones microestructurales significativas detectadas\n"
            info_text += "• Posible compromiso de la integridad mecánica\n"
            info_text += "• Recomendación: evaluación clínica especializada\n"
        
        self.sim_info_text.insert(tk.END, info_text)
    
    # ============================================================================
    # MÉTODOS DE CÁLCULO PRINCIPAL
    # ============================================================================
    
    def calculate(self):
        """Método principal de cálculo"""
        try:
            # Calcular longitudes de secciones
            total_length = self.femur_length.get()
            
            sections = []
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
            
            current_z = 0
            for name, percent_var, density_var, size_var, var_var, orient_var, orient_str_var, cluster_var in section_vars:
                percent = percent_var.get() / 100.0
                length_cm = total_length * percent
                
                section_data = {
                    'name': name,
                    'percent': percent_var.get(),
                    'length_cm': length_cm,
                    'start_z': current_z,
                    'end_z': current_z + length_cm,
                    'density_per_cm2': density_var.get(),
                    'size_um': size_var.get(),
                    'variability': var_var.get(),
                    'orientation': orient_var.get(),
                    'orientation_strength': orient_str_var.get(),
                    'clustering': cluster_var.get()
                }
                
                sections.append(section_data)
                current_z += length_cm
            
            # Aplicar factores de simulación
            age_factor = self.age_factor.get()
            pathology_factor = self.pathology_factor.get()
            
            for section in sections:
                # Aplicar efectos del envejecimiento
                if age_factor != 1.0:
                    section['density_per_cm2'] *= (2.0 - age_factor)
                    section['size_um'] *= age_factor
                    section['variability'] = min(1.0, section['variability'] * age_factor)
                
                # Aplicar efectos patológicos
                if pathology_factor != 1.0:
                    section['density_per_cm2'] *= (2.0 - pathology_factor * 0.5)
                    section['size_um'] *= pathology_factor
                    section['variability'] = min(1.0, section['variability'] * pathology_factor)
                    section['clustering'] = min(1.0, section['clustering'] * pathology_factor)
            
            self.sections_data = {
                'total_length_cm': total_length,
                'sections': sections,
                'simulation_mode': self.simulation_mode.get(),
                'age_factor': age_factor,
                'pathology_factor': pathology_factor
            }
            
            # Generar distribución de osteonas
            self.generate_osteona_distribution()
            
            # Mostrar resultados
            self.display_results()
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {str(e)}")
    
    def generate_osteona_distribution(self):
        """Genera la distribución de osteonas"""
        if not self.sections_data:
            return
        
        all_osteonas = []
        
        for section in self.sections_data['sections']:
            # Calcular número de osteonas para esta sección
            area_section = section['length_cm'] * 3.0  # Asumiendo 3cm de ancho
            num_osteonas = int(area_section * section['density_per_cm2'])
            
            section_osteonas = []
            
            # Generar clusters si el factor es alto
            if section['clustering'] > 0.3:
                num_clusters = max(1, int(num_osteonas * section['clustering'] * 0.1))
                osteonas_per_cluster = num_osteonas // (num_clusters + 1)
                
                # Generar centros de cluster
                cluster_centers = []
                for _ in range(num_clusters):
                    cluster_z = random.uniform(section['start_z'], section['end_z'])
                    cluster_centers.append(cluster_z)
                
                # Generar osteonas agrupadas
                clustered_count = 0
                for center_z in cluster_centers:
                    for _ in range(osteonas_per_cluster):
                        if clustered_count >= num_osteonas:
                            break
                        
                        # Posición cerca del centro del cluster
                        pos_z = np.random.normal(center_z, section['length_cm'] * 0.1)
                        pos_z = max(section['start_z'], min(section['end_z'], pos_z))
                        
                        osteona = self.create_osteona(section, pos_z, is_clustered=True)
                        section_osteonas.append(osteona)
                        clustered_count += 1
                
                # Generar osteonas dispersas restantes
                remaining = num_osteonas - clustered_count
                for _ in range(remaining):
                    pos_z = random.uniform(section['start_z'], section['end_z'])
                    osteona = self.create_osteona(section, pos_z, is_clustered=False)
                    section_osteonas.append(osteona)
            else:
                # Distribución uniforme
                for _ in range(num_osteonas):
                    pos_z = random.uniform(section['start_z'], section['end_z'])
                    osteona = self.create_osteona(section, pos_z, is_clustered=False)
                    section_osteonas.append(osteona)
            
            all_osteonas.extend(section_osteonas)
        
        self.distribution_data = all_osteonas
    
    def create_osteona(self, section, position_z, is_clustered=False):
        """Crea una osteona individual"""
        # Generar tamaño según variabilidad
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
        
        size = max(50, min(400, size))  # Límites realistas
        
        # Generar orientación
        base_orientation = section['orientation']
        orientation_strength = section['orientation_strength']
        
        if orientation_strength > 0.1:
            # Von Mises distribution para orientación preferencial
            concentration = orientation_strength * 10
            angle = np.random.vonmises(np.radians(base_orientation), concentration)
            angle_degrees = np.degrees(angle) % 360
        else:
            # Orientación aleatoria
            angle_degrees = random.uniform(0, 360)
        
        return {
            'section_name': section['name'],
            'position_z_cm': position_z,
            'angle_degrees': angle_degrees,
            'size_um': size,
            'is_clustered': is_clustered,
            'cluster_id': random.randint(1, 10) if is_clustered else None
        }
    
    # ============================================================================
    # MÉTODOS DE VISUALIZACIÓN
    # ============================================================================
    
    def update_visualization(self):
        """Actualiza todas las visualizaciones"""
        if not self.sections_data or not self.distribution_data:
            return
        
        # Limpiar subplots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        # Gráfico 1: Perfil del fémur con secciones
        self.plot_femur_profile()
        
        # Gráfico 2: Distribución de osteonas
        self.plot_osteona_distribution()
        
        # Gráfico 3: Análisis de orientación
        self.plot_orientation_analysis()
        
        # Gráfico 4: Distribución de tamaños
        self.plot_size_distribution()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_femur_profile(self):
        """Gráfico del perfil del fémur"""
        sections = self.sections_data['sections']
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        
        # Dibujar secciones
        for i, section in enumerate(sections):
            self.ax1.barh(1, section['length_cm'], left=section['start_z'], 
                         height=0.5, color=colors[i % len(colors)], alpha=0.7, 
                         label=section['name'])
        
        self.ax1.set_xlabel('Posición (cm)')
        self.ax1.set_ylabel('Sección del Fémur')
        self.ax1.set_title('Perfil Anatómico del Fémur')
        self.ax1.set_ylim(0.5, 1.5)
        self.ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    def plot_osteona_distribution(self):
        """Gráfico de distribución de osteonas"""
        df = pd.DataFrame(self.distribution_data)
        
        # Separar osteonas agrupadas y dispersas
        clustered = df[df['is_clustered'] == True]
        dispersed = df[df['is_clustered'] == False]
        
        # Scatter plot
        if not dispersed.empty:
            self.ax2.scatter(dispersed['position_z_cm'], dispersed['size_um'], 
                           c='red', marker='o', s=20, alpha=0.6, label='Dispersas')
        
        if not clustered.empty:
            self.ax2.scatter(clustered['position_z_cm'], clustered['size_um'], 
                           c='blue', marker='s', s=20, alpha=0.8, label='Agrupadas')
        
        self.ax2.set_xlabel('Posición (cm)')
        self.ax2.set_ylabel('Tamaño (μm)')
        self.ax2.set_title('Distribución de Osteonas')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
    
    def plot_orientation_analysis(self):
        """Gráfico de análisis de orientación (rosa de vientos)"""
        df = pd.DataFrame(self.distribution_data)
        
        # Convertir a radianes
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
        
        # Colorear barras
        if hist.max() > 0:
            colors = plt.cm.viridis(hist / hist.max())
            for bar, color in zip(bars, colors):
                bar.set_color(color)
        
        self.ax3.set_title('Rosa de Orientaciones', pad=20)
        self.ax3.set_theta_zero_location('N')
        self.ax3.set_theta_direction(-1)
    
    def plot_size_distribution(self):
        """Gráfico de distribución de tamaños por sección"""
        df = pd.DataFrame(self.distribution_data)
        
        # Histograma por sección
        sections = df['section_name'].unique()
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        
        for i, section in enumerate(sections):
            section_data = df[df['section_name'] == section]
            self.ax4.hist(section_data['size_um'], bins=15, alpha=0.6, 
                         color=colors[i % len(colors)], label=section)
        
        self.ax4.set_xlabel('Tamaño (μm)')
        self.ax4.set_ylabel('Frecuencia')
        self.ax4.set_title('Distribución de Tamaños por Sección')
        self.ax4.legend(fontsize=8)
        self.ax4.grid(True, alpha=0.3)
    
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
    
    def show_3d_visualization(self):
        """Muestra visualización 3D en ventana separada"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para visualizar.")
            return
        
        try:
            # Crear ventana 3D
            viz_3d_window = tk.Toplevel(self.root)
            viz_3d_window.title("Visualización 3D - Distribución de Osteonas")
            viz_3d_window.geometry("800x600")
            
            # Crear figura 3D
            fig_3d = plt.figure(figsize=(10, 8))
            ax_3d = fig_3d.add_subplot(111, projection='3d')
            
            df = pd.DataFrame(self.distribution_data)
            
            # Generar coordenadas aleatorias para visualización 3D
            y_coords = np.random.uniform(-1.5, 1.5, len(df))
            x_coords = np.random.uniform(-1.5, 1.5, len(df))
            
            # Scatter 3D
            scatter = ax_3d.scatter(x_coords, y_coords, df['position_z_cm'], 
                                  c=df['size_um'], cmap='viridis', 
                                  s=df['size_um']/5, alpha=0.6)
            
            ax_3d.set_xlabel('X (cm)')
            ax_3d.set_ylabel('Y (cm)')
            ax_3d.set_zlabel('Posición Z (cm)')
            ax_3d.set_title('Distribución 3D de Osteonas')
            
            # Colorbar
            cbar = plt.colorbar(scatter, ax=ax_3d, shrink=0.5)
            cbar.set_label('Tamaño (μm)')
            
            # Integrar con tkinter
            canvas_3d = FigureCanvasTkAgg(fig_3d, master=viz_3d_window)
            canvas_3d.get_tk_widget().pack(fill="both", expand=True)
            canvas_3d.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en visualización 3D: {str(e)}")
    
    def show_statistical_analysis(self):
        """Muestra análisis estadístico detallado"""
        if not self.distribution_data:
            messagebox.showwarning("Advertencia", "No hay datos para analizar.")
            return
        
        try:
            # Crear ventana de análisis estadístico
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Análisis Estadístico Avanzado")
            stats_window.geometry("1000x700")
            
            # Área de texto para estadísticas
            stats_text = tk.Text(stats_window, height=30, width=80)
            stats_scrollbar = ttk.Scrollbar(stats_window, command=stats_text.yview)
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
            
            stats_text.insert(tk.END, stats_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis estadístico: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE ANÁLISIS BIOMECÁNICO
    # ============================================================================
    
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
            
            # Estimación de propiedades mecánicas
            relative_density = 1 - (porosity / 100)
            estimated_modulus = 20000 * (relative_density ** 2.5)  # MPa
            analysis_content += f"Módulo elástico estimado: {estimated_modulus:.0f} MPa\n"
            
            estimated_strength = 137 * (relative_density ** 1.8)  # MPa
            analysis_content += f"Resistencia estimada: {estimated_strength:.0f} MPa\n"
            
            analysis_content += "\n"
        
        self.analysis_text.insert(tk.END, analysis_content)
    
    def analyze_distribution_patterns(self):
        """Analiza patrones de distribución espacial"""
        if not self.distribution_data:
            return
        
        self.analysis_text.delete(1.0, tk.END)
        
        df = pd.DataFrame(self.distribution_data)
        
        content = "ANÁLISIS DE PATRONES DE DISTRIBUCIÓN\n"
        content += "=" * 40 + "\n\n"
        
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
        
        try:
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
        except ImportError:
            content += "Análisis de correlación no disponible (scipy no encontrado)\n"
        
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
            "densidad_diafisis": len(diaphysis_data) / (self.sections_data['sections'][2]['length_cm'] * 3),
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
        
        return report
    
    # ============================================================================
    # MÉTODOS DE EXPORTACIÓN
    # ============================================================================
    
    def export_data(self, format_type):
        """Método de exportación básico"""
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
            
            messagebox.showinfo("Éxito", f"Datos exportados correctamente:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos:\n{str(e)}")
    
    def export_report_txt(self):
        """Exporta reporte como texto plano"""
        if not hasattr(self, 'current_report_text'):
            self.current_report_text = self.generate_comprehensive_report()
        
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
    
    # ============================================================================
    # MÉTODOS DE VISUALIZACIÓN Y ACTUALIZACIÓN
    # ============================================================================
    
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
        
        self.preview_text.insert(tk.END, preview_text)

# ============================================================================
# FUNCIÓN PRINCIPAL PARA EJECUTAR LA APLICACIÓN
# ============================================================================

def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = FemurOsteonaDistributorAdvanced(root)
    
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
    main()