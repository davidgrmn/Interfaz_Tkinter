import customtkinter as ctk
import numpy as np
import picturebasics as ptb
import matplotlib.pyplot as plt
from tkinter import filedialog
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==============================================================
# VARIABLES GLOBALES
# ==============================================================
imagen_original = None        # Imagen principal cargada
imagen_original_copy = None   # Copia para revertir cambios
imagen_aux = None             # Imagen secundaria para fusión
zoom_flag = False             # Control del zoom


# ==============================================================
# FUNCIONES PRINCIPALES
# ==============================================================

# Abre imagen principal
def abrir_imagen():
    global imagen_original, imagen_original_copy
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"), ("Todos", "*.*")]
    )
    if not ruta:
        return
    imagen_original = Image.open(ruta).resize((500, 700))
    imagen_original_copy = imagen_original.copy()
    mostrar_imagen(imagen_original)

# Abre imagen auxiliar (para fusión)
def abrir_imagen_aux():
    global imagen_aux
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"), ("Todos", "*.*")]
    )
    if not ruta:
        return
    imagen_aux = Image.open(ruta).resize((500,700))
    foto = ctk.CTkImage(imagen_aux, size=(125, 125))
    lbl_aux.configure(image=foto)
    lbl_aux.image = foto 

# Muestra imagen en el visor principal
def mostrar_imagen(img):
    foto = ctk.CTkImage(img, size=(500, 700))
    lbl.configure(image=foto)
    lbl.image = foto  

# Activa modo zoom con clic en la imagen
def activar_zoom():
    global zoom_activo
    zoom_activo = True
    lbl.bind("<Button-1>", ejecutar_zoom)

# Revierte a la imagen original
def rollback():
    global imagen_original, imagen_original_copy
    if imagen_original is None:
        return 
    imagen_original = imagen_original_copy.copy()
    mostrar_imagen(imagen_original)

# Guarda la imagen modificada
def save():
    global imagen_original
    if imagen_original is None:
        return
    imagen_original.save("imagen_modificada.jpg")


# ==============================================================
# FUNCIONES DE BRILLO
# ==============================================================

# Brillo general
def aplicar_brillo_slider():
    global imagen_original
    if imagen_original is None:
        return
    val = slider_brillo.get()
    lbl_valor_brillo.configure(text=str(val))
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.bright(img_np, val)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

# Brillo por canal RGB
def aplicar_brillo_slider_layers():
    global imagen_original
    if imagen_original is None:
        return
    val_r, val_g, val_b = slider_r.get(), slider_g.get(), slider_b.get()
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.bright_canal(img_np, val_r, val_g, val_b)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)


# ==============================================================
# FUNCIONES DE BINARIZACIÓN Y RESOLUCIÓN
# ==============================================================

# Aplica binarización con umbral del slider
def aplicar_binarizacion_slider():
    global imagen_original
    if imagen_original is None:
        return
    val = slider_binarizar.get()
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.binary(img_np, val)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

# Reduce la resolución según el factor indicado
def reducir_res_btn():
    global imagen_original
    if imagen_original is None:
        return
    val = int(entry_resr.get())
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.res_reducer(img_np, val)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)


# ==============================================================
# FUNCIONES DE ZOOM, ROTACIÓN, CORTE Y FUSIÓN
# ==============================================================

# Aplica zoom al hacer clic en la imagen
def ejecutar_zoom(event):
    global zoom_activo, imagen_original
    if not zoom_activo or imagen_original is None:
        return
    x_click, y_click = event.x, event.y
    img_np = np.array(imagen_original)
    zoomed = ptb.zoom(img_np, x_click, y_click)
    imagen_original = Image.fromarray(zoomed.astype(np.uint8))
    mostrar_imagen(imagen_original)
    zoom_activo = False
    lbl.unbind("<Button-1>")

# Fusión entre dos imágenes con factor ingresado
def fusion_btn():
    global imagen_original, imagen_aux
    if imagen_original is None or imagen_aux is None:
        return
    factor = float(entry_fus.get())
    img_np = np.array(imagen_original, dtype=np.float32)
    img_aux_np = np.array(imagen_aux, dtype=np.float32)
    img_np = ptb.fusion(img_np, img_aux_np, factor)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

# Recorte de imagen según coordenadas
def cut_img():
    global imagen_original
    if imagen_original is None:
        return
    x_1, y_1, x_2, y_2 = int(entry_x1.get()), int(entry_y1.get()), int(entry_x2.get()), int(entry_y2.get())
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.cut(img_np, x_1, y_1, x_2, y_2)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

