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

# --- ESTADO DE EDICIÓN (Para saber qué estamos editando) ---
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
        pdf.set_xy(10, 20)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='C')

    pdf.ln(45)
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
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
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
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; height: 3.5em; border: none; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    # Si estamos editando, forzamos a que el menú muestre "CARGAR"
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
        # Buscamos los datos de la propiedad a editar
        fila_editar = df[df['ID'] == st.session_state.edit_id].iloc[0]
        titulo_def = fila_editar['Titulo']
        precio_def = fila_editar['Precio']
        desc_def = fila_editar['Descripcion']
        link_def = fila_editar['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        titulo_def, precio_def, desc_def, link_def = "", "", "", ""

    with st.form("form_carga", clear_on_submit=True):
        t = st.text_input("Título", value=titulo_def)
        p = st.text_input("Precio USD", value=str(precio_def))
        d = st.text_area("Descripción", value=desc_def)
        l = st.text_input("Link de Drive", value=str(link_def) if str(link_def) != "nan" else "")
        
        btn_label = "💾 GUARDAR CAMBIOS" if st.session_state.edit_id is not None else "🚀 GUARDAR"
        if st.form_submit_button(btn_label):
            if t and p:
                if st.session_state.edit_id is not None:
                    # EDITAR EXISTENTE
                    df.loc[df['ID'] == st.session_state.edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p, d, l]
                    st.session_state.edit_id = None # Limpiamos el modo edición
                else:
                    # NUEVA FILA
                    nuevo_id = datetime.now().timestamp()
                    nueva_fila = pd.DataFrame([[nuevo_id, datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], columns=df.columns)
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                
                df.to_csv(DB_FILE, index=False)
                st.success("¡Operación exitosa!")
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
                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {row["Precio"]}</h4></div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
                with c1:
                    pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR FICHA", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
                with c2:
                    link_valido = str(row['LinkDrive']).strip()
                    if link_valido and link_valido != "nan" and link_valido.startswith("http"):
                        st.link_button("📂 DRIVE", link_valido)
                    else:
                        st.button("📂 SIN LINK", disabled=True, key=f"dr_{row['ID']}")
                with c3:
                    if st.button("📝", key=f"edit_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
