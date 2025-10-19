import numpy as np
import matplotlib.pyplot as plt
import math



# ==============================================================
# CAPAS RGB Y CMYK
# ==============================================================

def layer(img, capa):
    """
    Aísla una capa RGB específica (0=R, 1=G, 2=B) de la imagen.
    El resto de canales se ponen en 0.
    """
    layer_img = np.zeros_like(img)
    layer_img[:, :, capa] = img[:, :, capa]
    return layer_img


def layer_cmyk(img, capa):
    """
    Simula la separación de capas CMY (Cian, Magenta, Amarillo).
    Se parte de un modelo RGB, "apagando" los canales necesarios
    para dejar visible solo el componente deseado.
    """
    copia = np.copy(img)

    if capa == "y":  # Amarillo = mezcla de R y G
        copia[:, :, 0] = copia[:, :, 1] = 255
        return copia

    elif capa == "c":  # Cian = mezcla de G y B
        copia[:, :, 1] = copia[:, :, 2] = 255
        return copia

    elif capa == "m":  # Magenta = mezcla de R y B
        copia[:, :, 0] = copia[:, :, 2] = 255
        return copia


# ==============================================================
# BRILLO
# ==============================================================

def bright(img, factor):
    """
    Ajusta el brillo general sumando un valor a todos los píxeles.
    Se utiliza np.clip para mantener los valores dentro del rango [0,255].
    """
    img_brillo = img + factor
    img_brillo = np.clip(img_brillo, 0, 255)
    return img_brillo


def bright_canal(img, r, g, b):
    """
    Ajusta el brillo de forma independiente para cada canal RGB.
    Suma valores distintos en cada capa y luego recorta el rango.
    """
    img_copy = img.copy()
    img_copy[..., 0] += r  # Canal rojo
    img_copy[..., 1] += g  # Canal verde
    img_copy[..., 2] += b  # Canal azul
    img_copy = np.clip(img_copy, 0, 255)
    return img_copy


# ==============================================================
# NEGATIVO Y ESCALA DE GRISES
# ==============================================================

def negative(img):
    """
    Invierte los colores de la imagen.
    Para una imagen normalizada (0-1), basta con 1 - img.
    Si está en rango 0-255, el resultado se ajusta en la interfaz.
    """
    negativa = 1 - img
    return negativa


def get_luminosity_gray(img):
    """
    Convierte la imagen a escala de grises usando ponderaciones
    perceptuales basadas en la sensibilidad del ojo humano:
    0.21 * R + 0.72 * G + 0.07 * B
    """
    gray = img[:, :, 0] * 0.21 + img[:, :, 1] * 0.72 + img[:, :, 2] * 0.07
    return gray


def get_average_gray(img):
    """
    Convierte la imagen a escala de grises por promedio simple.
    (R + G + B) / 3
    """
    gray = (img[:, :, 0] + img[:, :, 1] + img[:, :, 2]) / 3
    return gray


# ==============================================================
# BINARIZACIÓN
# ==============================================================

def binary(img, umbral):
    """
    Convierte una imagen en blanco y negro según un umbral dado (0–1).
    Primero calcula una versión en escala de grises,
    luego aplica el umbral generando 0 o 255 en cada píxel.
    """
    img = img.astype(np.float32)

    # Verificar tipo de imagen
    if len(img.shape) == 2:  # Grayscale
        gris = img
    elif len(img.shape) == 3:
        # Ponderación RGB → gris perceptual
        gris = (img[:, :, 0] * 0.21 + img[:, :, 1] * 0.72 + img[:, :, 2] * 0.07)
    else:
        raise ValueError("Forma de img inválida.")

    # Normalizar y umbralizar
    gris_norm = np.clip(gris / 255.0, 0, 1)
    img_bin = (gris_norm > umbral).astype(np.uint8) * 255
    return img_bin


# ==============================================================
# REDUCCIÓN DE RESOLUCIÓN
# ==============================================================

def res_reducer(img, factor):
    """
    Reduce la resolución de la imagen seleccionando un pixel
    de cada 'factor' en filas y columnas.
    Ejemplo: factor=2 → reduce a la cuarta parte.
    """
    res_ = img[::factor, ::factor]
    return res_


# ==============================================================
# CONTRASTE
# ==============================================================

def contrast_logarithmic(img, factor=1.0):
    """
    Aumenta el contraste mediante una función logarítmica.
    Se aplica log(1 + x), donde x está normalizado en [0,1].
    Cuanto mayor el 'factor', más se realzan las sombras.
    """
    img = img.astype(np.float32) / 255.0
    result = factor * np.log1p(img)
    result = result / np.log1p(1.0)
    result = np.clip(result * 255, 0, 255).astype(np.uint8)
    return result