# Rotación manual según ángulo
def rotate():
    global imagen_original
    if imagen_original is None:
        return
    angle = int(entry_angle.get())
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.rotar_manual(img_np, angle)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)


# ==============================================================
# HISTOGRAMA
# ==============================================================

def mostrar_histograma():
    if imagen_original is None:
        return
    fig = ptb.generar_histograma(imagen_original)
    for widget in frame_hist.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_hist)
    canvas.draw()
    canvas.get_tk_widget().pack()
    plt.close(fig)


# ==============================================================
# CONTRASTE Y CAPAS
# ==============================================================

def contraste_log():
    global imagen_original
    if imagen_original is None:
        return
    factor = slider_contraste_light.get()
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.contrast_logarithmic(img_np, factor)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

def contraste_exp():
    global imagen_original
    if imagen_original is None:
        return
    factor = slider_contraste_dark.get()
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.contrast_exponential(img_np, factor)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

# Muestra capas RGB o CMYK
def layers(capa):
    global imagen_original
    if imagen_original is None:
        return
    img_np = np.array(imagen_original, dtype=np.float32)
    if capa in ["r","g","b"]:
        img_np = ptb.layer(img_np, {"r":0,"g":1,"b":2}[capa])
    else:
        img_np = ptb.layer_cmyk(img_np, capa)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)


# ==============================================================
# ESCALA DE GRISES Y NEGATIVO
# ==============================================================

def btn_average_gray():
    global imagen_original
    if imagen_original is None:
        return
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.get_average_gray(img_np)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

def luminosity_gray():
    global imagen_original
    if imagen_original is None:
        return
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.get_luminosity_gray(img_np)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)

def negative():
    global imagen_original
    if imagen_original is None:
        return
    img_np = np.array(imagen_original, dtype=np.float32)
    img_np = ptb.negative(img_np)
    imagen_original = Image.fromarray(img_np.astype(np.uint8))
    mostrar_imagen(imagen_original)


# ==============================================================
# INTERFAZ GRÁFICA (UI)
# ==============================================================

root = ctk.CTk()
root.title("Visor de imágenes")
root.geometry("1280x720")

# Botones principales: abrir, revertir, guardar
btn = ctk.CTkButton(root, text="Abrir imagen...", command=abrir_imagen)
btn.grid(row=0, column=0, pady=10, padx=10)
btn_rollback = ctk.CTkButton(root, text="Revertir cambios", fg_color="red", command=rollback)
btn_rollback.place(x=10, y=680)
btn_save = ctk.CTkButton(root, text="Guardar cambios", fg_color="green", command=save)
btn_save.place(x=200, y=10)

# Tabs de funciones
tabview = ctk.CTkTabview(root, width=650, height=600)
tabview.place(x=10, y=60)
tab_basicas = tabview.add("Básicas")
tab_color = tabview.add("Color")
tab_fusion = tabview.add("Fusión")
tab_hist = tabview.add("Histograma")
tab_layers = tabview.add("Capas")


# ----------------------------------------------------------------
# SECCIÓN COLOR
# ----------------------------------------------------------------

# brillo general
lbl_brillo = ctk.CTkLabel(tab_color, text="Brillo:", font=("Arial", 24, "bold"))
lbl_brillo.grid(row=0, column=0, sticky="w")

lbl_valor_brillo = ctk.CTkLabel(tab_color, text="0")
lbl_valor_brillo.grid(row=1, column=1, sticky="w")

slider_brillo = ctk.CTkSlider(tab_color, from_=-100, to=100)
slider_brillo.grid(row=1, column=0,pady=15)

ctk.CTkButton(tab_color,text="Aplicar brillo",command=aplicar_brillo_slider).place(x=238,y=38)


# brillo por canal
lbl_brillo_2 = ctk.CTkLabel(tab_color, text="Brillo por capas:", font=("Arial", 24, "bold"))
lbl_brillo_2.grid(row=2, column=0, sticky="w")

ctk.CTkLabel(tab_color, text="R", text_color="red").grid(row=3, column=1, sticky="w",padx=10)
ctk.CTkLabel(tab_color, text="G", text_color="green").grid(row=4, column=1,sticky="w",padx=10)
ctk.CTkLabel(tab_color, text="B", text_color="blue").grid(row=5, column=1, sticky="w",padx=10)

slider_r = ctk.CTkSlider(tab_color, from_=-150, to=150)
slider_r.grid(row=3, column=0)

