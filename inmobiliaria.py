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
    
    # 1. LOGO CENTRADO ARRIBA
    try:
        # Usamos la URL exacta de tu GitHub
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=10)
        if res.status_code == 200:
            with open("temp_logo.png", "wb") as f: f.write(res.content)
            # Centrado en A4 (210mm ancho): (210 - 55) / 2 = 77.5
            pdf.image("temp_logo.png", x=77.5, y=10, w=55)
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.set_xy(10, 20)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')

    pdf.ln(40)
    
    # 2. CUERPO DE LA FICHA
    pdf.set_text_color(0, 0, 0)
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
    pdf.ln(15)
    
    # 3. QR A REDES
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # 4. SECCIÓN CONTACTO (ICONOS ALINEADOS)
    pdf.set_y(-60)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.ln(2)

    def dibujar_red(nombre_archivo, texto, y_actual):
        base_url = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/"
        try:
            r = requests.get(base_url + nombre_archivo, timeout=10)
            if r.status_code == 200:
                with open(f"icon_{nombre_archivo}", "wb") as f: f.write(r.content)
                pdf.image(f"icon_{nombre_archivo}", x=10, y=y_actual, w=5)
            # Texto siempre visible
            pdf.set_xy(17, y_actual + 0.5)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, txt=texto, ln=True)
        except:
            pdf.set_xy(17, y_actual + 0.5)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, txt=texto, ln=True)

    pos_y = pdf.get_y() + 2
    dibujar_red("ws.png", "WhatsApp: +54 9 351 308-3986", pos_y)
    dibujar_red("ig.png", "Instagram: @cortes.inmo", pos_y + 8)
    dibujar_red("tk.png", "TikTok: @cortes.inmobiliaria", pos_y + 16)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ WEB (BOTÓN VERDE) ---
st.markdown("""
    <style>
    /* BOTÓN VERDE PROFESIONAL */
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    div.stDownloadButton > button:hover {
        background-color: #218838 !important;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("MENÚ", ["📂 CARGAR", "🖼️ PORTFOLIO"])

if menu == "📂 CARGAR":
    st.title("📂 Nueva Propiedad")
    with st.form("f_carga", clear_on_submit=True):
        t = st.text_input("Título")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link Drive")
        if st.form_submit_button("🚀 GUARDAR"):
            if t and p:
                new_data = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                new_data.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Propiedad Guardada!")

else:
    st.title("🖼️ Portfolio Personal")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for _, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {row["Precio"]}</h4></div>', unsafe_allow_html=True)
                pdf_output = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.download_button(label="📄 ENVIAR FICHA", data=pdf_output, file_name=f"Ficha_{row['Titulo']}.pdf")
                with col2:
                    st.link_button("📂 DRIVE", str(row['LinkDrive']))
                with col3:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
