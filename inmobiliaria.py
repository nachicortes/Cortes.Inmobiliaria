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

# Estado para la edición
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
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
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')
    
    pdf.ln(45)
    # Formateo de precio para el PDF con puntos de miles
    try:
        p_num = float(str(precio).replace(".", "").replace(",", ""))
        p_f = f"{p_num:,.0f}".replace(",", ".")
    except: p_f = precio

    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {p_f}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
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
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    # Si estamos editando, forzamos la vista a CARGAR
    nav_idx = 0 if st.session_state.edit_id is not None else 1
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"], index=nav_idx)
    st.divider()
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("💾 COPIA DE SEGURIDAD", f, file_name="Respaldo.csv")

# --- LÓGICA ---
df = pd.read_csv(DB_FILE)

if menu == "📂 CARGAR":
    eid = st.session_state.edit_id
    if eid is not None:
        st.title("📝 Editar Propiedad")
        fila = df[df['ID'] == eid].iloc[0]
        v_t, v_p, v_d, v_l = fila['Titulo'], fila['Precio'], fila['Descripcion'], fila['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        v_t, v_p, v_d, v_l = "", "", "", ""

    with st.form("form_inmo", clear_on_submit=True):
        t = st.text_input("Título", value=v_t)
        p = st.text_input("Precio USD (Escribir solo números)", value=str(v_p))
        d = st.text_area("Descripción", value=v_d)
        l = st.text_input("Link de Drive", value=str(v_l) if str(v_l) != "nan" else "")
        
        if st.form_submit_button("🚀 GUARDAR CAMBIOS"):
            if t and p:
                p_clean = p.replace(".", "").replace(",", "").strip()
                if eid is not None:
                    df.loc[df['ID'] == eid, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_clean, d, l]
                    st.session_state.edit_id = None
                else:
                    new_row = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_clean, d, l]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Propiedad guardada con éxito!")
                st.rerun()

    if eid is not None:
        if st.button("❌ Cancelar Edición"):
            st.session_state.edit_id = None
            st.rerun()

else:
    st.title("🖼️ Portfolio Personal")
    if df.empty:
        st.info("No hay propiedades.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                try:
                    p_num = float(str(row['Precio']).replace(".", "").replace(",", ""))
                    p_disp = f"{p_num:,.0f}".replace(",", ".")
                except: p_disp = row['Precio']

                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {p_disp}</h4></div>', unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
                with c1:
                    pdf = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR FICHA", data=pdf, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"p_{row['ID']}")
                with c2:
                    link = str(row['LinkDrive']).strip()
                    if link and link != "nan" and link.startswith("http"):
                        st.link_button("📂 DRIVE", link, key=f"d_{row['ID']}")
                    else:
                        st.button("📂 SIN LINK", disabled=True, key=f"nd_{row['ID']}")
                with c3:
                    if st.button("📝", key=f"e_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"x_{row['ID']}"):
                        df = df[df['ID'] != row['ID']]
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
