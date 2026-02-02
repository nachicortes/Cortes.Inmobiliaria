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

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF (TU VERSIÓN CON REDES) ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO PRINCIPAL
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
    
    # 2. CUERPO
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
    
    # 3. QR
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    # 4. CONTACTO (Mantenemos tu lógica de iconos)
    pdf.set_y(-60)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.ln(2)

    iconos = {
        "ws": "https://cdn-icons-png.flaticon.com/512/733/733585.png",
        "ig": "https://cdn-icons-png.flaticon.com/512/174/174855.png",
        "tk": "https://cdn-icons-png.flaticon.com/512/3046/3046121.png"
    }

    def agregar_linea_contacto(tipo, texto, y_pos):
        try:
            r = requests.get(iconos[tipo], timeout=10)
            with open(f"icon_{tipo}.png", "wb") as f: f.write(r.content)
            pdf.image(f"icon_{tipo}.png", x=10, y=y_pos, w=5)
        except: pass
        pdf.set_xy(17, y_pos + 0.5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=texto, ln=True)

    y_pos = pdf.get_y() + 2
    agregar_linea_contacto("ws", "WhatsApp: +54 9 351 308-3986", y_pos)
    agregar_linea_contacto("ig", "Instagram: @cortes.inmo", y_pos + 8)
    agregar_linea_contacto("tk", "TikTok: @cortes.inmobiliaria", y_pos + 16)
    
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
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"])
    st.divider()
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("💾 COPIA DE SEGURIDAD", f, file_name="Respaldo.csv")

# --- LÓGICA ---
if menu == "📂 CARGAR":
    st.title("📂 Nueva Propiedad")
    with st.form("carga", clear_on_submit=True):
        t = st.text_input("Título")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link de Drive")
        if st.form_submit_button("🚀 GUARDAR"):
            if t and p:
                df_n = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                df_n.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Propiedad Guardada!")

else:
    st.title("🖼️ Portfolio Personal")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            for _, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {row["Precio"]}</h4></div>', unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                        st.download_button("📄 ENVIAR FICHA", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
                    with c2:
                        # MEJORA: Solo muestra el botón si hay un link válido
                        link_valido = str(row['LinkDrive']).strip()
                        if link_valido and link_valido != "nan" and link_valido.startswith("http"):
                            st.link_button("📂 DRIVE", link_valido)
                        else:
                            st.button("📂 SIN LINK", disabled=True, key=f"drive_{row['ID']}")
                    with c3:
                        if st.button("🗑️", key=f"del_{row['ID']}"):
                            df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                            st.rerun()
