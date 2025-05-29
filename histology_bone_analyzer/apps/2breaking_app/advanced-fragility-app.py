import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from PIL import Image, ImageTk
import os
from datetime import datetime
from pathlib import Path
import logging

class AdvancedBoneFragilityAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Havers Analisis - Advanced Fragility Assessment")
        self.root.configure(bg='#000000')
        self.root.geometry("1400x900")
        
        # SOLUCIÓN 1: Configurar el cierre correcto de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar directorios usando rutas relativas
        self.setup_directories()
        
        # Variables para datos
        self.imagen_original = None
        self.datos_canales = None
        self.resultados_analisis = None
        self.matriz_filas = 9  # Matriz más grande por defecto (9x9)
        self.matriz_cols = 9
        
        # Coeficientes del modelo avanzado (configurables)
        self.coeficientes = {
            'w1': 1.0,
            'w2': 0.5,
            'w3': 0.3,
            'w4': 0.2
        }
        
        self.setup_ui()
    
    def on_closing(self):
        """SOLUCIÓN 1: Maneja el cierre correcto de la aplicación"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
    def setup_directories(self):
        """Configura los directorios del proyecto de forma consistente."""
        try:
            # Detectar la ruta base del proyecto (ahora Workspace_tfg_2.0)
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            
            # Todo va directamente a breaking_app/ (sin subcarpetas)
            self.base_dir = project_root / "data" / "sample_results" / "breaking_app"
            self.results_dir = self.base_dir  # Mismo directorio, sin subcarpeta
            
            # Crear directorio si no existe
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"Directorio configurado: {self.base_dir}")
            
        except Exception as e:
            logging.error(f"Error configurando directorios: {e}")
            # Fallback a directorio actual
            self.base_dir = Path.cwd() / "breaking_app_results"
            self.results_dir = self.base_dir
            
            self.base_dir.mkdir(exist_ok=True)
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="Advanced Bone Fragility Analysis",
                              font=("Helvetica", 24, "bold"),
                              fg='white', bg='#000000')
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas (SOLUCIÓN 4: Solo 3 pestañas ahora)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configurar estilo para el notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#000000')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
        # Crear pestañas (eliminamos la pestaña de análisis)
        self.setup_config_tab()
        self.setup_visualization_tab()
        self.setup_results_tab()
        
    def setup_config_tab(self):
        """Configura la pestaña de configuración"""
        config_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(config_frame, text="Configuración")
        
        # Frame para configuración de parámetros
        param_frame = tk.LabelFrame(config_frame, text="Parámetros del Modelo",
                                   fg='white', bg='#000000', font=("Helvetica", 12))
        param_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Configuración de coeficientes
        coef_labels = {
            'w1': 'Peso base (Área × log(N))',
            'w2': 'Peso heterogeneidad tamaño',
            'w3': 'Peso densidad conectividad',
            'w4': 'Peso anisotropía orientación'
        }
        
        self.coef_vars = {}
        for i, (coef, desc) in enumerate(coef_labels.items()):
            tk.Label(param_frame, text=desc, fg='white', bg='#000000').grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            
            var = tk.DoubleVar(value=self.coeficientes[coef])
            self.coef_vars[coef] = var
            
            spinbox = tk.Spinbox(param_frame, from_=0.0, to=2.0, increment=0.1,
                               textvariable=var, width=10)
            spinbox.grid(row=i, column=1, padx=10, pady=5)
        
        # Configuración de matriz
        matrix_frame = tk.LabelFrame(config_frame, text="Configuración de Matriz",
                                   fg='white', bg='#000000', font=("Helvetica", 12))
        matrix_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(matrix_frame, text="Resolución de matriz:", 
                fg='white', bg='#000000').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.matrix_var = tk.StringVar(value="9x9")
        matrix_combo = ttk.Combobox(matrix_frame, textvariable=self.matrix_var,
                                   values=["6x6", "9x9", "12x12", "15x15"])
        matrix_combo.grid(row=0, column=1, padx=10, pady=5)
        matrix_combo.bind('<<ComboboxSelected>>', self.on_matrix_change)
        
        # Botones de carga
        load_frame = tk.Frame(config_frame, bg='#000000')
        load_frame.pack(fill=tk.X, padx=20, pady=20)
        
        load_btn = tk.Button(load_frame, text="Cargar Imagen y Datos Excel",
                           command=self.cargar_datos, bg='#BD0000', fg='white',
                           font=("Helvetica", 12), height=2)
        load_btn.pack(fill=tk.X, pady=10)
        
        # SOLUCIÓN 4: Botón de análisis movido aquí desde la pestaña eliminada
        analyze_btn = tk.Button(load_frame, text="Ejecutar Análisis Avanzado",
                              command=self.ejecutar_analisis_avanzado,
                              bg='#BD0000', fg='white', font=("Helvetica", 14),
                              height=3)
        analyze_btn.pack(fill=tk.X, pady=10)
        
        # Frame para mostrar progreso
        self.progress_frame = tk.Frame(config_frame, bg='#000000')
        self.progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="",
                                     fg='white', bg='#000000', font=("Helvetica", 12))
        self.progress_label.pack()

    def setup_visualization_tab(self):
        """Configura la pestaña de visualización"""
        viz_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(viz_frame, text="Visualización")
        
        # SOLUCIÓN 2: Botones FUERA del canvas para que siempre estén visibles
        self.viz_controls = tk.Frame(viz_frame, bg='#000000')
        self.viz_controls.pack(fill=tk.X, padx=20, pady=10)
        
        btn_heatmap = tk.Button(self.viz_controls, text="Mapa de Calor Fragilidad",
                              command=self.mostrar_mapa_calor,
                              bg='#BD0000', fg='white')
        btn_heatmap.pack(side=tk.LEFT, padx=5)
        
        btn_connectivity = tk.Button(self.viz_controls, text="Visualizar Conectividad",
                                   command=self.mostrar_conectividad,
                                   bg='#BD0000', fg='white')
        btn_connectivity.pack(side=tk.LEFT, padx=5)
        
        btn_anisotropy = tk.Button(self.viz_controls, text="Análisis Anisotropía",
                                 command=self.mostrar_anisotropia,
                                 bg='#BD0000', fg='white')
        btn_anisotropy.pack(side=tk.LEFT, padx=5)
        
        # Frame para canvas de matplotlib SEPARADO de los botones
        self.viz_canvas_frame = tk.Frame(viz_frame, bg='#000000')
        self.viz_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_results_tab(self):
        """Configura la pestaña de resultados"""
        results_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(results_frame, text="Resultados")
        
        # Frame para texto de resultados
        text_frame = tk.Frame(results_frame, bg='#000000')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Texto con scrollbar
        self.results_text = tk.Text(text_frame, bg='#222222', fg='white',
                                  font=("Consolas", 10), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                               command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de exportación
        export_frame = tk.Frame(results_frame, bg='#000000')
        export_frame.pack(fill=tk.X, padx=20, pady=10)
        
        export_excel_btn = tk.Button(export_frame, text="Exportar a Excel",
                                    command=self.exportar_excel,
                                    bg='#BD0000', fg='white')
        export_excel_btn.pack(side=tk.LEFT, padx=5)
        
        export_report_btn = tk.Button(export_frame, text="Generar Informe Completo",
                                    command=self.generar_informe,
                                    bg='#BD0000', fg='white')
        export_report_btn.pack(side=tk.LEFT, padx=5)
        
    def on_matrix_change(self, event=None):
        """SOLUCIÓN 3: Maneja el cambio en la configuración de matriz y limpia resultados"""
        matrix_size = self.matrix_var.get()
        size = int(matrix_size.split('x')[0])
        self.matriz_filas = self.matriz_cols = size
        
        # Limpiar resultados anteriores para forzar recálculo
        self.resultados_analisis = None
        self.progress_label.config(text="Configuración cambiada. Ejecute el análisis nuevamente.")
        
        # Limpiar visualizaciones
        self.limpiar_visualizaciones()
        
    def cargar_datos(self):
        """Carga la imagen y los datos de Excel"""
        try:
            # Seleccionar imagen
            imagen_path = filedialog.askopenfilename(
                title="Seleccionar imagen histológica",
                filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.tiff *.tif")]
            )
            if not imagen_path:
                return
                
            # Seleccionar Excel
            excel_path = filedialog.askopenfilename(
                title="Seleccionar archivo Excel con detecciones",
                filetypes=[("Excel", "*.xlsx *.xls")]
            )
            if not excel_path:
                return
                
            # Cargar imagen
            self.imagen_original = cv2.imread(imagen_path)
            if self.imagen_original is None:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
                return
            self.imagen_original = cv2.cvtColor(self.imagen_original, cv2.COLOR_BGR2RGB)
            
            # Cargar datos de Excel
            self.datos_canales = pd.read_excel(excel_path)
            
            # Validar columnas necesarias
            required_cols = ['Center X', 'Center Y', 'Ellipse Area (pixels^2)']
            # Intentar con nombres alternativos
            if 'X' in self.datos_canales.columns and 'Y' in self.datos_canales.columns:
                self.datos_canales['Center X'] = self.datos_canales['X']
                self.datos_canales['Center Y'] = self.datos_canales['Y']
            if 'Area' in self.datos_canales.columns:
                self.datos_canales['Ellipse Area (pixels^2)'] = self.datos_canales['Area']
                
            # Verificar que tengamos las columnas necesarias
            missing_cols = [col for col in required_cols if col not in self.datos_canales.columns]
            if missing_cols:
                messagebox.showerror("Error", f"El archivo Excel debe contener columnas: {', '.join(missing_cols)}")
                return
                
            messagebox.showinfo("Éxito", f"Datos cargados correctamente:\n"
                               f"Imagen: {os.path.basename(imagen_path)}\n"
                               f"Canales detectados: {len(self.datos_canales)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            logging.error(f"Error cargando datos: {e}")
    
    def calcular_densidad_conectividad(self, coordenadas):
        """Calcula la densidad de conectividad para un conjunto de canales"""
        n = len(coordenadas)
        if n < 2:
            return 0
        
        suma_inversos = 0
        total_pares = 0
        
        for i in range(n):
            for j in range(i+1, n):
                x1, y1 = coordenadas[i]
                x2, y2 = coordenadas[j]
                dist_squared = (x2-x1)**2 + (y2-y1)**2
                
                if dist_squared > 0:
                    suma_inversos += 1 / dist_squared
                    total_pares += 1
        
        if total_pares == 0:
            return 0
        
        return suma_inversos / total_pares
    
    def calcular_anisotropia_orientacion(self, coordenadas):
        """Calcula la anisotropía de orientación usando análisis estadístico"""
        if len(coordenadas) < 5:
            return 0
        
        # Convertir a array numpy
        coords = np.array(coordenadas)
        
        # Calcular orientaciones usando diferencias de coordenadas vecinas
        orientaciones = []
        for i in range(len(coords)):
            if i < len(coords) - 1:
                dx = coords[i+1][0] - coords[i][0]
                dy = coords[i+1][1] - coords[i][1]
                if dx != 0 or dy != 0:
                    angle = math.atan2(dy, dx)
                    # Normalizar al rango [0, π]
                    orientaciones.append(abs(angle) % math.pi)
        
        if len(orientaciones) < 3:
            return 0
        
        # Calcular desviación estándar
        std_orientaciones = np.std(orientaciones)
        max_std = math.pi / math.sqrt(12)  # Máxima desviación para distribución uniforme
        
        return min(std_orientaciones / max_std, 1.0)  # Normalizar entre 0 y 1
    
    def calcular_fragilidad_avanzada(self, canales_cuadrante):
        """Calcula la fragilidad usando el modelo avanzado"""
        n = len(canales_cuadrante)
        if n < 6:
            return 0, {}  # Insuficientes canales
        
        # Extraer datos
        areas = canales_cuadrante['Ellipse Area (pixels^2)'].values
        coordenadas = list(zip(canales_cuadrante['Center X'].values, 
                             canales_cuadrante['Center Y'].values))
        
        # Actualizar coeficientes desde la UI
        for coef in self.coeficientes:
            self.coeficientes[coef] = self.coef_vars[coef].get()
        
        # Calcular componentes
        area_promedio = np.mean(areas)
        factor_tamano = np.max(areas) / area_promedio if area_promedio > 0 else 1
        densidad_conectividad = self.calcular_densidad_conectividad(coordenadas)
        anisotropia = self.calcular_anisotropia_orientacion(coordenadas)
        
        # Aplicar fórmula avanzada
        w1, w2, w3, w4 = (self.coeficientes['w1'], self.coeficientes['w2'], 
                          self.coeficientes['w3'], self.coeficientes['w4'])
        
        termino_base = w1 * (area_promedio * math.log(n))
        termino_tamano = 1 + w2 * (factor_tamano - 1)
        termino_conectividad = max(0.1, 1 - w3 * densidad_conectividad)  # Evitar valores negativos
        termino_anisotropia = 1 + w4 * anisotropia
        
        fragilidad = termino_base * termino_tamano * termino_conectividad * termino_anisotropia
        
        # Información detallada
        detalles = {
            'area_promedio': area_promedio,
            'factor_tamano': factor_tamano,
            'densidad_conectividad': densidad_conectividad,
            'anisotropia': anisotropia,
            'termino_base': termino_base,
            'termino_tamano': termino_tamano,
            'termino_conectividad': termino_conectividad,
            'termino_anisotropia': termino_anisotropia,
            'numero_canales': n
        }
        
        return fragilidad, detalles
    
    def ejecutar_analisis_avanzado(self):
        """SOLUCIÓN 3: Ejecuta el análisis avanzado con actualización forzada"""
        if self.datos_canales is None or self.imagen_original is None:
            messagebox.showerror("Error", "Primero carga una imagen y datos de Excel")
            return
        
        try:
            self.progress_label.config(text="Ejecutando análisis avanzado...")
            self.root.update()
            
            # Limpiar visualizaciones previas
            self.limpiar_visualizaciones()
            
            height, width = self.imagen_original.shape[:2]
            cuad_height = height // self.matriz_filas
            cuad_width = width // self.matriz_cols
            
            resultados = []
            matriz_fragilidad = np.zeros((self.matriz_filas, self.matriz_cols))
            
            # Analizar cada cuadrante
            for fila in range(self.matriz_filas):
                for col in range(self.matriz_cols):
                    # Definir límites del cuadrante
                    y_min = fila * cuad_height
                    y_max = (fila + 1) * cuad_height
                    x_min = col * cuad_width
                    x_max = (col + 1) * cuad_width
                    
                    # Filtrar canales en este cuadrante
                    canales_cuadrante = self.datos_canales[
                        (self.datos_canales['Center X'] >= x_min) & 
                        (self.datos_canales['Center X'] < x_max) &
                        (self.datos_canales['Center Y'] >= y_min) & 
                        (self.datos_canales['Center Y'] < y_max)
                    ]
                    
                    # Calcular fragilidad
                    fragilidad, detalles = self.calcular_fragilidad_avanzada(canales_cuadrante)
                    matriz_fragilidad[fila, col] = fragilidad
                    
                    resultado = {
                        'cuadrante': f"{fila+1}-{col+1}",
                        'fila': fila,
                        'columna': col,
                        'fragilidad': fragilidad,
                        'x_min': x_min, 'x_max': x_max,
                        'y_min': y_min, 'y_max': y_max,
                        **detalles
                    }
                    resultados.append(resultado)
            
            self.resultados_analisis = {
                'cuadrantes': resultados,
                'matriz_fragilidad': matriz_fragilidad,
                'timestamp': datetime.now()
            }
            
            # Identificar zonas críticas
            self.identificar_zonas_criticas()
            
            # Mostrar resultados
            self.mostrar_resultados_texto()
            
            self.progress_label.config(text="Análisis completado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis: {str(e)}")
            self.progress_label.config(text="Error en el análisis")
            logging.error(f"Error en análisis: {e}")
    
    def limpiar_visualizaciones(self):
        """SOLUCIÓN 2 y 3: Limpia SOLO los gráficos, los botones están separados"""
        try:
            # Ahora es seguro limpiar todo el canvas_frame porque los botones están separados
            for widget in self.viz_canvas_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logging.error(f"Error limpiando visualizaciones: {e}")
    
    def identificar_zonas_criticas(self):
        """Identifica cuadrantes más frágiles y patrones"""
        if not self.resultados_analisis:
            return
        
        resultados = self.resultados_analisis['cuadrantes']
        
        # Filtrar cuadrantes válidos (con suficientes canales)
        validos = [r for r in resultados if r['fragilidad'] > 0]
        
        if not validos:
            return
        
        # Ordenar por fragilidad
        validos.sort(key=lambda x: x['fragilidad'], reverse=True)
        
        # Top 3 más frágiles
        self.resultados_analisis['top_fragiles'] = validos[:3]
        
        # Cuadrante más frágil
        if validos:
            mas_fragil = validos[0]
            self.resultados_analisis['mas_fragil'] = mas_fragil
        
        # Análisis de conectividad alta
        if validos:
            conectividades = [r['densidad_conectividad'] for r in validos]
            percentil_75 = np.percentile(conectividades, 75)
            alta_conectividad = [r for r in validos if r['densidad_conectividad'] > percentil_75]
            self.resultados_analisis['alta_conectividad'] = alta_conectividad
        
        # Análisis de anisotropía alta
        if validos:
            anisotropias = [r['anisotropia'] for r in validos]
            percentil_75 = np.percentile(anisotropias, 75)
            alta_anisotropia = [r for r in validos if r['anisotropia'] > percentil_75]
            self.resultados_analisis['alta_anisotropia'] = alta_anisotropia
    
    def mostrar_resultados_texto(self):
        """Muestra los resultados en formato texto"""
        if not self.resultados_analisis:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # Verificar que tenemos datos válidos
        if 'mas_fragil' not in self.resultados_analisis:
            self.results_text.insert(tk.END, "No se pudieron procesar suficientes cuadrantes para análisis.\n")
            return
        
        texto = f"""