slider_g = ctk.CTkSlider(tab_color, from_=-150, to=150)
slider_g.grid(row=4, column=0)
slider_b = ctk.CTkSlider(tab_color, from_=-150, to=150)
slider_b.grid(row=5, column=0)

btn_apply_bright_canal = ctk.CTkButton(tab_color, text="Aplicar brillo",width=80, command=aplicar_brillo_slider_layers)
btn_apply_bright_canal.place(x=235,y=132)


# binarización
ctk.CTkLabel(tab_color, text="Binarización:", font=("Arial", 24, "bold")).grid(row=10, column=0, sticky="w")
slider_binarizar = ctk.CTkSlider(tab_color, from_=0, to=1)
slider_binarizar.grid(row=11, column=0, sticky="w",pady=(0,15))

btn_bin = ctk.CTkButton(tab_color,text="Aplicar binarizacion",command=aplicar_binarizacion_slider)
btn_bin.grid(row=11,column=1)



# grayscale
ctk.CTkLabel(tab_color, text="Grayscale:", font=("Arial", 24, "bold")).grid(row=12, column=0, sticky="w",pady=(0,15))
btn_average = ctk.CTkButton(tab_color, text="Average", command=btn_average_gray)
btn_average.grid(row=13, column=0, sticky="w",pady=(0,15))
btn_luminosity_gray = ctk.CTkButton(tab_color, text="Luminosity", command=luminosity_gray)
btn_luminosity_gray.grid(row=13, column=1, sticky="w",pady=(0,15))


# negativo
ctk.CTkLabel(tab_color, text="Negativo:", font=("Arial", 24, "bold")).grid(row=14, column=0, sticky="w",pady=(0,15))
btn_negative = ctk.CTkButton(tab_color, text="Aplicar negativo", command=negative)
btn_negative.grid(row=15, column=0, sticky="w")


# contrastes
ctk.CTkLabel(tab_color, text="Contrastes:", font=("Arial", 24, "bold")).grid(row=7, column=0, sticky="w")

slider_contraste_light = ctk.CTkSlider(tab_color, from_=0.5, to=5.0)
slider_contraste_light.grid(row=8, column=0)
ctk.CTkLabel(tab_color, text="Claro (Logarítmico)").grid(row=8, column=1, sticky="w")

slider_contraste_dark = ctk.CTkSlider(tab_color, from_=0.2, to=3.0)
slider_contraste_dark.grid(row=9, column=0,pady=(0,15))
ctk.CTkLabel(tab_color, text="Oscuro (Exponencial)").grid(row=9, column=1, sticky="w", pady=(0,15))

btn_cons_light = ctk.CTkButton(tab_color,text="Aplicar Claro",command=contraste_log)
btn_cons_light.grid(row=8,column=2,sticky="w")

btn_cons_dark = ctk.CTkButton(tab_color,text="Aplicar Oscuro",command=contraste_exp)
btn_cons_dark.grid(row=9,column=2,sticky="w")




# ----------------------------------------------------------------
# SECCIÓN CAPAS
# ----------------------------------------------------------------
ctk.CTkLabel(tab_layers, text="RGB:", font=("Arial", 24, "bold")).grid(row=0, column=0, sticky="w",pady=(0,15))
capa_roja_btn = ctk.CTkButton(tab_layers,text="",fg_color="#ff4d4d",command=lambda: layers("r"))
capa_roja_btn.grid(row=1,column=0,padx=(0,15),pady=(0,40))
capa_verde_btn = ctk.CTkButton(tab_layers,text="",fg_color="#4dff4d",command=lambda: layers("g"))
capa_verde_btn.grid(row=1,column=1,padx=15,pady=(0,40))
capa_azul_btn = ctk.CTkButton(tab_layers,text="",fg_color="#4d4dff",command=lambda: layers("b"))
capa_azul_btn.grid(row=1,column=2,pady=(0,40),padx=15)

ctk.CTkLabel(tab_layers, text="CMYK:", font=("Arial", 24, "bold")).grid(row=2, column=0, sticky="w", pady=(0,15))
capa_celeste_btn = ctk.CTkButton(tab_layers,text="",fg_color="#00ffff",command=lambda: layers("c"))
capa_celeste_btn.grid(row=3,column=0,padx=(0,15))
capa_magenta_btn = ctk.CTkButton(tab_layers,text="",fg_color="#ff00ff",command=lambda: layers("m"))
capa_magenta_btn.grid(row=3,column=1,padx=15)
capa_amarilla_btn = ctk.CTkButton(tab_layers,text="",fg_color="#ffff00",command=lambda: layers("y"))
capa_amarilla_btn.grid(row=3,column=2,padx=15)




