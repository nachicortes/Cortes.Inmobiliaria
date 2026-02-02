import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
import qrcode

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Cortés Inmobiliaria",
    page_icon="https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png",
    layout="wide"
)

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF (RESTAURADA CON REDES) ---
def crear_pdf(titulo, precio, fecha, desc):
    try:
        p_limpio = str(precio).replace(".", "").replace(",", "")
        p_formateado = f"{int(p_limpio):,}".replace(",", ".")
    except:
        p_formateado = precio

    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=10)
        if res.status_code == 200:
            with open("temp_logo.png", "wb") as f: f.write(res.content)
            pdf.image("temp_logo.png", x=75, y=10, w=60)
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.set_xy(10, 20)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')

    pdf.ln(45)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {p_formateado}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(10)
    
    # QR
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # Contacto al pie
    pdf.set_y(-55)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 6, txt="Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 6, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS ---
st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
        border: none;
    }
