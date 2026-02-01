import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
from io import BytesIO
import qrcode

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortés Inmo", layout="wide")

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO CENTRADO
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png"
        response = requests.get(url_logo)
        with open("temp_logo.png", "wb") as f: f.write(response.content)
        # 210mm es el ancho A4. (210 - 60 de ancho logo) / 2 = 75 para centrar
        pdf.image("temp_logo.png", x=75, y=10, w=60) 
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')

    pdf.ln(45) # Espacio después del logo centrado
    
    # 2. CUERPO (ESTILO NEGRO Y SOBRIO)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(10)
    
    # 3. QR A INSTAGRAM
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # 4. SECCIÓN CONTACTO (LOGOS AJUSTADOS)
    pdf.set_y(-60)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.ln(2)

    def agregar_red(nombre_img, texto, y_off):
        base_url = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/"
        try:
            r = requests.get(base_url + nombre_img)
            if r.status_code == 200:
                with open(f"temp_{nombre_img}", "wb") as f: f.write(r.content)
                # w=6 para que los logos se vean más grandes y uniformes
                pdf.image(f"temp_{nombre_img}", x=10, y=y_off,
