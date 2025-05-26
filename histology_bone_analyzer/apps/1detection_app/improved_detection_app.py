import cv2
import os
import shutil
import pandas as pd
import numpy as np
from math import ceil, pi
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import logging
from dataclasses import dataclass
from ultralytics import YOLO
import torch
from tkinter import Tk, Button, Text, Scrollbar, Frame, Label, filedialog, StringVar, messagebox, ttk
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import gc
import time

# ============================================================================
# CONFIGURACIÓN GLOBAL Y CONSTANTES
# ============================================================================

@dataclass
class Config:
    """Configuración centralizada de la aplicación."""
    # Directorios base
    BASE_DIR: str = r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\histology_bone_analyzer\data\sample_results\detection_app"
    TECHNICAL_DIR: str = r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\histology_bone_analyzer\docs\technical"
    RECONSTRUCTED_IMAGES_DIR: str = r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\histology_bone_analyzer\data\sample_images"
    
    # Configuración de modelo
    MODEL_PATHS: List[str] = None
    CONFIDENCE_THRESHOLD: float = 0.4
    MAX_PIXELS: int = 178956970
    NUM_SEGMENTS: int = 150
    SEGMENT_COLS: int = 15
    
    # Configuración visual
    BACKGROUND_COLOR: str = '#000000'
    BUTTON_COLOR: str = '#BD0000'
    BUTTON_HOVER_COLOR: str = '#333333'
    TEXT_COLOR: str = 'white'
    
    # Configuración de visualización
    FIGURE_SIZE: Tuple[int, int] = (16, 16)
    DPI: int = 600
    HEATMAP_BINS: int = 100
    
    def __post_init__(self):
        if self.MODEL_PATHS is None:
            self.MODEL_PATHS = [
                r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\histology_bone_analyzer\models\weights.pt",
                r"C:\Users\joanb\OneDrive\Escritorio\TFG\workspace\runs\detect\train\weights\weights.pt",
                r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\runs\detect\train13\weights\weights.pt",
                r"C:\Users\joanb\OneDrive\Escritorio\TFG\Workspace_tfg\osteona\weights.pt"
            ]
        
        # Crear rutas derivadas
        self.IMAGES_SEGMENTED_DIR = os.path.join(self.BASE_DIR, "images_segmented")
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "segmented_results")
        self.RESULTS_DIR = os.path.join(self.BASE_DIR, "results")
        self.EXCEL_DIR = os.path.join(self.BASE_DIR, "excel")

# Instancia global de configuración
config = Config()

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

