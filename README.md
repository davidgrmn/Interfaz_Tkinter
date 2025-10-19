# 🖼️ Picture Manipulator

**Picture Manipulator** es una aplicación de escritorio desarrollada en **Python** usando [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), [Pillow](https://pillow.readthedocs.io/en/stable/), y **NumPy**.  
Permite abrir, visualizar y editar imágenes aplicando diferentes transformaciones desde una interfaz gráfica amigable y moderna.

---

## ⚙️ Funcionalidades principales

### 🎨 Ajustes de color
- 🔆 Brillo general o por canales (R, G, B)  
- ⚫ Binarización mediante umbral  
- 🩶 Conversión a escala de grises (Promedio o Luminosidad)  
- 🌑 Negativo  
- 🌓 Contraste logarítmico y exponencial  

### 🧩 Capas y visualización
- Visualización individual de capas **RGB**  
- Simulación de capas **CMYK**

### 🧰 Herramientas básicas
- ✂️ Recorte de imagen por coordenadas  
- 🔄 Rotación manual  
- 📉 Reducción de resolución  
- 🔍 Zoom con clic sobre la imagen  

### 🖼️ Fusión de imágenes
- Permite combinar dos imágenes distintas con un **factor de mezcla ajustable**

### 📊 Análisis
- Generación de **histograma RGB** embebido dentro de la interfaz  

---

## 🪄 Uso

1. Ejecutar el programa desde terminal:

   ```bash
   python tk.py