=== ANÁLISIS AVANZADO DE FRAGILIDAD ÓSEA ===
Fecha: {self.resultados_analisis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
Matriz de análisis: {self.matriz_filas}×{self.matriz_cols}

COEFICIENTES UTILIZADOS:
w1 (peso base): {self.coeficientes['w1']:.2f}
w2 (heterogeneidad): {self.coeficientes['w2']:.2f}
w3 (conectividad): {self.coeficientes['w3']:.2f}
w4 (anisotropía): {self.coeficientes['w4']:.2f}

CUADRANTE MÁS FRÁGIL:
Cuadrante: {self.resultados_analisis['mas_fragil']['cuadrante']}
Índice de fragilidad: {self.resultados_analisis['mas_fragil']['fragilidad']:.2f}
Número de canales: {self.resultados_analisis['mas_fragil']['numero_canales']}
Área promedio: {self.resultados_analisis['mas_fragil']['area_promedio']:.2f}
Factor de tamaño: {self.resultados_analisis['mas_fragil']['factor_tamano']:.2f}
Densidad conectividad: {self.resultados_analisis['mas_fragil']['densidad_conectividad']:.4f}
Anisotropía: {self.resultados_analisis['mas_fragil']['anisotropia']:.3f}

TOP 3 CUADRANTES MÁS FRÁGILES:
"""
        
        for i, cuad in enumerate(self.resultados_analisis['top_fragiles'], 1):
            texto += f"\n{i}. Cuadrante {cuad['cuadrante']}: Fragilidad {cuad['fragilidad']:.2f}"
        
        if self.resultados_analisis.get('alta_conectividad'):
            texto += f"\n\nCUADRANTES CON ALTA CONECTIVIDAD ({len(self.resultados_analisis['alta_conectividad'])}):"
            for cuad in self.resultados_analisis['alta_conectividad'][:5]:
                texto += f"\n- Cuadrante {cuad['cuadrante']}: Conectividad {cuad['densidad_conectividad']:.4f}"
        
        if self.resultados_analisis.get('alta_anisotropia'):
            texto += f"\n\nCUADRANTES CON ALTA ANISOTROPÍA ({len(self.resultados_analisis['alta_anisotropia'])}):"
            for cuad in self.resultados_analisis['alta_anisotropia'][:5]:
                texto += f"\n- Cuadrante {cuad['cuadrante']}: Anisotropía {cuad['anisotropia']:.3f}"
        
        # Estadísticas generales
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        if fragilidades:
            texto += f"""

ESTADÍSTICAS GENERALES:
Fragilidad promedio: {np.mean(fragilidades):.2f}
Fragilidad máxima: {np.max(fragilidades):.2f}
Fragilidad mínima: {np.min(fragilidades):.2f}
Desviación estándar: {np.std(fragilidades):.2f}
Cuadrantes analizados: {len(fragilidades)} de {self.matriz_filas * self.matriz_cols}
"""
        
        self.results_text.insert(tk.END, texto)
    
    def mostrar_mapa_calor(self):
        """SOLUCIÓN 2: Muestra un mapa de calor de la fragilidad conservando botones"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        # Limpiar canvas anterior pero mantener botones
        self.limpiar_visualizaciones()
        
        # Crear figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('black')
        
        # Mapa de calor de fragilidad
        im1 = ax1.imshow(self.resultados_analisis['matriz_fragilidad'], 
                        cmap='Reds', interpolation='nearest')
        ax1.set_title('Mapa de Fragilidad', color='white', fontsize=14)
        ax1.set_facecolor('black')
        
        # Agregar valores en cada celda
        for i in range(self.matriz_filas):
            for j in range(self.matriz_cols):
                valor = self.resultados_analisis['matriz_fragilidad'][i, j]
                if valor > 0:
                    ax1.text(j, i, f'{valor:.0f}', ha='center', va='center',
                           color='white' if valor < np.max(self.resultados_analisis['matriz_fragilidad'])/2 else 'black',
                           fontweight='bold')
        
        plt.colorbar(im1, ax=ax1)
        
        # Histograma de distribución
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        ax2.hist(fragilidades, bins=15, color='red', alpha=0.7, edgecolor='white')
        ax2.set_title('Distribución de Fragilidad', color='white', fontsize=14)
        ax2.set_xlabel('Índice de Fragilidad', color='white')
        ax2.set_ylabel('Frecuencia', color='white')
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def mostrar_conectividad(self):
        """SOLUCIÓN 2: Visualiza la densidad de conectividad conservando botones"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        # Limpiar canvas anterior pero mantener botones
        self.limpiar_visualizaciones()
        
        # Crear matriz de conectividad
        matriz_conectividad = np.zeros((self.matriz_filas, self.matriz_cols))
        for resultado in self.resultados_analisis['cuadrantes']:
            if resultado['fragilidad'] > 0:
                matriz_conectividad[resultado['fila'], resultado['columna']] = resultado['densidad_conectividad']
        
        # Crear figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('black')
        
        # Mapa de conectividad
        im1 = ax1.imshow(matriz_conectividad, cmap='Blues', interpolation='nearest')
        ax1.set_title('Densidad de Conectividad', color='white', fontsize=14)
        ax1.set_facecolor('black')
        plt.colorbar(im1, ax=ax1)
        
        # Scatter plot: Conectividad vs Fragilidad
        conectividades = [r['densidad_conectividad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        ax2.scatter(conectividades, fragilidades, c='cyan', alpha=0.7)
        ax2.set_xlabel('Densidad de Conectividad', color='white')
        ax2.set_ylabel('Fragilidad', color='white')
        ax2.set_title('Correlación Conectividad-Fragilidad', color='white', fontsize=14)
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        # Línea de tendencia
        if len(conectividades) > 1:
            z = np.polyfit(conectividades, fragilidades, 1)
            p = np.poly1d(z)
            ax2.plot(sorted(conectividades), p(sorted(conectividades)), "r--", alpha=0.8)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def mostrar_anisotropia(self):
        """SOLUCIÓN 2: Visualiza el análisis de anisotropía conservando botones"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        # Limpiar canvas anterior pero mantener botones
        self.limpiar_visualizaciones()
        
        # Crear matriz de anisotropía
        matriz_anisotropia = np.zeros((self.matriz_filas, self.matriz_cols))
        for resultado in self.resultados_analisis['cuadrantes']:
            if resultado['fragilidad'] > 0:
                matriz_anisotropia[resultado['fila'], resultado['columna']] = resultado['anisotropia']
        
        # Crear figura
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('black')
        
        # Mapa de anisotropía
        im1 = ax1.imshow(matriz_anisotropia, cmap='viridis', interpolation='nearest')
        ax1.set_title('Anisotropía de Orientación', color='white', fontsize=12)
        ax1.set_facecolor('black')
        plt.colorbar(im1, ax=ax1)
        
        # Scatter plot: Anisotropía vs Fragilidad
        anisotropias = [r['anisotropia'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        ax2.scatter(anisotropias, fragilidades, c='yellow', alpha=0.7)
        ax2.set_xlabel('Anisotropía', color='white')
        ax2.set_ylabel('Fragilidad', color='white')
        ax2.set_title('Correlación Anisotropía-Fragilidad', color='white', fontsize=12)
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        # Distribución de factores de tamaño
        factores_tamano = [r['factor_tamano'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        ax3.hist(factores_tamano, bins=12, color='orange', alpha=0.7, edgecolor='white')
        ax3.set_xlabel('Factor de Tamaño', color='white')
        ax3.set_ylabel('Frecuencia', color='white')
        ax3.set_title('Distribución Factor de Tamaño', color='white', fontsize=12)
        ax3.set_facecolor('black')
        ax3.tick_params(colors='white')
        
        # Análisis multivariable
        areas_prom = [r['area_promedio'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        numero_canales = [r['numero_canales'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        scatter = ax4.scatter(areas_prom, numero_canales, c=fragilidades, 
                            cmap='Reds', alpha=0.7, s=60)
        ax4.set_xlabel('Área Promedio', color='white')
        ax4.set_ylabel('Número de Canales', color='white')
        ax4.set_title('Área vs Número (Color = Fragilidad)', color='white', fontsize=12)
        ax4.set_facecolor('black')
        ax4.tick_params(colors='white')
        plt.colorbar(scatter, ax=ax4)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.colorbar(im1, ax=ax1)
        
        # Histograma de distribución
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        ax2.hist(fragilidades, bins=15, color='red', alpha=0.7, edgecolor='white')
        ax2.set_title('Distribución de Fragilidad', color='white', fontsize=14)
        ax2.set_xlabel('Índice de Fragilidad', color='white')
        ax2.set_ylabel('Frecuencia', color='white')
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def mostrar_conectividad(self):
        """Visualiza la densidad de conectividad"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        # Limpiar canvas anterior
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # Crear matriz de conectividad
        matriz_conectividad = np.zeros((self.matriz_filas, self.matriz_cols))
        for resultado in self.resultados_analisis['cuadrantes']:
            if resultado['fragilidad'] > 0:
                matriz_conectividad[resultado['fila'], resultado['columna']] = resultado['densidad_conectividad']
        
        # Crear figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('black')
        
        # Mapa de conectividad
        im1 = ax1.imshow(matriz_conectividad, cmap='Blues', interpolation='nearest')
        ax1.set_title('Densidad de Conectividad', color='white', fontsize=14)
        ax1.set_facecolor('black')
        plt.colorbar(im1, ax=ax1)
        
        # Scatter plot: Conectividad vs Fragilidad
        conectividades = [r['densidad_conectividad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        ax2.scatter(conectividades, fragilidades, c='cyan', alpha=0.7)
        ax2.set_xlabel('Densidad de Conectividad', color='white')
        ax2.set_ylabel('Fragilidad', color='white')
        ax2.set_title('Correlación Conectividad-Fragilidad', color='white', fontsize=14)
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        # Línea de tendencia
        if len(conectividades) > 1:
            z = np.polyfit(conectividades, fragilidades, 1)
            p = np.poly1d(z)
            ax2.plot(sorted(conectividades), p(sorted(conectividades)), "r--", alpha=0.8)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def mostrar_anisotropia(self):
        """Visualiza el análisis de anisotropía"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        # Limpiar canvas anterior
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # Crear matriz de anisotropía
        matriz_anisotropia = np.zeros((self.matriz_filas, self.matriz_cols))
        for resultado in self.resultados_analisis['cuadrantes']:
            if resultado['fragilidad'] > 0:
                matriz_anisotropia[resultado['fila'], resultado['columna']] = resultado['anisotropia']
        
        # Crear figura
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('black')
        
        # Mapa de anisotropía
        im1 = ax1.imshow(matriz_anisotropia, cmap='viridis', interpolation='nearest')
        ax1.set_title('Anisotropía de Orientación', color='white', fontsize=12)
        ax1.set_facecolor('black')
        plt.colorbar(im1, ax=ax1)
        
        # Scatter plot: Anisotropía vs Fragilidad
        anisotropias = [r['anisotropia'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        ax2.scatter(anisotropias, fragilidades, c='yellow', alpha=0.7)
        ax2.set_xlabel('Anisotropía', color='white')
        ax2.set_ylabel('Fragilidad', color='white')
        ax2.set_title('Correlación Anisotropía-Fragilidad', color='white', fontsize=12)
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white')
        
        # Distribución de factores de tamaño
        factores_tamano = [r['factor_tamano'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        ax3.hist(factores_tamano, bins=12, color='orange', alpha=0.7, edgecolor='white')
        ax3.set_xlabel('Factor de Tamaño', color='white')
        ax3.set_ylabel('Frecuencia', color='white')
        ax3.set_title('Distribución Factor de Tamaño', color='white', fontsize=12)
        ax3.set_facecolor('black')
        ax3.tick_params(colors='white')
        
        # Análisis multivariable
        areas_prom = [r['area_promedio'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        numero_canales = [r['numero_canales'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        scatter = ax4.scatter(areas_prom, numero_canales, c=fragilidades, 
                            cmap='Reds', alpha=0.7, s=60)
        ax4.set_xlabel('Área Promedio', color='white')
        ax4.set_ylabel('Número de Canales', color='white')
        ax4.set_title('Área vs Número (Color = Fragilidad)', color='white', fontsize=12)
        ax4.set_facecolor('black')
        ax4.tick_params(colors='white')
        plt.colorbar(scatter, ax=ax4)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def exportar_excel(self):
        """Exporta los resultados a Excel"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        try:
            # Crear nombre de archivo con timestamp directamente en breaking_app/
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.base_dir / f"analisis_fragilidad_{timestamp}.xlsx"
            
            # Crear DataFrame con todos los resultados
            df_resultados = pd.DataFrame(self.resultados_analisis['cuadrantes'])
            
            # Crear archivo Excel con múltiples hojas
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja principal con todos los datos
                df_resultados.to_excel(writer, sheet_name='Análisis Completo', index=False)
                
                # Hoja con resumen ejecutivo
                if 'mas_fragil' in self.resultados_analisis:
                    resumen_data = {
                        'Métrica': [
                            'Cuadrante más frágil',
                            'Fragilidad máxima',
                            'Fragilidad promedio',
                            'Desviación estándar',
                            'Cuadrantes analizados',
                            'Fecha de análisis'
                        ],
                        'Valor': [
                            self.resultados_analisis['mas_fragil']['cuadrante'],
                            f"{self.resultados_analisis['mas_fragil']['fragilidad']:.2f}",
                            f"{np.mean([r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]):.2f}",
                            f"{np.std([r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]):.2f}",
                            len([r for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]),
                            self.resultados_analisis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    }
                    df_resumen = pd.DataFrame(resumen_data)
                    df_resumen.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
                
                # Hoja con top frágiles
                if 'top_fragiles' in self.resultados_analisis:
                    df_top = pd.DataFrame(self.resultados_analisis['top_fragiles'])
                    df_top.to_excel(writer, sheet_name='Top Frágiles', index=False)
                
                # Hoja con configuración utilizada
                config_data = {
                    'Parámetro': ['w1', 'w2', 'w3', 'w4', 'Matriz'],
                    'Valor': [
                        self.coeficientes['w1'],
                        self.coeficientes['w2'],
                        self.coeficientes['w3'],
                        self.coeficientes['w4'],
                        f"{self.matriz_filas}x{self.matriz_cols}"
                    ],
                    'Descripción': [
                        'Peso base (Área × log(N))',
                        'Peso heterogeneidad tamaño',
                        'Peso densidad conectividad',
                        'Peso anisotropía orientación',
                        'Resolución de matriz'
                    ]
                }
                df_config = pd.DataFrame(config_data)
                df_config.to_excel(writer, sheet_name='Configuración', index=False)
            
            messagebox.showinfo("Éxito", f"Resultados exportados a:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
            logging.error(f"Error exportando Excel: {e}")
    
    def generar_informe(self):
        """Genera un informe completo en HTML"""
        if not self.resultados_analisis:
            messagebox.showwarning("Advertencia", "Primero ejecuta el análisis")
            return
        
        try:
            # Crear directorio para el informe directamente en breaking_app/
            timestamp = self.resultados_analisis['timestamp'].strftime('%Y%m%d_%H%M%S')
            informe_dir = self.base_dir / f"informe_fragilidad_{timestamp}"
            informe_dir.mkdir(exist_ok=True)
            
            # Generar visualizaciones y guardarlas
            self.guardar_visualizaciones(informe_dir, timestamp)
            
            # Crear HTML
            html_content = self.crear_html_informe(timestamp)
            
            filename = informe_dir / "informe_fragilidad.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            messagebox.showinfo("Éxito", f"Informe completo generado en:\n{informe_dir}")
            
            # Intentar abrir el archivo
            try:
                import webbrowser
                webbrowser.open(str(filename))
            except:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
            logging.error(f"Error generando informe: {e}")
    
    def guardar_visualizaciones(self, directorio, timestamp):
        """Guarda las visualizaciones como imágenes"""
        try:
            # Mapa de calor
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('white')
            im = ax.imshow(self.resultados_analisis['matriz_fragilidad'], cmap='Reds')
            ax.set_title('Mapa de Fragilidad Ósea')
            plt.colorbar(im)
            plt.savefig(directorio / f'mapa_fragilidad_{timestamp}.png', 
                       dpi=300, bbox_inches='tight')
            plt.close()
            
            # Conectividad
            matriz_conectividad = np.zeros((self.matriz_filas, self.matriz_cols))
            for resultado in self.resultados_analisis['cuadrantes']:
                if resultado['fragilidad'] > 0:
                    matriz_conectividad[resultado['fila'], resultado['columna']] = resultado['densidad_conectividad']
            
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('white')
            im = ax.imshow(matriz_conectividad, cmap='Blues')
            ax.set_title('Densidad de Conectividad')
            plt.colorbar(im)
            plt.savefig(directorio / f'conectividad_{timestamp}.png', 
                       dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            logging.error(f"Error guardando visualizaciones: {e}")
    
    def crear_html_informe(self, timestamp):
        """Crea el contenido HTML del informe"""
        if 'mas_fragil' not in self.resultados_analisis:
            return "<html><body><h1>Error: No hay datos suficientes para generar el informe</h1></body></html>"
            
        mas_fragil = self.resultados_analisis['mas_fragil']
        fragilidades = [r['fragilidad'] for r in self.resultados_analisis['cuadrantes'] if r['fragilidad'] > 0]
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Análisis de Fragilidad Ósea</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #BD0000; color: white; padding: 20px; text-align: center; }}
        .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #BD0000; }}
        .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .critical {{ background: #ffebee; border: 2px solid #BD0000; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #BD0000; color: white; }}
        .image-container {{ text-align: center; margin: 20px 0; }}
        .footer {{ margin-top: 50px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Informe de Análisis Avanzado de Fragilidad Ósea</h1>
        <h2>Havers Analisis - Phygital Human Bone 3.0</h2>
        <p>Generado el: {self.resultados_analisis['timestamp'].strftime('%d de %B de %Y a las %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Resumen Ejecutivo</h2>
        <div class="metric critical">
            <strong>Cuadrante Más Frágil:</strong> {mas_fragil['cuadrante']}<br>
            <strong>Índice de Fragilidad:</strong> {mas_fragil['fragilidad']:.2f}
        </div>
        <div class="metric">
            <strong>Análisis realizado en matriz:</strong> {self.matriz_filas}×{self.matriz_cols} cuadrantes<br>
            <strong>Cuadrantes analizados:</strong> {len(fragilidades)} de {self.matriz_filas * self.matriz_cols}<br>
            <strong>Fragilidad promedio:</strong> {np.mean(fragilidades):.2f} ± {np.std(fragilidades):.2f}
        </div>
    </div>

    <div class="section">
        <h2>Configuración del Modelo</h2>
        <p>El análisis utilizó el modelo matemático avanzado de fragilidad ósea con los siguientes coeficientes:</p>
        <table>
            <tr><th>Coeficiente</th><th>Valor</th><th>Descripción</th></tr>
            <tr><td>w₁</td><td>{self.coeficientes['w1']:.2f}</td><td>Peso del término base (Área × log(N))</td></tr>
            <tr><td>w₂</td><td>{self.coeficientes['w2']:.2f}</td><td>Peso de heterogeneidad de tamaño</td></tr>
            <tr><td>w₃</td><td>{self.coeficientes['w3']:.2f}</td><td>Peso de densidad de conectividad</td></tr>
            <tr><td>w₄</td><td>{self.coeficientes['w4']:.2f}</td><td>Peso de anisotropía de orientación</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Análisis Detallado del Cuadrante Más Frágil</h2>
        <div class="metric critical">
            <h3>Cuadrante {mas_fragil['cuadrante']}</h3>
            <p><strong>Número de canales:</strong> {mas_fragil['numero_canales']}</p>
            <p><strong>Área promedio:</strong> {mas_fragil['area_promedio']:.2f} píxeles²</p>
            <p><strong>Factor de tamaño:</strong> {mas_fragil['factor_tamano']:.2f}</p>
            <p><strong>Densidad de conectividad:</strong> {mas_fragil['densidad_conectividad']:.6f}</p>
            <p><strong>Anisotropía de orientación:</strong> {mas_fragil['anisotropia']:.3f}</p>
        </div>
        
        <h4>Descomposición del Índice de Fragilidad:</h4>
        <ul>
            <li>Término base: {mas_fragil['termino_base']:.2f}</li>
            <li>Factor de tamaño: {mas_fragil['termino_tamano']:.2f}</li>
            <li>Factor de conectividad: {mas_fragil['termino_conectividad']:.2f}</li>
            <li>Factor de anisotropía: {mas_fragil['termino_anisotropia']:.2f}</li>
        </ul>
    </div>

    <div class="section">
        <h2>Top 5 Cuadrantes Más Frágiles</h2>
        <table>
            <tr>
                <th>Ranking</th>
                <th>Cuadrante</th>
                <th>Fragilidad</th>
                <th>Canales</th>
                <th>Área Promedio</th>
                <th>Conectividad</th>
            </tr>"""
        
        for i, cuad in enumerate(self.resultados_analisis['top_fragiles'][:5], 1):
            html += f"""
            <tr>
                <td>{i}</td>
                <td>{cuad['cuadrante']}</td>
                <td>{cuad['fragilidad']:.2f}</td>
                <td>{cuad['numero_canales']}</td>
                <td>{cuad['area_promedio']:.2f}</td>
                <td>{cuad['densidad_conectividad']:.6f}</td>
            </tr>"""
        
        html += f"""
        </table>
    </div>

    <div class="section">
        <h2>Visualizaciones</h2>
        <div class="image-container">
            <h3>Mapa de Fragilidad</h3>
            <img src="mapa_fragilidad_{timestamp}.png" alt="Mapa de Fragilidad" style="max-width: 100%; height: auto;">
        </div>
        <div class="image-container">
            <h3>Densidad de Conectividad</h3>
            <img src="conectividad_{timestamp}.png" alt="Densidad de Conectividad" style="max-width: 100%; height: auto;">
        </div>
    </div>

    <div class="section">
        <h2>Interpretación Biomecánica</h2>
        <h3>Factores Críticos Identificados:</h3>"""
        
        # Análisis de factores críticos
        if self.resultados_analisis.get('alta_conectividad'):
            html += f"""
        <div class="metric">
            <strong>Alta Conectividad Detectada:</strong> {len(self.resultados_analisis['alta_conectividad'])} cuadrantes presentan 
            densidad de conectividad en el percentil 75 superior, lo que indica agrupaciones de canales que pueden facilitar 
            la propagación de microfracturas.
        </div>"""
        
        if self.resultados_analisis.get('alta_anisotropia'):
            html += f"""
        <div class="metric">
            <strong>Anisotropía Significativa:</strong> {len(self.resultados_analisis['alta_anisotropia'])} cuadrantes muestran 
            alta anisotropía de orientación, sugiriendo alineación preferencial de canales que puede crear planos de debilidad.
        </div>"""
        
        html += f"""
        <h3>Recomendaciones:</h3>
        <ul>
            <li>Monitorización especial del cuadrante {mas_fragil['cuadrante']} debido a su alto índice de fragilidad</li>
            <li>Considerar la distribución espacial heterogénea en el diseño de modelos biomiméticos</li>
            <li>Evaluar la anisotropía de orientación para optimizar las propiedades direccionales</li>
        </ul>
    </div>

    <div class="footer">
        <p>Informe generado por Havers Analisis v3.0 - Phygital Human Bone Project</p>
        <p>Para más información sobre la metodología, consultar la documentación técnica del proyecto</p>
    </div>
</body>
</html>"""
        
        return html

def main():
    """Función principal para ejecutar la aplicación"""
    # Configurar logging en breaking_app/ directamente
    try:
        # Detectar directorio del proyecto
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        log_dir = project_root / "data" / "sample_results" / "breaking_app"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "fragility_app.log"
    except:
        # Fallback
        log_file = "fragility_app.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    root = tk.Tk()
    app = AdvancedBoneFragilityAnalyzer(root)
    
    try:
        root.mainloop()
    except Exception as e:
        logging.error(f"Error en aplicación principal: {e}")
        messagebox.showerror("Error Fatal", f"Error inesperado: {e}")

if __name__ == "__main__":
    main()