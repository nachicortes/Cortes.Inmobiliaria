import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import requests

# --- NUEVO DISEÑADOR DE FLYERS PROFESIONAL ---
def generar_flyer_pro(propiedad, fotos, estilo="Moderno"):
    # Creamos un lienzo blanco de 1080x1350 (Formato Portrait Instagram)
    canvas = Image.new('RGB', (1080, 1350), color=(255, 255, 255))
    
    # Combinar fotos (Tomamos hasta 3 fotos)
    posiciones = [(0,0,1080,675), (0,675,540,1000), (540,675,1080,1000)]
    for i, archivo in enumerate(fotos[:3]):
        img = Image.open(archivo).convert("RGB")
        # Redimensionar y recortar para que encaje en su cuadrante
        ancho, alto = posiciones[i][2]-posiciones[i][0], posiciones[i][3]-posiciones[i][1]
        img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
        canvas.paste(img, (posiciones[i][0], posiciones[i][1]))

    draw = ImageDraw.Draw(canvas)
    
    # Capa de diseño (Rectángulo inferior para texto)
    draw.rectangle([0, 1000, 1080, 1350], fill=(255, 255, 255))
    
    # Redacción Inteligente (Juego de palabras según precio/título)
    texto_gancho = f"¡TU PRÓXIMO HOGAR EN {propiedad['Titulo'].upper()}!"
    draw.text((50, 1050), texto_gancho, fill=(0,0,0))
    draw.text((50, 1150), f"Oportunidad única: USD {propiedad['Precio']}", fill=(40, 167, 69))
    
    return canvas

# --- MEJORA PDF: QR GENERADO EN MEMORIA ---
def obtener_qr_memoria(url):
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img_qr.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- INTEGRACIÓN EN EL MENÚ ---
if st.session_state.get('menu') == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Editor de Flyers Multi-foto")
    p_sel = st.selectbox("Elegí la propiedad", df['Titulo'])
    datos_p = df[df['Titulo'] == p_sel].iloc[0]
    
    fotos = st.file_uploader("Subí hasta 3 fotos de la propiedad", accept_multiple_files=True)
    
    if fotos:
        if st.button("✨ GENERAR DISEÑO"):
            flyer_final = generar_flyer_pro(datos_p, fotos)
            st.image(flyer_final, caption="Diseño generado para Cortés Inmobiliaria")
            
            # Botón de descarga del Flyer
            buf = BytesIO()
            flyer_final.save(buf, format="JPEG")
            st.download_button("💾 Descargar Flyer para Redes", buf.getvalue(), "flyer_cortes.jpg")
