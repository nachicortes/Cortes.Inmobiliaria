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

# --- FUNCIÓN PDF PROFESIONAL ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO ORIGINAL
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png"
        response = requests.get(url_logo)
        with open("temp_logo.png", "wb") as f:
            f.write(response.content)
        pdf.image("temp_logo.png", x=10, y=10, w=45) 
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.text(10, 20, "CORTÉS INMOBILIARIA")

    pdf.ln(30)
    
    # 2. CUERPO DE LA FICHA (ESTILO NEGRO)
    pdf.set_draw_color(0, 0, 0)
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
    
    # 3. CÓDIGO QR A INSTAGRAM (DRIVE PRIVADO)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    
    ig_link = "https://www.instagram.com/cortes.inmo/"
    qr = qrcode.make(ig_link)
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # 4. SECCIÓN CONTACTO
    pdf.set_y(-60)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.ln(2)

    def agregar_contacto(icono_url, texto, y_pos):
        try:
            res = requests.get(icono_url)
            if res.status_code == 200:
                with open("temp_icon.png", "wb") as f: f.write(res.content)
                pdf.image("temp_icon.png", x=10, y=y_pos, w=5)
            pdf.set_xy(17, y_pos+0.5)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 5, txt=texto, ln=True)
        except:
            pass

    base_url = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/"
    
    agregar_contacto(base_url+"ws.png", "WhatsApp: +54 9 351 308-3986", pdf.get_y()+2)
    agregar_contacto(base_url+"ig.png", "Instagram: @cortes.inmo", pdf.get_y()+2)
    agregar_contacto(base_url+"tk.png", "TikTok: @cortes.inmobiliaria", pdf.get_y()+2)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ APP ---
st.markdown("""
    <style>
    .stDownloadButton>button { background-color: #000000 !important; color: white !important; border-radius: 12px; height: 4em; width: 100%; font-weight: bold; border: none; }
    .card { background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #f0f0f0; margin-bottom: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"])

if menu == "📂 CARGAR":
    st.title("📂 Nueva Propiedad")
    with st.form("form_carga", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link de Drive (Privado)")
        if st.form_submit_button("🚀 GUARDAR"):
            if t and p and l:
                id_p = datetime.now().timestamp()
                df_n = pd.DataFrame([[id_p, datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                df_n.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Propiedad Guardada!")

else:
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card"><h2>🏠 {row["Titulo"]}</h2><h3>USD {row["Precio"]}</h3></div>', unsafe_allow_html=True)
                pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.download_button(label="📄 ENVIAR FICHA", data=pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", mime="application/pdf")
                with c2:
                    st.link_button("📂 VER DRIVE", row['LinkDrive'])
                with c3:
                    if st.button(f"🗑️ Borrar", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
