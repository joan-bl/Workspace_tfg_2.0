import cv2
import os
import shutil
import pandas as pd
from math import ceil, pi
from ultralytics import YOLO
import torch
from tkinter import Tk, Button, Text, Scrollbar, Canvas, Frame, Label, ttk, filedialog
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import io
import numpy as np

def configure_window(window, title):
    window.title(title)
    window.geometry("1000x1000")
    window.configure(bg='#001f3f')

def configure_button(button):
    # Define el aspecto visual del botón
    button.configure(
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 12),
        padx=10,
        pady=5,
        relief="raised",
        borderwidth=2
    )
    # Añadir efectos hover si se desea
    button.bind("<Enter>", lambda e: button.configure(bg="#45a049"))
    button.bind("<Leave>", lambda e: button.configure(bg="#4CAF50"))

def select_image(root):
    image_path = None  # Inicializa la variable
    
    def on_button_click():
        nonlocal image_path  # Usa nonlocal para modificar la variable del ámbito superior
        file_path = askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            image_path = file_path
            root.quit()
            for widget in root.winfo_children():
                widget.destroy()

    configure_window(root, "Select Image")
    title = Label(root, text="PhygitalBone 2.0", font=("Helvetica", 24), fg="white", bg="#001f3f")
    title.pack(pady=20)

    button = Button(root, text="Load Image", command=on_button_click)
    configure_button(button)
    button.pack(expand=True)

    root.mainloop()
    return image_path

def divide_and_save_image(image_path, output_dir, num_segments=150):
    """
    Divide una imagen en segmentos más pequeños y los guarda en el directorio especificado.
    """
    # Verificar si el directorio existe y eliminarlo si es necesario
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Leer la imagen
    print(f"Leyendo imagen desde: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: No se pudo cargar la imagen {image_path}")
        return None, None, None

    # Obtener dimensiones de la imagen
    print(f"Dimensiones de la imagen: {image.shape}")
    
    # Configurar la división
    cols = 15
    rows = ceil(num_segments / cols)
    segment_height = image.shape[0] // rows
    segment_width = image.shape[1] // cols
    
    print(f"Dividiendo en {rows}x{cols} segmentos")
    print(f"Tamaño de cada segmento: {segment_width}x{segment_height}")

    # Dividir y guardar
    segment_positions = []
    for i in range(rows):
        for j in range(cols):
            start_y = i * segment_height
            end_y = start_y + segment_height if i < rows - 1 else image.shape[0]
            start_x = j * segment_width
            end_x = start_x + segment_width if j < cols - 1 else image.shape[1]
            
            segment = image[start_y:end_y, start_x:end_x]
            segment_filename = f"segment_{i * cols + j + 1}.png"
            segment_path = os.path.join(output_dir, segment_filename)
            
            cv2.imwrite(segment_path, segment)
            print(f"Guardado segmento {i * cols + j + 1} en {segment_path}")
            
            segment_positions.append((start_x, start_y, i * cols + j + 1))

    print(f"Se guardaron {len(segment_positions)} segmentos en {output_dir}")
    return segment_positions, segment_width, segment_height

def calculate_box_centers_and_areas(boxes, start_x, start_y, segment_id):
    """
    Calcula los centros y áreas de las cajas de detección.
    """
    centers = []
    for box in boxes:
        xyxy = box.xyxy.clone().detach().cpu().view(1, 4)
        width = xyxy[0, 2] - xyxy[0, 0]
        height = xyxy[0, 3] - xyxy[0, 1]
        cx = start_x + (xyxy[0, 0] + xyxy[0, 2]) / 2
        cy = start_y + (xyxy[0, 1] + xyxy[0, 3]) / 2
        semi_major_axis = width / 2
        semi_minor_axis = height / 2
        ellipse_area = pi * semi_major_axis * semi_minor_axis  # Calcula el área de la elipse
        centers.append((cx, cy, segment_id, ellipse_area))
    return centers

