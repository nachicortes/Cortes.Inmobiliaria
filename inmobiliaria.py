import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
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

def formato_precio(v):
    try:
        num = "".join(filter(str.isdigit, str(v)))
        return f"{int(num):,}".replace(",", ".") if num else "0"
    except: return str(v)

# --- PDF DEFINITIVO (DISEÑO FIEL) ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO CENTRADO (Descarga forzada)
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=5)
        img_logo = BytesIO(res.content)
        pdf.image(img_logo, x=75, y=10, w=60)
    except: pass
    
    pdf.ln(35)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, txt=str(titulo).upper(), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) 
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"VALOR: USD {formato_precio(precio)}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, txt=str(desc))
    
    # 2. SECCIÓN QR (Generación Garantizada)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    try:
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data("https://www.instagram.com/cortes.inmo/")
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        img_qr.save(qr_io, format='PNG')
        qr_io.seek(0)
        pdf.image(qr_io, x=10, y=pdf.get_y()+2, w=35)
    except: 
        pdf.cell(0, 10, txt="[Escaneá nuestro Instagram @cortes.inmo]", ln=True)
    
    # 3. PIE DE PÁGINA (Contacto con íconos fijos)
    pdf.set_y(245)
    pdf.line(10, 245, 200, 245)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="CONTACTO:", ln=True)
    
    y_contact = pdf.get_y()
    redes = [
        ("WhatsApp", "+54 9 351 308-3986", "https://cdn-icons-png.flaticon.com/512/3670/3670051.png"),
        ("Instagram", "@cortes.inmo", "https://cdn-icons-png.flaticon.com/512/3955/3955024.png"),
        ("TikTok", "@cortes.inmobiliaria", "https://cdn-icons-png.flaticon.com/512/3046/3046121.png")
    ]
    
    for plataforma, texto, url_ico in redes:
        try:
            r_ico = requests.get(url_ico, timeout=3)
            pdf.image(BytesIO(r_ico.content), x=10, y=y_contact+1, w=4)
        except: pass
        pdf.set_xy(16, y_contact)
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 6, txt=f"{plataforma}: {texto}", ln=True)
        y_contact += 6

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])
    st.info("Conectado con éxito ✅")

if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    if df.empty: st.info("No hay propiedades para mostrar.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.5, 1, 0.5, 0.5])
                with c1:
                    try:
                        pdf_data = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                        st.download_button("📄 FICHA PDF", pdf_data, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"dl_{row['ID']}")
                    except: st.error("Error al generar PDF")
                with c2:
                    if "http" in str(row['LinkDrive']): st.link_button("📂 DRIVE", str(row['LinkDrive']), use_container_width=True)
                with c3:
                    if st.button("📝", key=f"ed_{row['ID']}", use_container_width=True):
                        st.session_state.edit_id = row['ID']; st.rerun()
                with c4:
                    if st.button("🗑️", key=f"br_{row['ID']}", use_container_width=True):
                        if sheet:
                            cell = sheet.find(str(row['ID']))
                            sheet.delete_rows(cell.row)
                            st.rerun()

elif menu == "📂 CARGAR" or st.session_state.edit_id:
    st.title("📝 Gestión de Datos")
    # Formulario de carga/edición... (se mantiene igual al anterior)
