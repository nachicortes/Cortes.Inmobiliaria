import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Cortés Inmobiliaria", page_icon="🏠", layout="wide")

def conectar_google():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(credentials).open("DB_Cortes_Inmo").sheet1
    except: return None

sheet = conectar_google()

def obtener_datos():
    if sheet:
        try: return pd.DataFrame(sheet.get_all_records())
        except: return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = obtener_datos()
if 'edit_id' not in st.session_state: st.session_state.edit_id = None

# --- MOTOR DE DISEÑO: FLYER MULTIFOTO ---
def generar_flyer_premium(propiedad, fotos_subidas):
    # Lienzo Instagram (1080x1350)
    canvas = Image.new('RGB', (1080, 1350), color='#FFFFFF')
    draw = ImageDraw.Draw(canvas)
    
    # Lógica de cuadrícula para 3 fotos
    posiciones = [(0, 0, 1080, 600), (0, 600, 535, 950), (545, 600, 1080, 950)]
    
    for i, file in enumerate(fotos_subidas[:3]):
        img = Image.open(file).convert("RGB")
        ancho = posiciones[i][2] - posiciones[i][0]
        alto = posiciones[i][3] - posiciones[i][1]
        # Ajuste inteligente de imagen
        img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
        canvas.paste(img, (posiciones[i][0], posiciones[i][1]))

    # Pie de diseño con redacción comercial
    draw.rectangle([0, 950, 1080, 1350], fill='#1A1A1A') # Fondo oscuro elegante
    
    # Aquí iría el texto (Mañana cargaremos tipografías personalizadas)
    titulo_comercial = f"EXCLUSIVO: {propiedad['Titulo'].upper()}"
    precio_comercial = f"INVERSIÓN: USD {propiedad['Precio']}"
    
    # Dibujo de texto básico (provisional hasta cargar fuentes)
    draw.text((50, 1000), titulo_comercial, fill='#FFFFFF')
    draw.text((50, 1100), precio_comercial, fill='#28A745')
    
    return canvas

# --- PDF ROBUSTO ---
def crear_pdf_final(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado con línea estética
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=str(titulo).upper(), ln=True)
    pdf.set_draw_color(40, 167, 69)
    pdf.line(10, 25, 200, 25)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 15)
    pdf.set_text_color(40, 167, 69)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio}", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=str(desc))
    
    # QR e Iconos (Bloque de seguridad para evitar página en blanco)
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr_b = BytesIO(); qr.save(qr_b); qr_b.seek(0)
        pdf.image(qr_b, x=160, y=250, w=30)
    except: pass
    
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, txt="CONTACTO: @cortes.inmo", ln=True)
    pdf.cell(0, 5, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ STREAMLIT ---
with st.sidebar:
    st.title("Cortés Inmo")
    menu = st.radio("MENÚ", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])

if menu == "🖼️ PORTFOLIO":
    st.title("Portfolio de Propiedades")
    for i, row in df.iloc[::-1].iterrows():
        with st.expander(f"🏠 {row['Titulo']} - USD {row['Precio']}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Generar PDF", key=f"pdf_{row['ID']}"):
                    pdf_v = crear_pdf_final(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("Descargar", pdf_v, f"{row['Titulo']}.pdf")
            with col2:
                if st.button("Borrar", key=f"del_{row['ID']}"):
                    cell = sheet.find(str(row['ID']))
                    sheet.delete_rows(cell.row)
                    st.rerun()

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("Creador de Flyers Multifoto")
    p_sel = st.selectbox("Elegí propiedad", df['Titulo'])
    fotos = st.file_uploader("Subí 3 fotos", accept_multiple_files=True)
    
    if fotos and st.button("Crear Flyer"):
        datos = df[df['Titulo'] == p_sel].iloc[0]
        resultado = generar_flyer_premium(datos, fotos)
        st.image(resultado)