def plot_centers(df, image_path):
    """
    Genera un gráfico de dispersión con los centros de los canales de Havers.
    """
    plt.figure(figsize=(10, 10))
    # Cargar la imagen inicial
    image = plt.imread(image_path)
    plt.imshow(image, extent=[0, image.shape[1], image.shape[0], 0], alpha=0.6)
    plt.scatter(df['Center X'], df['Center Y'], c='blue', marker='o', s=10)  # Puntos más pequeños
    plt.title('Mapa de coordenadas de canales de Havers')
    plt.xlabel('Center X')
    plt.ylabel('Center Y')
    plt.grid(True)
    plt.gca().invert_yaxis()  # Invertir el eje Y para que coincida con la representación de la imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def plot_heatmap(df, image_path):
    """
    Genera un mapa de calor para visualizar la densidad de canales de Havers.
    """
    plt.figure(figsize=(10, 10))
    # Generar el mapa de calor
    heatmap, xedges, yedges = np.histogram2d(df['Center X'], df['Center Y'], bins=(100, 100))
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    plt.imshow(heatmap.T, extent=extent, origin='lower', cmap='hot', alpha=0.6)
    plt.colorbar()
    # Cargar la imagen inicial con transparencia
    image = plt.imread(image_path)
    plt.imshow(image, extent=[0, image.shape[1], image.shape[0], 0], alpha=0.4)
    plt.title('Mapa de densidad de canales de Havers')
    plt.xlabel('Center X')
    plt.ylabel('Center Y')
    plt.grid(True)
    plt.gca().invert_yaxis()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def save_plot(buf, title):
    """
    Guarda un gráfico en un archivo.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
        title=title
    )
    if file_path:
        with open(file_path, 'wb') as f:
            f.write(buf.getbuffer())

def calculate_distance_matrix(centers_df):
    """
    Calcula la distancia media entre los centros de los canales de Havers.
    """
    distances = []
    points = centers_df[['Center X', 'Center Y']].values
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = np.sqrt(((points[i] - points[j]) ** 2).sum())
            distances.append(dist)
    return np.mean(distances) if distances else 0

def display_results(root, excel_path, plot_buf, heatmap_buf, avg_area, count_havers, avg_distance):
    """
    Muestra los resultados del análisis en una interfaz gráfica.
    """
    for widget in root.winfo_children():
        widget.destroy()
    configure_window(root, "Results")
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Crear pestañas
    frame1 = Frame(notebook, bg='#001f3f')
    frame2 = Frame(notebook, bg='#001f3f')
    frame3 = Frame(notebook, bg='#001f3f')
    frame4 = Frame(notebook, bg='#001f3f')
    notebook.add(frame1, text="Coordinates")
    notebook.add(frame2, text="Plot")
    notebook.add(frame3, text="Analysis")
    notebook.add(frame4, text="Heatmap")

    # Pestaña de coordenadas
    text_area = Text(frame1, bg='#001f3f', fg="white", insertbackground="white")
    text_area.pack(side='left', fill='both', expand=True)
    scrollbar = Scrollbar(frame1, command=text_area.yview)
    scrollbar.pack(side='right', fill='y')
    text_area.config(yscrollcommand=scrollbar.set)

    # Mostrar contenido del archivo de Excel
    with pd.ExcelFile(excel_path) as xls:
        df = pd.read_excel(xls)
        text_area.insert('1.0', df.to_string())

    # Pestaña de gráfico
    plot_image = Image.open(plot_buf)
    plot_photo = ImageTk.PhotoImage(plot_image)
    plot_canvas = Canvas(frame2, bg='#001f3f')
    plot_canvas.pack(fill='both', expand=True)
    plot_canvas.create_image(500, 500, image=plot_photo)  # Ubicación central de la imagen
    plot_canvas.image = plot_photo  # Mantener una referencia para evitar la recolección de basura

    # Botón para guardar el gráfico
    save_plot_button = Button(frame2, text="Guardar Gráfico", 
                             command=lambda: save_plot(plot_buf, "Guardar Mapa de Coordenadas"))
    configure_button(save_plot_button)
    save_plot_button.pack(side='bottom', pady=10)

    # Pestaña de análisis
    analysis_text = Text(frame3, bg='#001f3f', fg="white", insertbackground="white", font=("Helvetica", 14))
    analysis_text.pack(fill='both', expand=True)
    analysis_text.insert('1.0', f"""
    Análisis de la imagen:
    
    Número de canales de Havers detectados: {count_havers}
    
    Área promedio de los canales: {avg_area:.2f} pixels²
    
    Distancia media entre canales: {avg_distance:.2f} pixels
    """)

    # Pestaña de mapa de calor
    heatmap_image = Image.open(heatmap_buf)
    heatmap_photo = ImageTk.PhotoImage(heatmap_image)
    heatmap_canvas = Canvas(frame4, bg='#001f3f')
    heatmap_canvas.pack(fill='both', expand=True)
    heatmap_canvas.create_image(500, 500, image=heatmap_photo)
    heatmap_canvas.image = heatmap_photo

    # Botón para guardar el mapa de calor
    save_heatmap_button = Button(frame4, text="Guardar Mapa de Calor", 
                                command=lambda: save_plot(heatmap_buf, "Guardar Mapa de Calor"))
    configure_button(save_heatmap_button)
    save_heatmap_button.pack(side='bottom', pady=10)

    # Mantener la ventana abierta
    root.mainloop()

def main():
    """
    Función principal del programa.
    """
    # Crear ventana principal
    root = Tk()
    
    # Selección de imagen
    image_path = select_image(root)
    if not image_path:
        print("No se seleccionó ninguna imagen.")
        root.destroy()
        return
    
    # Imprimir la ruta de la imagen para depuración
    print(f"Imagen seleccionada: {image_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(image_path):
        print(f"ERROR: El archivo {image_path} no existe.")
        root.destroy()
        return
    
    # Actualizar la ventana para mostrar el progreso
    root = Tk()  # Crear una nueva ventana ya que la anterior se cerró
    configure_window(root, "Processing")
    Label(root, text="Processing, please wait...", font=("Helvetica", 16), fg="white", bg='#001f3f').pack(expand=True)
    root.update()
    
    # Directorios para imágenes segmentadas y resultados
    images_dir = 'imagenes_sep'
    output_dir = 'resultado_img'
    confidence_threshold = 0.4
    
    # Crear directorios para segmentos y resultados
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Dividir la imagen en segmentos
        print(f"Dividiendo imagen {image_path} en segmentos...")
        segment_positions, segment_width, segment_height = divide_and_save_image(image_path, images_dir)
        if segment_positions is None:
            print("Error al dividir la imagen.")
            root.destroy()
            return
        
        # Cargar modelo YOLO
        print("Cargando modelo YOLO...")
        model_path = r"C:\Users\joanb\OneDrive\Escritorio\TFG\workspace\osteona\best.pt"
        print(f"Ruta del modelo: {model_path}")
        
        if not os.path.exists(model_path):
            print(f"ERROR: El archivo del modelo {model_path} no existe.")
            root.destroy()
            return
            
        model = YOLO(model_path)
        
        # Obtener lista de archivos de segmentos
        segment_files = sorted(
            [f for f in os.listdir(images_dir) if f.endswith('.png')],
            key=lambda x: int(x.split('_')[-1].split('.')[0]) if '_' in x and x.split('_')[-1].split('.')[0].isdigit() else 0
        )
        
        if not segment_files:
            print(f"No se encontraron archivos de segmentos en {images_dir}")
            root.destroy()
            return
            
        print(f"Se encontraron {len(segment_files)} archivos de segmentos")
        
        # Lista para almacenar los centros y áreas de las cajas delimitadoras
        box_centers_and_areas = []
        
        # Analizar cada segmento
        print("Analizando segmentos con el modelo YOLO...")
        for idx, (start_x, start_y, segment_id) in enumerate(segment_positions):
            segment_filename = f"segment_{segment_id}.png"
            segment_path = os.path.join(images_dir, segment_filename)
            
            if not os.path.exists(segment_path):
                print(f"Advertencia: Archivo de segmento no encontrado: {segment_path}")
                continue
                
            print(f"Analizando segmento {segment_id}: {segment_path}")
            
            # Realizar detección con YOLO
            results = model(segment_path, conf=confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                print(f"Segmento {segment_id}: Se detectaron {len(boxes)} canales de Havers")
                centers = calculate_box_centers_and_areas(boxes, start_x, start_y, segment_id)
                box_centers_and_areas.extend(centers)

                # Guardar imagen con anotaciones
                annotated_img = result.plot()
                output_path = os.path.join(output_dir, f"result_{segment_id}.png")
                cv2.imwrite(output_path, annotated_img)
        
        # Si no se detectaron canales
        if not box_centers_and_areas:
            print("No se detectaron canales de Havers.")
            root.destroy()
            return
        
        print(f"Se detectaron un total de {len(box_centers_and_areas)} canales de Havers")
        
        # Generar DataFrame con coordenadas y áreas
        df = pd.DataFrame(box_centers_and_areas, columns=['Center X', 'Center Y', 'Segment ID', 'Ellipse Area (pixels^2)'])
        excel_path = 'bounding_box_centers.xlsx'
        df.to_excel(excel_path, index=False)
        print(f"Centros y áreas de las cajas delimitadoras guardados en {excel_path}")
        
        # Generar visualizaciones
        print("Generando visualizaciones...")
        plot_buf = plot_centers(df, image_path)
        heatmap_buf = plot_heatmap(df, image_path)
        avg_area = df['Ellipse Area (pixels^2)'].mean()
        count_havers = df.shape[0]
        avg_distance = calculate_distance_matrix(df)
        
        # Mostrar resultados
        print("Mostrando resultados...")
        display_results(root, excel_path, plot_buf, heatmap_buf, avg_area, count_havers, avg_distance)
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()

if __name__ == '__main__':
    main()