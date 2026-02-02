import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Cortés Inmobiliaria - Marketing",
    page_icon="https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png",
    layout="wide"
)

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIONES DE APOYO ---
def formato_precio(valor):
    try:
        s_valor = str(valor).split('.')[0]
        limpio = "".join(filter(str.isdigit, s_valor))
        if not limpio: return "0"
        return f"{int(limpio):,}".replace(",", ".")
    except:
        return str(valor)

# --- FUNCIÓN FLYER (La Joya de la Corona) ---
def crear_flyer(foto_subida, titulo, precio):
    # Abrir la foto y convertir a 1080x1080 (formato Instagram)
    img = Image.open(foto_subida).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    
    # 1. Capa de sombra inferior para que el texto se lea bien
    overlay = Image.new('RGBA', (1080, 1080), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([0, 800, 1080, 1080], fill=(0, 0, 0, 160)) # Sombra negra semi-transparente
    img.paste(overlay, (0,0), overlay)

    # 2. Agregar Logo de la inmobiliaria (esquina superior)
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo)
        logo = Image.open(BytesIO(res.content)).convert("RGBA")
        logo.thumbnail((250, 250))
        img.paste(logo, (40, 40), logo)
    except: pass

    # 3. Textos (Usamos fuentes básicas del sistema)
    try:
        # Intentamos cargar una fuente de sistema, si falla usamos la default
        font_t = ImageFont.load_default(size=60)
        font_p = ImageFont.load_default(size=80)
    except:
        font_t = ImageFont.load_default()
        font_p = ImageFont.load_default()

    # Dibujar Título y Precio
    draw.text((50, 850), titulo.upper(), fill="white", font=font_t)
    draw.text((50, 930), f"USD {formato_precio(precio)}", fill="#FFD700", font=font_p) # Color dorado para el precio
    draw.text((50, 1020), "CONSULTANOS: +54 9 351 308-3986", fill="white", font=font_t)

    # Guardar en memoria
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- FUNCIÓN PDF (Igual a la anterior) ---
def crear_pdf(titulo, precio, fecha, desc):
    precio_lindo = formato_precio(precio)
    pdf = FPDF()
    pdf.add_page()
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=10)
        if res.status_code == 200:
            with open("temp_logo.png", "wb") as f: f.write(res.content)
            pdf.image("temp_logo.png", x=75, y=10, w=60)
    except: pass
    pdf.ln(45)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio_lindo}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 7, txt=desc)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.sidebar.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
menu = st.sidebar.radio("MENÚ", ["🏠 PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR NUEVO"])

df = pd.read_csv(DB_FILE)

if menu == "📂 CARGAR NUEVO":
    st.title("📂 Cargar Propiedad")
    with st.form("carga"):
        t = st.text_input("Título")
        p = st.text_input("Precio (Solo números)")
        d = st.text_area("Descripción")
        l = st.text_input("Link Drive")
        if st.form_submit_button("Guardar"):
            p_limpio = "".join(filter(str.isdigit, p))
            nueva = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_limpio, d, l]], columns=df.columns)
            pd.concat([df, nueva]).to_csv(DB_FILE, index=False)
            st.success("Guardado!")
            st.rerun()

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers para Redes")
    if df.empty:
        st.warning("Primero cargá una propiedad en el Portfolio.")
    else:
        # 1. Elegir propiedad
        prop_elegida = st.selectbox("Seleccioná la propiedad:", df['Titulo'].tolist())
        datos = df[df['Titulo'] == prop_elegida].iloc[0]
        
        # 2. Subir Foto
        st.info("Subí la mejor foto de la propiedad (se cortará cuadrada automáticamente)")
        foto = st.file_uploader("Elegir Imagen", type=['jpg', 'jpeg', 'png'])
        
        if foto:
            st.image(foto, caption="Vista Previa de tu foto", width=300)
            if st.button("✨ GENERAR MI FLYER"):
                flyer_img = crear_flyer(foto, datos['Titulo'], datos['Precio'])
                st.image(flyer_img, caption="¡Flyer Terminado!", use_container_width=True)
                st.download_button("💾 DESCARGAR FLYER PARA INSTAGRAM", flyer_img, file_name=f"Flyer_{datos['Titulo']}.png", mime="image/png")

else:
    st.title("🖼️ Tu Portfolio")
    for i, row in df.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div style="background:#fff; padding:15px; border-radius:10px; border-left: 5px solid #28a745; margin-bottom:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1)"><h3>{row["Titulo"]} - USD {formato_precio(row["Precio"])}</h3></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                pdf = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                st.download_button("📄 FICHA PDF", pdf, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"p_{row['ID']}")
            with c2:
                link = str(row['LinkDrive']).strip()
                if "http" in link:
                    st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; height:3em; border-radius:10px;">📂 DRIVE</button></a>', unsafe_allow_html=True)
            with c3:
                if st.button("🗑️ Borrar", key=f"d_{row['ID']}"):
                    df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                    st.rerun()
