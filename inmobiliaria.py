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

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PARA FORMATEAR PRECIOS (1500000 -> 1.500.000) ---
def formato_precio(valor):
    try:
        # Quitamos cualquier punto o coma que haya puesto el usuario por error
        limpio = str(valor).replace(".", "").replace(",", "").strip()
        return f"{int(limpio):,}".replace(",", ".")
    except:
        return valor

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
    precio_lindo = formato_precio(precio)
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
    pdf.cell(0, 10, txt=f"VALOR: USD {precio_lindo}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    pdf.set_y(-60)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    
    # Datos de contacto directos para evitar errores de descarga de iconos
    pdf.set_font("Arial", '', 10)
    pdf.ln(2)
    pdf.cell(0, 6, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 6, txt="Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 6, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS ---
st.markdown("""
    <style>
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; height: 3.5em; border: none; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    idx_menu = 0 if st.session_state.edit_id is not None else 1
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"], index=idx_menu)
    st.divider()
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("💾 COPIA DE SEGURIDAD", f, file_name="Respaldo.csv")

df = pd.read_csv(DB_FILE)

# --- LÓGICA DE CARGA / EDICIÓN ---
if menu == "📂 CARGAR":
    if st.session_state.edit_id is not None:
        st.title("📝 Editar Propiedad")
        fila = df[df['ID'] == st.session_state.edit_id].iloc[0]
        v_t, v_p, v_d, v_l = fila['Titulo'], fila['Precio'], fila['Descripcion'], fila['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        v_t, v_p, v_d, v_l = "", "", "", ""

    with st.form("form_carga", clear_on_submit=True):
        t = st.text_input("Título", value=v_t)
        p = st.text_input("Precio USD (Escribí solo números, ej: 1500000)", value=str(v_p))
        d = st.text_area("Descripción", value=v_d)
        l = st.text_input("Link de Drive", value=str(v_l) if str(v_l) != "nan" else "")
        
        if st.form_submit_button("💾 GUARDAR"):
            if t and p:
                # Guardamos el número limpio para no tener problemas de cálculos
                p_limpio = str(p).replace(".", "").replace(",", "").strip()
                if st.session_state.edit_id is not None:
                    df.loc[df['ID'] == st.session_state.edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_limpio, d, l]
                    st.session_state.edit_id = None
                else:
                    nueva = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_limpio, d, l]], columns=df.columns)
                    df = pd.concat([df, nueva], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Guardado con éxito!")
                st.rerun()

    if st.session_state.edit_id is not None:
        if st.button("❌ Cancelar Edición"):
            st.session_state.edit_id = None
            st.rerun()

# --- PORTFOLIO ---
else:
    st.title("🖼️ Portfolio Personal")
    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            with st.container():
                precio_mostrar = formato_precio(row['Precio'])
                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {precio_mostrar}</h4></div>', unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
                with c1:
                    pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR FICHA", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"p_{row['ID']}")
                with c2:
                    link = str(row['LinkDrive']).strip()
                    if link and link != "nan" and link.startswith("http"):
                        st.link_button("📂 DRIVE", link)
                    else:
                        st.button("📂 SIN LINK", disabled=True, key=f"d_{row['ID']}")
                with c3:
                    if st.button("📝", key=f"ed_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
