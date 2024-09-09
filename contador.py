import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime

# Configuração inicial do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o tema do sistema (light/dark)
ctk.set_default_color_theme("blue")  # Tema padrão

# Variáveis globais para controle do estado da imagem
image_path = None
stages = []
stage_names = []
current_stage = 0

# Função para carregar e mostrar a imagem original
def load_image():
    global image_path, stages, stage_names, current_stage
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        image_path = file_path
        img = Image.open(image_path)
        img.thumbnail((400, 400))  # Ajustar o tamanho da imagem para visualização
        img = ImageTk.PhotoImage(img)
        image_label.configure(image=img)
        image_label.image = img
        stage_label.configure(text="Imagem Original")
        messagebox.showinfo("Imagem carregada", "Imagem carregada com sucesso!")
        
        # Resetar os estágios e nomes
        stages = []
        stage_names = []
        current_stage = 0

        # Processar e salvar cada estágio da transformação
        process_image_stages()

# Função para processar e armazenar os diferentes estágios de processamento
def process_image_stages():
    global stages, stage_names, image_path

    # Carregar a imagem usando OpenCV
    image = cv2.imread(image_path)
    
    # 1. Adicionar a imagem original ao estágio
    stages.append(image)
    stage_names.append("Imagem Original")

    # 2. Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    stages.append(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))  # Convertendo de volta para BGR para exibição
    stage_names.append("Escala de Cinza")

    # 3. Aplicar filtro Gaussiano para suavizar
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    stages.append(cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append("Imagem Suavizada (Filtro Gaussiano)")

    # 4. Aplicar limiarização (thresholding)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    stages.append(cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append("Limiarização (Thresholding)")

    # 5. Operações morfológicas (remoção de ruídos e conexão de áreas quebradas)
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)  # Abertura para remover pequenos ruídos
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel, iterations=1)  # Fechamento para conectar áreas quebradas
    stages.append(cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append("Operações Morfológicas")

    # 6. Encontrar contornos na imagem e adicionar a contagem de objetos
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_image = cv2.drawContours(image.copy(), contours, -1, (0, 255, 0), 2)
    
    # Contar o número de objetos detectados
    num_objects = len(contours)
    
    # Adicionar o número de objetos detectados à imagem
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(contour_image, f'Objetos Detectados: {num_objects}', (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Adicionar ao estágio e ao nome
    stages.append(contour_image)
    stage_names.append(f"Contornos Detectados - Objetos: {num_objects}")

    # Salvar a imagem com data e hora para evitar sobreescrita
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_image_path = f"output_contours_{timestamp}.jpg"
    cv2.imwrite(output_image_path, contour_image)
    messagebox.showinfo("Imagem salva", f"A imagem foi salva como {output_image_path}")

    # Exibir o primeiro estágio (imagem original)
    display_current_stage()

# Função para exibir o estágio atual
def display_current_stage():
    global current_stage, stages, stage_names
    if stages and 0 <= current_stage < len(stages):
        img = stages[current_stage]
        img_resized = cv2.resize(img, (400, 400))  # Redimensionar para caber no label
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)))
        image_label.configure(image=img_tk)
        image_label.image = img_tk
        stage_label.configure(text=stage_names[current_stage])  # Atualiza o label com o nome do estágio

# Função para avançar para o próximo estágio
def next_stage():
    global current_stage
    if current_stage < len(stages) - 1:
        current_stage += 1
        display_current_stage()
    else:
        messagebox.showinfo("Fim", "Você já visualizou todas as etapas do processamento.")

# Interface gráfica com CustomTkinter
app = ctk.CTk()
app.title("Contador de Bactérias - Placa de Petri")
app.geometry("600x700")

# Título
title_label = ctk.CTkLabel(app, text="Contador de Bactérias - Placa de Petri", font=("Arial", 20))
title_label.pack(pady=20)

# Label para mostrar a imagem carregada
image_label = ctk.CTkLabel(app, width=400, height=400, text="")
image_label.pack(pady=10)

# Label para mostrar o nome do estágio atual
stage_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
stage_label.pack(pady=10)

# Botão para selecionar imagem
select_image_btn = ctk.CTkButton(app, text="Selecionar Imagem", command=load_image)
select_image_btn.pack(pady=10)

# Botão para avançar para o próximo estágio
next_stage_btn = ctk.CTkButton(app, text="Avançar", command=next_stage)
next_stage_btn.pack(pady=10)

# Loop da interface
app.mainloop()
