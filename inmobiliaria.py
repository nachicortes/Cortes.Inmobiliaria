import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
import qrcode

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Cortés Inmobiliaria",
    page_icon="https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png",
    layout="wide"
)

# Estado de edición (Para que la app sepa si estás creando una nueva o editando)
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
    # Formatear el precio para el PDF con puntos de mil
    try:
        p_limpio = str(precio).replace(".", "").replace(",", "")
        p_formateado = f"{int(p_limpio):,}".replace(",", ".")
    except:
        p_formateado = precio

    pdf = FPDF()
    pdf.add_page()
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
    pdf.ln(15)
    
    # QR
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ WEB (CSS ORIGINAL) ---
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
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    try:
        st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    except:
        st.title("🏡 CORTÉS INMO")
    
    st.divider()
    # Si estamos editando, forzamos a mostrar la pestaña de CARGA
    idx_menu = 0 if st.session_state.edit_id is not None else 1
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"], index=idx_menu)
    
    st.divider()
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button(label="💾 COPIA DE SEGURIDAD", data=f, file_name="Respaldo.csv", mime="text/csv")

# Carga de datos
df = pd.read_csv(DB_FILE)

# --- LÓGICA DE CARGA Y EDICIÓN ---
if menu == "📂 CARGAR":
    edit_id = st.session_state.edit_id
    
    if edit_id is not None:
        st.title("📝 Editar Propiedad")
        fila = df[df['ID'] == edit_id].iloc[0]
        v_t, v_p, v_d, v_l = fila['Titulo'], fila['Precio'], fila['Descripcion'], fila['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        v_t, v_p, v_d, v_l = "", "", "", ""

    with st.form("carga", clear_on_submit=True):
        t = st.text_input("Título", value=v_t)
        p = st.text_input("Precio USD (Escribí solo números, ej: 1500000)", value=str(v_p))
        d = st.text_area("Descripción", value=v_d)
        l = st.text_input("Link de Drive", value=str(v_l) if str(v_l) != "nan" else "")
        
        btn_label = "🚀 ACTUALIZAR" if edit_id is not None else "🚀 GUARDAR"
        if st.form_submit_button(btn_label):
            if t and p:
                # Limpiamos el precio de puntos para guardarlo puro
                p_limpio = p.replace(".", "").replace(",", "").strip()
                
                if edit_id is not None:
                    # Actualizar
                    df.loc[df['ID'] == edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_limpio, d, l]
                    st.session_state.edit_id =