# ----------------------------------------------------------------
# SECCIÓN BASICAS
# ----------------------------------------------------------------

#cut
ctk.CTkLabel(tab_basicas, text="Recorte:", font=("Arial", 24, "bold")).grid(row=0, column=0, sticky="w")
ctk.CTkLabel(tab_basicas,text="X1:").grid(row=1,column=0,pady=15)
entry_x1 = ctk.CTkEntry(tab_basicas)
entry_x1.grid(row=1,column=1,pady=15)

ctk.CTkLabel(tab_basicas,text="Y1:").grid(row=1,column=2)
entry_y1 = ctk.CTkEntry(tab_basicas)
entry_y1.grid(row=1,column=3,padx=(0,5))

ctk.CTkLabel(tab_basicas,text="X2:").grid(row=2,column=0)
entry_x2 = ctk.CTkEntry(tab_basicas)
entry_x2.grid(row=2,column=1)

ctk.CTkLabel(tab_basicas,text="Y2:").grid(row=2,column=2)
entry_y2 = ctk.CTkEntry(tab_basicas)
entry_y2.grid(row=2,column=3)

cut_btn = ctk.CTkButton(tab_basicas,text="Cut",command=cut_img)
cut_btn.grid(row=1,column=4)

#rotate
ctk.CTkLabel(tab_basicas, text="Rotar:", font=("Arial", 24, "bold")).grid(row=3, column=0, sticky="w")
ctk.CTkLabel(tab_basicas,text="Angulo:").grid(row=4,column=0,pady=15)
entry_angle = ctk.CTkEntry(tab_basicas)
entry_angle.grid(row=4,column=1)

rotate_btn = ctk.CTkButton(tab_basicas,text="Apply Rotation",command=rotate)
rotate_btn.grid(row=4,column=2)

#res reducer
ctk.CTkLabel(tab_basicas, text="Res Reducer:", font=("Arial", 24, "bold")).grid(row=5, column=0, sticky="w")
ctk.CTkLabel(tab_basicas,text="Factor:").grid(row=6,column=0)

entry_resr = ctk.CTkEntry(tab_basicas)
entry_resr.grid(row=6,column=1,padx=15)

btn_res = ctk.CTkButton(tab_basicas,text="Aplicar reduccion",command=reducir_res_btn)
btn_res.grid(row=6,column=2)

#zoom
ctk.CTkLabel(tab_basicas, text="Zoom:", font=("Arial", 24, "bold")).grid(row=7, column=0, sticky="w")
btn_zoom = ctk.CTkButton(tab_basicas,text="Aplicar zoom..",command=activar_zoom)
btn_zoom.grid(row=8,column=0)



# ----------------------------------------------------------------
# SECCIÓN HISTOGRAMA
# ----------------------------------------------------------------
btn_hist = ctk.CTkButton(tab_hist,text="Mostrar histograma",command=mostrar_histograma)
btn_hist.grid(row=0,column=0,sticky="w")

frame_hist = ctk.CTkFrame(tab_hist)
frame_hist.grid(row=1,column=0,pady=15)




# ----------------------------------------------------------------
# SECCIÓN FUSION
# ----------------------------------------------------------------
btn_img_aux = ctk.CTkButton(tab_fusion,text="Abrir imagen..",command=abrir_imagen_aux)
btn_img_aux.grid(row=0,column=0,padx=(0,15),pady=(0,20))
btn_fus = ctk.CTkButton(tab_fusion,text="Fusionar",command=fusion_btn)
btn_fus.grid(row=0,column=1,pady=(0,20))
ctk.CTkLabel(tab_fusion,text="Vista previa:").grid(row=1,column=0,sticky="w")
ctk.CTkLabel(tab_fusion,text="Factor:").grid(row=3,column=0,sticky="w")
entry_fus = ctk.CTkEntry(tab_fusion)
entry_fus.grid(row=4,column=0,sticky="w")
ctk.CTkLabel(tab_fusion,text="0 = Sin ecualizar").grid(row=4,column=1)




# ----------------------------------------------------------------
# VISOR DE IMAGEN
# ----------------------------------------------------------------
lbl = ctk.CTkLabel(root, text="")
lbl.place(x=765, y=10)

lbl_aux = ctk.CTkLabel(tab_fusion, text="")
lbl_aux.grid(row=2,column=0,sticky="w",pady=(0,15))


lbl.bind("<Button-1>",ejecutar_zoom)
# ----------------------------------------------------------------
# LOOP PRINCIPAL
# ----------------------------------------------------------------
root.mainloop()