def contrast_exponential(img, factor=1.0):
    """
    Aplica una función exponencial para intensificar el contraste.
    Resalta las zonas brillantes de manera no lineal.
    """
    img = img.astype(np.float32) / 255.0
    result = np.expm1(factor * img)
    result = result / np.expm1(factor)
    result = np.clip(result * 255, 0, 255).astype(np.uint8)
    return result


# ==============================================================
# RECORTE Y ZOOM DIGITAL
# ==============================================================

def cut(img, x1, y1, x2, y2):
    """
    Recorta la imagen entre las coordenadas (x1,y1) y (x2,y2).
    """
    cutted = img[x1:x2, y1:y2]
    return cutted


def zoom(img, center_x, center_y, zoom_area=100, zoom_factor=5):
    """
    Realiza un 'zoom digital' en torno a un punto (center_x, center_y).
    - Recorta un área cuadrada (zoom_area)
    - Amplía ese recorte por repetición de píxeles (np.kron)
    """
    h, w = img.shape[:2]

    # Asegurar que el recorte no salga de los límites
    start_row = max(0, center_y - zoom_area // 2)
    end_row = min(h, center_y + zoom_area // 2)
    start_col = max(0, center_x - zoom_area // 2)
    end_col = min(w, center_x + zoom_area // 2)

    recorte = img[start_row:end_row, start_col:end_col]
    zoomed = np.kron(recorte, np.ones((zoom_factor, zoom_factor, 1)))
    return zoomed


# ==============================================================
# FUSIÓN DE IMÁGENES
# ==============================================================

def fusion(img1, img2, ecul_factor):
    """
    Combina dos imágenes según un factor de mezcla (0–1).
    - Si ecul_factor = 0.5 → mezcla equitativa
    - Si ecul_factor = 1 → solo la primera imagen
    - Si ecul_factor = 0 → suma directa (sin ponderar)
    """
    if 0.1 <= ecul_factor <= 1:
        fus = img1 * ecul_factor + img2 * (1 - ecul_factor)
        return fus
    elif ecul_factor == 0:
        fus = img1 + img2
        return fus


# ==============================================================
# ROTACIÓN MANUAL
# ==============================================================

def rotar_manual(matriz, grados):
    """
    Rota una imagen (matriz NumPy) un ángulo en grados.
    Implementa la rotación manualmente, sin usar PIL.
    Usa rotación inversa (backward mapping) para evitar huecos.
    """
    theta = math.radians(grados)
    h, w, c = matriz.shape
    cx, cy = w // 2, h // 2  # Centro original

    # Calcular tamaño nuevo considerando expansión
    new_w = int(abs(w * math.cos(theta)) + abs(h * math.sin(theta)))
    new_h = int(abs(w * math.sin(theta)) + abs(h * math.cos(theta)))

    nueva = np.zeros((new_h, new_w, c), dtype=np.uint8)
    new_cx, new_cy = new_w // 2, new_h // 2

    # Para cada píxel de la nueva imagen, calcula de dónde viene
    for y in range(new_h):
        for x in range(new_w):
            x_rel = x - new_cx
            y_rel = y - new_cy
            orig_x = int(cx + x_rel * math.cos(-theta) - y_rel * math.sin(-theta))
            orig_y = int(cy + x_rel * math.sin(-theta) + y_rel * math.cos(-theta))
            if 0 <= orig_x < w and 0 <= orig_y < h:
                nueva[y, x] = matriz[orig_y, orig_x]

    return nueva


# ==============================================================
# HISTOGRAMA RGB
# ==============================================================

def generar_histograma(img):
    """
    Genera un histograma RGB de una imagen PIL.
    Retorna una figura Matplotlib lista para insertar en Tkinter.

    - Convierte la imagen a array NumPy
    - Calcula la distribución de intensidad para cada canal (R,G,B)
    - Devuelve la figura configurada para mostrarse en la interfaz
    """
    img_np = np.array(img.convert("RGB"))
    fig, ax = plt.subplots(figsize=(4.5, 3), dpi=100)
    colores = ('r', 'g', 'b')

    for i, color in enumerate(colores):
        hist, bins = np.histogram(img_np[..., i].flatten(), bins=256, range=[0, 256])
        ax.plot(bins[:-1], hist, color=color)

    ax.set_title("Histograma RGB")
    ax.set_xlabel("Intensidad")
    ax.set_ylabel("Frecuencia")
    ax.ticklabel_format(style='plain', axis='y')
    plt.tight_layout()
    return fig