def setup_logging():
    """Configura el sistema de logging para mejor seguimiento de errores."""
    log_file = os.path.join(config.BASE_DIR, "detection_app.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# GESTIÓN DE MEMORIA Y RECURSOS
# ============================================================================

class MemoryManager:
    """Gestiona la memoria de forma eficiente durante el procesamiento."""
    
    @staticmethod
    def clear_cache():
        """Limpia la caché de memoria."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @staticmethod
    def get_memory_usage():
        """Obtiene el uso actual de memoria."""
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB

# ============================================================================
# GESTIÓN DE DIRECTORIOS
# ============================================================================

class DirectoryManager:
    """Maneja la creación y gestión de directorios."""
    
    @staticmethod
    def initialize_directories():
        """Crea todas las carpetas necesarias si no existen."""
        directories = [
            config.BASE_DIR,
            config.IMAGES_SEGMENTED_DIR,
            config.OUTPUT_DIR,
            config.RESULTS_DIR,
            config.EXCEL_DIR,
            config.TECHNICAL_DIR,
            config.RECONSTRUCTED_IMAGES_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio verificado/creado: {directory}")
    
    @staticmethod
    def clean_segment_directory():
        """Limpia la carpeta de segmentos."""
        if os.path.exists(config.IMAGES_SEGMENTED_DIR):
            for file in os.listdir(config.IMAGES_SEGMENTED_DIR):
                if file.startswith("segment_") and file.endswith(".png"):
                    os.remove(os.path.join(config.IMAGES_SEGMENTED_DIR, file))

# ============================================================================
# INTERFAZ GRÁFICA MEJORADA
# ============================================================================

class UIManager:
    """Gestiona todos los aspectos de la interfaz de usuario."""
    
    @staticmethod
    def configure_window(window: Tk, title: str):
        """Configura el aspecto visual y posición de la ventana."""
        window.title(title)
        
        # Configurar tamaños y posición
        ancho_ventana = 900
        alto_ventana = 700
        x = (window.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (window.winfo_screenheight() // 2) - (alto_ventana // 2)
        window.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
        
        window.resizable(True, True)
        window.minsize(700, 500)
        window.configure(bg=config.BACKGROUND_COLOR)
        
        # Configurar estilo para ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TProgressbar', background=config.BUTTON_COLOR)
    
    @staticmethod
    def configure_button(button: Button):
        """Aplica estilo visual mejorado a los botones."""
        button.configure(
            bg=config.BUTTON_COLOR,
            fg=config.TEXT_COLOR,
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=8,
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        
        # Efectos hover mejorados
        def on_enter(e):
            button.configure(bg=config.BUTTON_HOVER_COLOR, relief="raised", borderwidth=2)
        
        def on_leave(e):
            button.configure(bg=config.BUTTON_COLOR, relief="flat", borderwidth=0)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    @staticmethod
    def clear_window(window: Tk):
        """Elimina todos los widgets de una ventana."""
        for widget in window.winfo_children():
            widget.destroy()
    
    @staticmethod
    def show_progress_dialog(parent: Tk, title: str = "Procesando..."):
        """Muestra una ventana de progreso moderna."""
        progress_window = Tk()
        progress_window.title(title)
        progress_window.geometry("400x150")
        progress_window.configure(bg=config.BACKGROUND_COLOR)
        progress_window.resizable(False, False)
        
        # Centrar ventana
        progress_window.transient(parent)
        progress_window.grab_set()
        
        # Contenido
        Label(progress_window, text=title, font=("Helvetica", 14, "bold"), 
              fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR).pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate', length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        status_label = Label(progress_window, text="Iniciando...", font=("Helvetica", 10), 
                           fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR)
        status_label.pack(pady=5)
        
        progress_window.update()
        
        return progress_window, progress_bar, status_label

# ============================================================================
# PROCESAMIENTO DE IMÁGENES OPTIMIZADO
# ============================================================================

class ImageProcessor:
    """Maneja todo el procesamiento de imágenes de forma optimizada."""
    
    @staticmethod
    def validate_image(image_path: str) -> bool:
        """Valida que la imagen sea legible y tenga formato correcto."""
        try:
            # Verificar existencia
            if not os.path.exists(image_path):
                logger.error(f"Archivo no encontrado: {image_path}")
                return False
            
            # Verificar formato
            valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
            if Path(image_path).suffix.lower() not in valid_extensions:
                logger.error(f"Formato de imagen no soportado: {image_path}")
                return False
            
            # Intentar cargar la imagen
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"No se pudo cargar la imagen: {image_path}")
                return False
            
            logger.info(f"Imagen validada correctamente: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validando imagen: {e}")
            return False
    
    @staticmethod
    def resize_image_if_needed(image_path: str, max_pixels: int = None) -> str:
        """Redimensiona una imagen si excede el límite de píxeles."""
        if max_pixels is None:
            max_pixels = config.MAX_PIXELS
        
        logger.info(f"Verificando tamaño de imagen: {image_path}")
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("No se pudo cargar la imagen")
            
            height, width = img.shape[:2]
            pixels = height * width
            logger.info(f"Tamaño original: {width}x{height} = {pixels:,} píxeles")
            
            if pixels <= max_pixels:
                return image_path
            
            # Calcular nuevo tamaño
            scale = (max_pixels / pixels) ** 0.5
            new_width = int(width * scale)
            new_height = int(height * scale)
            logger.info(f"Redimensionando a: {new_width}x{new_height}")
            
            # Redimensionar con interpolación de alta calidad
            resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Guardar versión redimensionada
            path_obj = Path(image_path)
            resized_path = str(path_obj.parent / f"{path_obj.stem}_resized{path_obj.suffix}")
            cv2.imwrite(resized_path, resized)
            
            logger.info(f"Imagen redimensionada guardada en: {resized_path}")
            
            # Limpiar memoria
            del img, resized
            MemoryManager.clear_cache()
            
            return resized_path
            
        except Exception as e:
            logger.error(f"Error redimensionando imagen: {e}")
            raise
    
    @staticmethod
    def divide_image_optimized(image_path: str, num_segments: int = None) -> Tuple[List[Tuple], int, int]:
        """Divide una imagen en segmentos optimizando el uso de memoria."""
        if num_segments is None:
            num_segments = config.NUM_SEGMENTS
        
        # Limpiar directorio de segmentos
        DirectoryManager.clean_segment_directory()
        
        logger.info(f"Dividiendo imagen: {image_path}")
        
        try:
            # Cargar imagen con manejo de errores mejorado
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if image is None:
                # Método alternativo de carga
                with open(image_path, 'rb') as f:
                    img_bytes = f.read()
                image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                
                if image is None:
                    raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Configurar división
            cols = config.SEGMENT_COLS
            rows = ceil(num_segments / cols)
            segment_height = image.shape[0] // rows
            segment_width = image.shape[1] // cols
            
            logger.info(f"Dividiendo en {rows}x{cols} segmentos ({segment_width}x{segment_height} cada uno)")
            
            # Dividir y guardar con progreso
            segment_positions = []
            total_segments = min(rows * cols, num_segments)
            
            for i in range(rows):
                for j in range(cols):
                    if len(segment_positions) >= total_segments:
                        break
                    
                    # Calcular límites del segmento
                    start_y = i * segment_height
                    end_y = min(start_y + segment_height, image.shape[0])
                    start_x = j * segment_width
                    end_x = min(start_x + segment_width, image.shape[1])
                    
                    # Extraer segmento
                    segment = image[start_y:end_y, start_x:end_x].copy()
                    
                    # Guardar segmento
                    segment_id = len(segment_positions) + 1
                    segment_filename = f"segment_{segment_id}.png"
                    segment_path = os.path.join(config.IMAGES_SEGMENTED_DIR, segment_filename)
                    
                    cv2.imwrite(segment_path, segment, [cv2.IMWRITE_PNG_COMPRESSION, 1])
                    
                    segment_positions.append((start_x, start_y, segment_id))
                    
                    # Limpiar memoria del segmento
                    del segment
                
                if len(segment_positions) >= total_segments:
                    break
            
            # Limpiar memoria de la imagen original
            del image
            MemoryManager.clear_cache()
            
            logger.info(f"Segmentación completada: {len(segment_positions)} segmentos guardados")
            return segment_positions, segment_width, segment_height
            
        except Exception as e:
            logger.error(f"Error dividiendo imagen: {e}")
            raise

# ============================================================================
# MODELO YOLO OPTIMIZADO
# ============================================================================

class YOLOModelManager:
    """Gestiona la carga y uso del modelo YOLO de forma optimizada."""
    
    def __init__(self):
        self.model = None
        self.model_path = None
    
    def find_model_path(self) -> Optional[str]:
        """Busca el modelo YOLO en las rutas especificadas."""
        for path in config.MODEL_PATHS:
            if os.path.exists(path):
                logger.info(f"Modelo encontrado en: {path}")
                return path
        
        logger.error("No se encontró el modelo YOLO en ninguna ruta")
        return None
    
    def load_model(self) -> bool:
        """Carga el modelo YOLO con configuración optimizada."""
        try:
            self.model_path = self.find_model_path()
            if not self.model_path:
                return False
            
            logger.info("Cargando modelo YOLO...")
            self.model = YOLO(self.model_path)
            
            # Configurar modelo para mejor rendimiento
            if torch.cuda.is_available():
                self.model.to('cuda')
                logger.info("Modelo cargado en GPU")
            else:
                logger.info("Modelo cargado en CPU")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def process_segments_batch(self, segment_positions: List[Tuple], 
                              confidence_threshold: float = None,
                              batch_size: int = 4) -> List[Tuple]:
        """Procesa segmentos en lotes para mayor eficiencia."""
        if confidence_threshold is None:
            confidence_threshold = config.CONFIDENCE_THRESHOLD
        
        if not self.model:
            raise ValueError("Modelo no cargado")
        
        box_centers_and_areas = []
        total_segments = len(segment_positions)
        
        logger.info(f"Procesando {total_segments} segmentos en lotes de {batch_size}")
        
        # Procesar en lotes
        for i in range(0, total_segments, batch_size):
            batch_end = min(i + batch_size, total_segments)
            batch_positions = segment_positions[i:batch_end]
            
            batch_paths = []
            valid_positions = []
            
            # Preparar rutas del lote
            for start_x, start_y, segment_id in batch_positions:
                segment_path = os.path.join(config.IMAGES_SEGMENTED_DIR, f"segment_{segment_id}.png")
                if os.path.exists(segment_path):
                    batch_paths.append(segment_path)
                    valid_positions.append((start_x, start_y, segment_id))
            
            if not batch_paths:
                continue
            
            try:
                # Procesar lote con YOLO
                results = self.model(batch_paths, conf=confidence_threshold, verbose=False)
                
                # Procesar resultados
                for j, result in enumerate(results):
                    start_x, start_y, segment_id = valid_positions[j]
                    boxes = result.boxes
                    
                    if boxes is not None and len(boxes) > 0:
                        centers = self._calculate_centers_and_areas(boxes, start_x, start_y, segment_id)
                        box_centers_and_areas.extend(centers)
                        
                        # Guardar imagen con anotaciones
                        self._save_annotated_image(result, segment_id)
                    
                    logger.debug(f"Segmento {segment_id}: {len(boxes) if boxes else 0} detecciones")
                
                # Limpiar memoria después de cada lote
                MemoryManager.clear_cache()
                
            except Exception as e:
                logger.error(f"Error procesando lote {i//batch_size + 1}: {e}")
                continue
        
        logger.info(f"Procesamiento completado: {len(box_centers_and_areas)} detecciones totales")
        return box_centers_and_areas
    
    def _calculate_centers_and_areas(self, boxes, start_x: int, start_y: int, segment_id: int) -> List[Tuple]:
        """Calcula centros y áreas de las detecciones."""
        centers = []
        for box in boxes:
            try:
                xyxy = box.xyxy.clone().detach().cpu().view(1, 4)
                width = float(xyxy[0, 2] - xyxy[0, 0])
                height = float(xyxy[0, 3] - xyxy[0, 1])
                
                # Coordenadas globales del centro
                cx = float(start_x + (xyxy[0, 0] + xyxy[0, 2]) / 2)
                cy = float(start_y + (xyxy[0, 1] + xyxy[0, 3]) / 2)
                
                # Área elíptica
                semi_major_axis = width / 2
                semi_minor_axis = height / 2
                ellipse_area = pi * semi_major_axis * semi_minor_axis
                
                centers.append((cx, cy, segment_id, float(ellipse_area)))
                
            except Exception as e:
                logger.error(f"Error calculando centro para caja en segmento {segment_id}: {e}")
                continue
        
        return centers
    
    def _save_annotated_image(self, result, segment_id: int):
        """Guarda la imagen con anotaciones."""
        try:
            annotated_img = result.plot()
            
            # Guardar en directorio de resultados
            output_path = os.path.join(config.OUTPUT_DIR, f"result_{segment_id}.png")
            cv2.imwrite(output_path, annotated_img)
            
            # Guardar copia en directorio de imágenes reconstruidas
            reconstructed_path = os.path.join(config.RECONSTRUCTED_IMAGES_DIR, f"reconstructed_{segment_id}.png")
            cv2.imwrite(reconstructed_path, annotated_img)
            
        except Exception as e:
            logger.error(f"Error guardando imagen anotada para segmento {segment_id}: {e}")

# ============================================================================
# ANÁLISIS Y VISUALIZACIÓN OPTIMIZADOS
# ============================================================================

class DataAnalyzer:
    """Maneja el análisis de datos y generación de visualizaciones."""
    
    @staticmethod
    def calculate_distance_matrix_optimized(centers_df: pd.DataFrame) -> float:
        """Calcula la distancia media entre centros de forma optimizada."""
        if len(centers_df) < 2:
            return 0.0
        
        points = centers_df[['Center X', 'Center Y']].values
        
        # Usar broadcasting vectorizado para mayor eficiencia
        diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
        distances_matrix = np.sqrt(np.sum(diff**2, axis=2))
        
        # Tomar solo la matriz triangular superior (sin diagonal)
        upper_triangle = np.triu(distances_matrix, k=1)
        distances = upper_triangle[upper_triangle > 0]
        
        return float(np.mean(distances)) if len(distances) > 0 else 0.0
    
    @staticmethod
    def generate_visualization_optimized(df: pd.DataFrame, image_path: str) -> Dict[str, Any]:
        """Genera visualizaciones optimizadas con mejor calidad."""
        try:
            # Configurar matplotlib para mejor calidad
            plt.rcParams['figure.dpi'] = config.DPI
            plt.rcParams['savefig.dpi'] = config.DPI
            plt.rcParams['font.size'] = 12
            
            # Generar mapa de coordenadas
            plot_path = DataAnalyzer._create_coordinates_plot(df, image_path)
            
            # Generar mapa de calor
            heatmap_path = DataAnalyzer._create_heatmap(df, image_path)
            
            # Calcular estadísticas
            stats = DataAnalyzer._calculate_statistics(df)
            
            return {
                'plot_path': plot_path,
                'heatmap_path': heatmap_path,
                **stats
            }
            
        except Exception as e:
            logger.error(f"Error generando visualizaciones: {e}")
            raise
    
    @staticmethod
    def _create_coordinates_plot(df: pd.DataFrame, image_path: str) -> str:
        """Crea el mapa de coordenadas con mejor calidad."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)
        
        try:
            # Cargar y mostrar imagen de fondo
            image = plt.imread(image_path)
            ax.imshow(image, extent=[0, image.shape[1], image.shape[0], 0], alpha=0.7)
            
            # Crear scatter plot con colores basados en área
            areas = df['Ellipse Area (pixels^2)']
            scatter = ax.scatter(df['Center X'], df['Center Y'], 
                               c=areas, cmap='Reds', marker='o', s=20, alpha=0.8, edgecolors='black', linewidths=0.5)
            
            # Configurar plot
            ax.set_title('Mapa de Coordenadas de Canales de Havers', fontsize=16, fontweight='bold')
            ax.set_xlabel('Coordenada X (píxeles)', fontsize=14)
            ax.set_ylabel('Coordenada Y (píxeles)', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.invert_yaxis()
            
            # Añadir colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Área del Canal (píxeles²)', fontsize=12)
            
            # Guardar con alta calidad
            plot_filename = os.path.join(config.RESULTS_DIR, "mapa_coordenadas.png")
            plt.savefig(plot_filename, format='png', dpi=config.DPI, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Mapa de coordenadas guardado: {plot_filename}")
            return plot_filename
            
        except Exception as e:
            plt.close(fig)
            logger.error(f"Error creando mapa de coordenadas: {e}")
            raise
    
    @staticmethod
    def _create_heatmap(df: pd.DataFrame, image_path: str) -> str:
        """Crea el mapa de calor con mejor calidad."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE)
        
        try:
            # Cargar imagen de fondo
            image = plt.imread(image_path)
            ax.imshow(image, extent=[0, image.shape[1], image.shape[0], 0], alpha=0.5)
            
            # Crear mapa de calor
            heatmap, xedges, yedges = np.histogram2d(
                df['Center X'], df['Center Y'], 
                bins=config.HEATMAP_BINS
            )
            
            extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
            
            # Mostrar mapa de calor
            im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                          cmap='hot', alpha=0.7, interpolation='gaussian')
            
            # Configurar plot
            ax.set_title('Mapa de Densidad de Canales de Havers', fontsize=16, fontweight='bold')
            ax.set_xlabel('Coordenada X (píxeles)', fontsize=14)
            ax.set_ylabel('Coordenada Y (píxeles)', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.invert_yaxis()
            
            # Añadir colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Densidad de Canales', fontsize=12)
            
            # Guardar con alta calidad
            heatmap_filename = os.path.join(config.RESULTS_DIR, "mapa_calor.png")
            plt.savefig(heatmap_filename, format='png', dpi=config.DPI, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Mapa de calor guardado: {heatmap_filename}")
            return heatmap_filename
            
        except Exception as e:
            plt.close(fig)
            logger.error(f"Error creando mapa de calor: {e}")
            raise
    
    @staticmethod
    def _calculate_statistics(df: pd.DataFrame) -> Dict[str, float]:
        """Calcula estadísticas mejoradas de los datos."""
        return {
            'avg_area': float(df['Ellipse Area (pixels^2)'].mean()),
            'median_area': float(df['Ellipse Area (pixels^2)'].median()),
            'std_area': float(df['Ellipse Area (pixels^2)'].std()),
            'min_area': float(df['Ellipse Area (pixels^2)'].min()),
            'max_area': float(df['Ellipse Area (pixels^2)'].max()),
            'count': int(len(df)),
            'avg_distance': DataAnalyzer.calculate_distance_matrix_optimized(df)
        }

# ============================================================================
# GESTIÓN DE DATOS MEJORADA
# ============================================================================

class DataManager:
    """Gestiona el guardado y carga de datos."""
    
    @staticmethod
    def save_results_to_excel_enhanced(detections: List[Tuple]) -> Tuple[str, pd.DataFrame]:
        """Guarda resultados en Excel con formato mejorado."""
        try:
            # Crear DataFrame con mejor estructura
            df = pd.DataFrame(detections, columns=[
                'Center X', 'Center Y', 'Segment ID', 'Ellipse Area (pixels^2)'
            ])
            
            # Añadir columnas calculadas
            df['Area Category'] = pd.cut(df['Ellipse Area (pixels^2)'], 
                                       bins=3, labels=['Pequeño', 'Medio', 'Grande'])
            df['Detection Time'] = pd.Timestamp.now()
            
            # Ordenar por área descendente
            df = df.sort_values('Ellipse Area (pixels^2)', ascending=False)
            
            # Guardar en ubicación principal
            excel_path = os.path.join(config.EXCEL_DIR, 'bounding_box_centers_enhanced.xlsx')
            
            # Crear writer con múltiples hojas
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Hoja principal con datos
                df.to_excel(writer, sheet_name='Detecciones', index=False)
                
                # Hoja con estadísticas
                stats_df = pd.DataFrame({
                    'Métrica': ['Total Canales', 'Área Promedio', 'Área Mediana', 
                               'Desviación Estándar', 'Área Mínima', 'Área Máxima'],
                    'Valor': [len(df), df['Ellipse Area (pixels^2)'].mean(),
                             df['Ellipse Area (pixels^2)'].median(),
                             df['Ellipse Area (pixels^2)'].std(),
                             df['Ellipse Area (pixels^2)'].min(),
                             df['Ellipse Area (pixels^2)'].max()]
                })
                stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            # Crear copia de seguridad
            backup_path = os.path.join(config.TECHNICAL_DIR, 'bounding_box_centers_backup.xlsx')
            shutil.copy2(excel_path, backup_path)
            
            logger.info(f"Datos guardados en: {excel_path}")
            logger.info(f"Copia de seguridad en: {backup_path}")
            
            return excel_path, df
            
        except Exception as e:
            logger.error(f"Error guardando datos en Excel: {e}")
            raise

# ============================================================================
# APLICACIÓN PRINCIPAL MEJORADA
# ============================================================================

class DetectionApp:
    """Clase principal de la aplicación con arquitectura mejorada."""
    
    def __init__(self):
        self.root = None
        self.model_manager = YOLOModelManager()
        self.progress_window = None
        self.current_results = None
        
    def initialize(self):
        """Inicializa la aplicación."""
        try:
            # Configurar directorios
            DirectoryManager.initialize_directories()
            
            # Crear ventana principal
            self.root = Tk()
            UIManager.configure_window(self.root, "Havers Analysis - Detection App")
            
            # Cargar modelo
            if not self.model_manager.load_model():
                messagebox.showerror("Error", "No se pudo cargar el modelo YOLO.\nVerifica que el archivo de modelo esté disponible.")
                return False
            
            logger.info("Aplicación inicializada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando aplicación: {e}")
            return False
    
    def show_main_screen(self):
        """Muestra la pantalla principal mejorada."""
        UIManager.clear_window(self.root)
        
        # Frame principal
        main_frame = Frame(self.root, bg=config.BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título principal
        title = Label(main_frame, text="Havers Analysis", 
                     font=("Helvetica", 28, "bold"), 
                     fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR)
        title.pack(pady=(0, 10))
        
        # Subtítulo
        subtitle = Label(main_frame, text="Sistema Automatizado de Detección de Canales de Havers", 
                        font=("Helvetica", 14), 
                        fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR)
        subtitle.pack(pady=(0, 30))
        
        # Información del sistema
        info_frame = Frame(main_frame, bg=config.BACKGROUND_COLOR)
        info_frame.pack(pady=20)
        
        info_text = f"""
🔬 Modelo YOLO cargado: {os.path.basename(self.model_manager.model_path)}
💾 Uso de memoria: {MemoryManager.get_memory_usage():.1f} MB
🖥️ GPU disponible: {'Sí' if torch.cuda.is_available() else 'No'}
📊 Configuración: {config.NUM_SEGMENTS} segmentos, confianza {config.CONFIDENCE_THRESHOLD}
        """
        
        info_label = Label(info_frame, text=info_text, 
                          font=("Helvetica", 11), 
                          fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR,
                          justify="left")
        info_label.pack()
        
        # Botón principal
        load_button = Button(main_frame, text="Seleccionar Imagen Histológica", 
                           command=self.select_and_process_image)
        UIManager.configure_button(load_button)
        load_button.pack(pady=30)
        
        # Botón de resultados (si existen)
        if self.current_results:
            results_button = Button(main_frame, text="Ver Últimos Resultados", 
                                  command=self.show_results_screen)
            UIManager.configure_button(results_button)
            results_button.pack(pady=10)
    
    def select_and_process_image(self):
        """Selecciona y procesa una imagen con interfaz mejorada."""
        # Seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen Histológica",
            filetypes=[
                ("Imágenes", "*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.bmp"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("PNG", "*.png"),
                ("TIFF", "*.tiff;*.tif"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Validar imagen
        if not ImageProcessor.validate_image(file_path):
            messagebox.showerror("Error", "La imagen seleccionada no es válida o no se puede leer.")
            return
        
        # Confirmar procesamiento
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        response = messagebox.askyesno(
            "Confirmar Procesamiento",
            f"Archivo: {os.path.basename(file_path)}\n"
            f"Tamaño: {file_size:.1f} MB\n\n"
            f"¿Proceder con el análisis?\n"
            f"(Esto puede tomar varios minutos)"
        )
        
        if response:
            self.process_image_with_progress(file_path)
    
    def process_image_with_progress(self, image_path: str):
        """Procesa la imagen con barra de progreso mejorada."""
        try:
            # Mostrar ventana de progreso
            self.progress_window, progress_bar, status_label = UIManager.show_progress_dialog(
                self.root, "Analizando Imagen Histológica"
            )
            
            # Función de procesamiento en hilo separado
            def process_in_background():
                try:
                    # Paso 1: Validar y redimensionar
                    status_label.config(text="Validando y preparando imagen...")
                    self.progress_window.update()
                    
                    processed_path = ImageProcessor.resize_image_if_needed(image_path)
                    
                    # Paso 2: Segmentar imagen
                    status_label.config(text="Dividiendo imagen en segmentos...")
                    self.progress_window.update()
                    
                    segment_positions, width, height = ImageProcessor.divide_image_optimized(processed_path)
                    
                    # Paso 3: Procesar con YOLO
                    status_label.config(text="Ejecutando análisis con IA...")
                    self.progress_window.update()
                    
                    detections = self.model_manager.process_segments_batch(segment_positions)
                    
                    if not detections:
                        raise ValueError("No se detectaron canales de Havers en la imagen")
                    
                    # Paso 4: Guardar datos
                    status_label.config(text="Guardando resultados...")
                    self.progress_window.update()
                    
                    excel_path, df = DataManager.save_results_to_excel_enhanced(detections)
                    
                    # Paso 5: Generar visualizaciones
                    status_label.config(text="Generando visualizaciones...")
                    self.progress_window.update()
                    
                    viz_results = DataAnalyzer.generate_visualization_optimized(df, processed_path)
                    
                    # Combinar resultados
                    self.current_results = {
                        'excel_path': excel_path,
                        'processed_image_path': processed_path,
                        'original_image_path': image_path,
                        'dataframe': df,
                        **viz_results
                    }
                    
                    # Cerrar ventana de progreso
                    self.progress_window.destroy()
                    
                    # Mostrar resultados
                    self.show_results_screen()
                    
                except Exception as e:
                    if self.progress_window:
                        self.progress_window.destroy()
                    logger.error(f"Error en procesamiento: {e}")
                    messagebox.showerror("Error de Procesamiento", 
                                       f"Ocurrió un error durante el análisis:\n{str(e)}")
                    self.show_main_screen()
            
            # Ejecutar en hilo separado para no bloquear la UI
            import threading
            thread = threading.Thread(target=process_in_background)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            if self.progress_window:
                self.progress_window.destroy()
            logger.error(f"Error iniciando procesamiento: {e}")
            messagebox.showerror("Error", f"No se pudo iniciar el procesamiento: {e}")
    
    def show_results_screen(self):
        """Muestra los resultados con interfaz mejorada."""
        if not self.current_results:
            messagebox.showwarning("Sin Resultados", "No hay resultados para mostrar.")
            return
        
        UIManager.clear_window(self.root)
        
        # Crear notebook con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 1: Resumen
        self._create_summary_tab(notebook)
        
        # Pestaña 2: Estadísticas detalladas
        self._create_statistics_tab(notebook)
        
        # Pestaña 3: Acciones
        self._create_actions_tab(notebook)
        
        # Botón para volver
        back_button = Button(self.root, text="← Volver al Inicio", 
                           command=self.show_main_screen)
        UIManager.configure_button(back_button)
        back_button.pack(pady=10)
    
    def _create_summary_tab(self, notebook):
        """Crea la pestaña de resumen."""
        summary_frame = Frame(notebook, bg=config.BACKGROUND_COLOR)
        notebook.add(summary_frame, text="📊 Resumen")
        
        # Título
        title = Label(summary_frame, text="Resultados del Análisis", 
                     font=("Helvetica", 20, "bold"), 
                     fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR)
        title.pack(pady=20)
        
        # Métricas principales
        metrics_frame = Frame(summary_frame, bg=config.BACKGROUND_COLOR)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        results = self.current_results
        
        # Crear tarjetas de métricas
        metrics = [
            ("Canales Detectados", f"{results['count']:,}", "🔬"),
            ("Área Promedio", f"{results['avg_area']:.1f} px²", "📏"),
            ("Distancia Media", f"{results['avg_distance']:.1f} px", "📐"),
            ("Desv. Estándar", f"{results['std_area']:.1f} px²", "📊")
        ]
        
        for i, (label, value, icon) in enumerate(metrics):
            self._create_metric_card(metrics_frame, icon, label, value, i)
        
        # Información del archivo
        file_info = f"""
        📁 Archivo Original: {os.path.basename(results['original_image_path'])}
        💾 Tamaño Procesado: {os.path.getsize(results['processed_image_path']) / (1024*1024):.1f} MB
        📊 Excel Generado: {os.path.basename(results['excel_path'])}
        🎯 Rango de Áreas: {results['min_area']:.1f} - {results['max_area']:.1f} px²
        """
        
        info_label = Label(summary_frame, text=file_info, 
                          font=("Helvetica", 11), 
                          fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR,
                          justify="left")
        info_label.pack(pady=20)
    
    def _create_metric_card(self, parent, icon, label, value, index):
        """Crea una tarjeta de métrica."""
        card = Frame(parent, bg='#1a1a1a', relief="raised", bd=2)
        card.grid(row=index//2, column=index%2, padx=10, pady=10, sticky="ew")
        
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        # Contenido de la tarjeta
        icon_label = Label(card, text=icon, font=("Helvetica", 24), 
                          fg=config.TEXT_COLOR, bg='#1a1a1a')
        icon_label.pack(pady=(10, 5))
        
        value_label = Label(card, text=value, font=("Helvetica", 16, "bold"), 
                           fg=config.BUTTON_COLOR, bg='#1a1a1a')
        value_label.pack()
        
        label_label = Label(card, text=label, font=("Helvetica", 10), 
                           fg=config.TEXT_COLOR, bg='#1a1a1a')
        label_label.pack(pady=(0, 10))
    
    def _create_statistics_tab(self, notebook):
        """Crea la pestaña de estadísticas detalladas."""
        stats_frame = Frame(notebook, bg=config.BACKGROUND_COLOR)
        notebook.add(stats_frame, text="📈 Estadísticas")
        
        # Crear área de texto con scroll
        text_frame = Frame(stats_frame)
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        text_area = Text(text_frame, bg='#1a1a1a', fg=config.TEXT_COLOR, 
                        font=("Consolas", 11), wrap="word")
        scrollbar = Scrollbar(text_frame, command=text_area.yview)
        text_area.config(yscrollcommand=scrollbar.set)
        
        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generar reporte estadístico
        df = self.current_results['dataframe']
        report = self._generate_statistical_report(df)
        
        text_area.insert("1.0", report)
        text_area.config(state="disabled")
    
    def _generate_statistical_report(self, df: pd.DataFrame) -> str:
        """Genera un reporte estadístico detallado."""
        report = """
=================================================================
              REPORTE ESTADÍSTICO DETALLADO
              Análisis de Canales de Havers
=================================================================

ESTADÍSTICAS DESCRIPTIVAS
-------------------------
"""
        
        # Estadísticas básicas
        area_stats = df['Ellipse Area (pixels^2)'].describe()
        
        report += f"""
Total de canales detectados: {len(df):,}
Área promedio: {area_stats['mean']:.2f} px²
Mediana del área: {area_stats['50%']:.2f} px²
Desviación estándar: {area_stats['std']:.2f} px²
Área mínima: {area_stats['min']:.2f} px²
Área máxima: {area_stats['max']:.2f} px²
Rango intercuartílico: {area_stats['75%'] - area_stats['25%']:.2f} px²

DISTRIBUCIÓN POR CUARTILES
--------------------------
Q1 (25%): {area_stats['25%']:.2f} px²
Q2 (50%): {area_stats['50%']:.2f} px²
Q3 (75%): {area_stats['75%']:.2f} px²

ANÁLISIS DE DISTRIBUCIÓN ESPACIAL
---------------------------------
"""
        
        # Análisis por segmentos
        segment_counts = df['Segment ID'].value_counts().sort_index()
        
        report += f"""
Segmentos con detecciones: {len(segment_counts)} de {config.NUM_SEGMENTS}
Promedio de canales por segmento: {segment_counts.mean():.1f}
Segmento con más canales: {segment_counts.idxmax()} ({segment_counts.max()} canales)
Segmento con menos canales: {segment_counts.idxmin()} ({segment_counts.min()} canales)

DISTRIBUCIÓN POR CATEGORÍAS DE TAMAÑO
------------------------------------
"""
        
        # Categorización por área
        if 'Area Category' in df.columns:
            category_counts = df['Area Category'].value_counts()
            for category, count in category_counts.items():
                percentage = (count / len(df)) * 100
                report += f"{category}: {count} canales ({percentage:.1f}%)\n"
        
        report += f"""

MÉTRICAS DE CALIDAD
------------------
Coeficiente de variación: {(area_stats['std'] / area_stats['mean']) * 100:.1f}%
Distancia media entre canales: {self.current_results['avg_distance']:.2f} px

INFORMACIÓN TÉCNICA
------------------
Tiempo de procesamiento: {time.strftime('%Y-%m-%d %H:%M:%S')}
Umbral de confianza usado: {config.CONFIDENCE_THRESHOLD}
Número de segmentos procesados: {config.NUM_SEGMENTS}
Modelo utilizado: {os.path.basename(self.model_manager.model_path)}

=================================================================
"""
        
        return report
    
    def _create_actions_tab(self, notebook):
        """Crea la pestaña de acciones."""
        actions_frame = Frame(notebook, bg=config.BACKGROUND_COLOR)
        notebook.add(actions_frame, text="🛠️ Acciones")
        
        # Título
        title = Label(actions_frame, text="Acciones Disponibles", 
                     font=("Helvetica", 18, "bold"), 
                     fg=config.TEXT_COLOR, bg=config.BACKGROUND_COLOR)
        title.pack(pady=20)
        
        # Botones de acción
        button_frame = Frame(actions_frame, bg=config.BACKGROUND_COLOR)
        button_frame.pack(expand=True)
        
        buttons = [
            ("📊 Abrir Excel con Datos", lambda: self._open_file(self.current_results['excel_path'])),
            ("🗺️ Ver Mapa de Coordenadas", lambda: self._open_file(self.current_results['plot_path'])),
            ("🔥 Ver Mapa de Calor", lambda: self._open_file(self.current_results['heatmap_path'])),
            ("📁 Abrir Carpeta de Resultados", lambda: self._open_file(config.RESULTS_DIR)),
            ("💾 Exportar Reporte PDF", self._export_pdf_report),
            ("🔄 Procesar Nueva Imagen", self.select_and_process_image)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = Button(button_frame, text=text, command=command)
            UIManager.configure_button(btn)
            btn.pack(pady=10, padx=20, fill="x")
    
    def _open_file(self, file_path: str):
        """Abre un archivo con la aplicación predeterminada."""
        try:
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/macOS
                    import subprocess
                    subprocess.call(['xdg-open', file_path])
            else:
                messagebox.showerror("Error", f"Archivo no encontrado: {file_path}")
        except Exception as e:
            logger.error(f"Error abriendo archivo {file_path}: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
    
    def _export_pdf_report(self):
        """Exporta un reporte en PDF (función placeholder)."""
        messagebox.showinfo("Próximamente", 
                           "La exportación a PDF estará disponible en una futura actualización.")
    
    def run(self):
        """Ejecuta la aplicación principal."""
        if not self.initialize():
            return
        
        try:
            self.show_main_screen()
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")
            messagebox.showerror("Error Fatal", f"Error inesperado: {e}")
        finally:
            if self.root:
                self.root.destroy()

# ============================================================================
# FUNCIÓN MAIN MEJORADA
# ============================================================================

def main():
    """Función principal del programa mejorada."""
    try:
        # Verificar dependencias críticas
        if not torch.cuda.is_available():
            logger.warning("CUDA no disponible, usando CPU (procesamiento más lento)")
        
        # Crear y ejecutar aplicación
        app = DetectionApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en main: {e}")
        import traceback
        traceback.print_exc()
        
        # Mostrar error al usuario si es posible
        try:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error Fatal", 
                               f"La aplicación encontró un error fatal:\n{e}\n\n"
                               f"Consulta el archivo de log para más detalles.")
        except:
            pass

if __name__ == '__main__':
    main()
            