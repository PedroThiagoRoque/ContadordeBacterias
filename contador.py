import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime

# Configuração inicial do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o tema do sistema (light/dark)
ctk.set_default_color_theme("blue")  # Tema padrão

# Variáveis globais para controle do estado da imagem e parâmetros ajustáveis
image_path = None
stages = []
stage_names = []
current_stage = 0
blur_value = 5
threshold_value = 150
kernel_size = 2
morph_iterations = 1

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
        save_image_btn.configure(state="disabled")  # Desabilitar botão de salvar
        messagebox.showinfo("Imagem carregada", "Imagem carregada com sucesso!")
        
        # Resetar os estágios e nomes
        stages = []
        stage_names = []
        current_stage = 0

        # Processar e salvar cada estágio da transformação
        process_image_stages()

# Função para processar e armazenar os diferentes estágios de processamento
def process_image_stages():
    global stages, stage_names, image_path, blur_value, threshold_value, kernel_size, morph_iterations

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
    blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
    stages.append(cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append(f"Imagem Suavizada (Blur: {blur_value})")

    # 4. Aplicar limiarização (thresholding)
    _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY_INV)
    stages.append(cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append(f"Limiarização (Threshold: {threshold_value})")

    # 5. Operações morfológicas (remoção de ruídos e conexão de áreas quebradas)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=morph_iterations)  # Abertura
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel, iterations=morph_iterations)  # Fechamento
    stages.append(cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR))  # Convertendo para BGR para exibição
    stage_names.append(f"Operações Morfológicas (Kernel: {kernel_size}, Iterações: {morph_iterations})")

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

    # Habilitar botão de salvar imagem na etapa final
    save_image_btn.configure(state="normal")

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

# Função para salvar a imagem final com data e hora
def save_image():
    if stages and current_stage == len(stages) - 1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_image_path = f"output_final_{timestamp}.jpg"
        cv2.imwrite(output_image_path, stages[-1])
        messagebox.showinfo("Imagem Salva", f"Imagem salva como {output_image_path}")

# Função para atualizar os parâmetros a partir dos sliders
def update_parameters():
    global blur_value, threshold_value, kernel_size, morph_iterations
    blur_value = int(blur_slider.get())
    threshold_value = int(threshold_slider.get())
    kernel_size = int(kernel_slider.get())
    morph_iterations = int(iteration_slider.get())
    process_image_stages()

# Interface gráfica com CustomTkinter
app = ctk.CTk()
app.title("Contador de Bactérias - Placa de Petri")
app.geometry("700x700")

title_label = ctk.CTkLabel(app, text="Contador de Bactérias - Placa de Petri", font=("Arial", 20))
title_label.pack(pady=20)

# Frame lateral (menu de parâmetros)
side_menu = ctk.CTkFrame(app, width=250, height=600, corner_radius=10)
side_menu.pack(side="left", padx=20, pady=0)

# Botão para selecionar imagem
select_image_btn = ctk.CTkButton(side_menu, text="Selecionar Imagem", command=load_image)
select_image_btn.pack(pady=20)

# Sliders para ajuste dos parâmetros com feedback de valor
# Blur
blur_label = ctk.CTkLabel(side_menu, text="Blur")
blur_label.pack()
blur_value_label = ctk.CTkLabel(side_menu, text=f"{blur_value}")  # Label para mostrar o valor
blur_slider = ctk.CTkSlider(side_menu, from_=1, to=21, number_of_steps=10, 
                            command=lambda val: [blur_value_label.configure(text=f"{int(val)}"), update_parameters()])
blur_slider.set(blur_value)
blur_slider.pack(pady=10)
blur_value_label.pack()  # Mostrar o valor ao lado do slider

# Threshold
threshold_label = ctk.CTkLabel(side_menu, text="Threshold")
threshold_label.pack()
threshold_value_label = ctk.CTkLabel(side_menu, text=f"{threshold_value}")  # Label para mostrar o valor
threshold_slider = ctk.CTkSlider(side_menu, from_=0, to=255, number_of_steps=255, 
                                 command=lambda val: [threshold_value_label.configure(text=f"{int(val)}"), update_parameters()])
threshold_slider.set(threshold_value)
threshold_slider.pack(pady=10)
threshold_value_label.pack()  # Mostrar o valor ao lado do slider

# Kernel Size
kernel_label = ctk.CTkLabel(side_menu, text="Kernel Size")
kernel_label.pack()
kernel_value_label = ctk.CTkLabel(side_menu, text=f"{kernel_size}")  # Label para mostrar o valor
kernel_slider = ctk.CTkSlider(side_menu, from_=1, to=10, number_of_steps=10, 
                              command=lambda val: [kernel_value_label.configure(text=f"{int(val)}"), update_parameters()])
kernel_slider.set(kernel_size)
kernel_slider.pack(pady=10)
kernel_value_label.pack()  # Mostrar o valor ao lado do slider

# Morph Iterations
iteration_label = ctk.CTkLabel(side_menu, text="Morph Iterations")
iteration_label.pack()
iteration_value_label = ctk.CTkLabel(side_menu, text=f"{morph_iterations}")  # Label para mostrar o valor
iteration_slider = ctk.CTkSlider(side_menu, from_=1, to=10, number_of_steps=10, 
                                 command=lambda val: [iteration_value_label.configure(text=f"{int(val)}"), update_parameters()])
iteration_slider.set(morph_iterations)
iteration_slider.pack(pady=10)
iteration_value_label.pack()  # Mostrar o valor ao lado do slider


# Container de imagem e controle de etapas (à direita)
image_frame = ctk.CTkFrame(app, width=800, height=600)
image_frame.pack(side="left", padx=0, pady=0)

# Label para mostrar a imagem carregada
image_label = ctk.CTkLabel(image_frame, width=400, height=400, text="")
image_label.pack(pady=10)

# Label para mostrar o nome do estágio atual
stage_label = ctk.CTkLabel(image_frame, text="", font=("Arial", 16))
stage_label.pack(pady=10)

# Botões para avançar e salvar a imagem final
button_frame = ctk.CTkFrame(image_frame)
button_frame.pack(pady=20)

next_stage_btn = ctk.CTkButton(button_frame, text="Avançar", command=next_stage)
next_stage_btn.grid(row=0, column=0, padx=10)

save_image_btn = ctk.CTkButton(button_frame, text="Salvar Imagem", command=save_image, state="disabled")
save_image_btn.grid(row=0, column=1, padx=10)

# Loop da interface
app.mainloop()
