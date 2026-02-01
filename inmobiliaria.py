import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortés Inmo", layout="wide")

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN GENERAR PDF CON LOGO ---
def crear_pdf(titulo, precio, fecha, desc, link):
    pdf = FPDF()
    pdf.add_page()
    
    # Intentar cargar Logo desde GitHub
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png"
        response = requests.get(url_logo)
        logo_data = BytesIO(response.content)
        pdf.image(logo_data, x=10, y=8, w=33) # Logo en la esquina superior
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='R')

    pdf.ln(20)
    
    # Título de la Propiedad con Estilo
    pdf.set_draw_color(46, 125, 50) # Color verde para la línea
    pdf.set_line_width(1)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 12, txt=f"{titulo.upper()}", ln=True, border='B')
    pdf.ln(5)
    
    # Datos Principales
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Fecha de publicación: {fecha}", ln=True)
    pdf.ln(5)
    
    # Descripción
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="Detalles de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(10)
    
    # Link Drive
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="LINK A MATERIAL MULTIMEDIA (FOTOS/VIDEOS):", ln=True)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Arial", 'U', 10)
    pdf.multi_cell(0, 8, txt=link)
    
    # Bloque de Contacto con Colores de Redes
    pdf.set_y(-60)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="CONTACTO COMERCIAL:", ln=True, border='T')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, txt=f"WhatsApp: +54 9 351 308-3986", ln=True)
    
    # Simulación de colores de redes en texto
    pdf.set_text_color(228, 64, 95) # Color Instagram
    pdf.cell(0, 6, txt=f"Instagram: @cortes.inmo", ln=True)
    
    pdf.set_text_color(0, 0, 0) # Color TikTok (Negro)
    pdf.cell(0, 6, txt=f"TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS APP ---
st.markdown("""
    <style>
    .stDownloadButton>button { background-color: #2e7d32 !important; color: white !important; border-radius: 10px; height: 3.5em; width: 100%; font-weight: bold; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("MENÚ", ["📂 Cargar Propiedad", "🖼️ Mi Portfolio"])

if menu == "📂 Cargar Propiedad":
    st.title("📂 Cargar Propiedad")
    with st.form("carga", clear_on_submit=True):
        t = st.text_input("Nombre Propiedad")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link de Drive")
        if st.form_submit_button("GUARDAR"):
            if t and p and l:
                id_p = datetime.now().timestamp()
                df_n = pd.DataFrame([[id_p, datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                df_n.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("Guardado correctamente.")

else:
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card"><h2>🏠 {row["Titulo"]}</h2><b>USD {row["Precio"]}</b></div>', unsafe_allow_html=True)
                
                # Botón de PDF con estilo "Compartir"
                pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'], row['LinkDrive'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(label="📄 GENERAR Y ENVIAR FICHA", data=pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", mime="application/pdf")
                with col2:
                    if st.button(f"🗑️ Borrar", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
