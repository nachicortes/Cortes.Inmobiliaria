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
        # Centrado: (210mm ancho A4 - 60mm ancho logo) / 2 = 75
        pdf.image("temp_logo.png", x=75, y=10, w=60) 
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')

    pdf.ln(45)
    
    # 2. CUERPO (ESTILO NEGRO)
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
    pdf.ln(15)
    
    # 3. QR A REDES
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # 4. SECCIÓN CONTACTO (LOGOS CORREGIDOS)
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
                pdf.image(f"temp_{nombre_img}", x=10, y=y_off, w=6) # Tamaño icono
            pdf.set_xy(18, y_off + 0.5)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, txt=texto, ln=True)
        except: pass

    y_pos = pdf.get_y() + 2
    agregar_red("ws.png", "WhatsApp: +54 9 351 308-3986", y_pos)
    agregar_red("ig.png", "Instagram: @cortes.inmo", y_pos + 8)
    agregar_red("tk.png", "TikTok: @cortes.inmobiliaria", y_pos + 16)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ (BOTONES VERDES) ---
st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
    }
    div.stDownloadButton > button:hover {
        background-color: #1b5e20 !important;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("MENÚ", ["📂 CARGAR", "🖼️ PORTFOLIO"])

if menu == "📂 CARGAR":
    st.title("📂 Nueva Propiedad")
    with st.form("carga", clear_on_submit=True):
        t = st.text_input("Título")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link Drive (Uso Interno)")
        if st.form_submit_button("🚀 GUARDAR"):
            if t and p:
                df_n = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                df_n.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Guardado!")

else:
    st.title("🖼️ Portfolio Personal")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {row["Precio"]}</h4></div>', unsafe_allow_html=True)
                pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    st.download_button(label="📄 ENVIAR FICHA", data=pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf")
                with c2:
                    st.link_button("📂 DRIVE", str(row['LinkDrive']))
                with c3:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
