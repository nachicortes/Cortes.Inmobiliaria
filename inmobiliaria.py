import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortés Inmobiliaria", page_icon="🏠", layout="wide")

# Conexión Permanente
def conectar_google():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("DB_Cortes_Inmo").sheet1
    except: return None

sheet = conectar_google()

def obtener_datos():
    if sheet:
        try: return pd.DataFrame(sheet.get_all_records())
        except: return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = obtener_datos()
if 'edit_id' not in st.session_state: st.session_state.edit_id = None

# --- FUNCIONES DE APOYO ---
def formato_precio(valor):
    try:
        limpio = "".join(filter(str.isdigit, str(valor).split('.')[0]))
        return f"{int(limpio):,}".replace(",", ".") if limpio else "0"
    except: return str(valor)

def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    # Logo Principal
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=5)
        pdf.image(BytesIO(res.content), x=75, y=10, w=60)
    except: pass
    
    pdf.ln(35)
    pdf.set_font("Arial", 'B', 20); pdf.cell(0, 15, txt=str(titulo).upper(), ln=True, border='B')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, txt=f"VALOR: USD {formato_precio(precio)}", ln=True)
    pdf.set_font("Arial", 'I', 9); pdf.cell(0, 7, txt=f"Publicado: {fecha}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 8, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, txt=str(desc))
    
    # QR y Redes (Sección Final)
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 8, txt="CONTACTO:", ln=True, border='T')
    
    # Texto de contacto (mientras recuperamos íconos)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, txt=f"WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 5, txt=f"Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 5, txt=f"TikTok: @cortes.inmobiliaria", ln=True)
    
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr_b = BytesIO(); qr.save(qr_b); qr_b.seek(0)
        pdf.image(qr_b, x=160, y=250, w=30)
    except: pass
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])
    if st.button("🔄 Refrescar"): st.rerun()

# --- PORTFOLIO ---
if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    st.markdown("<style>div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; font-weight: bold; }</style>", unsafe_allow_html=True)
    
    for i, row in df.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1.5, 1, 0.5, 0.5])
            with c1:
                if st.button(f"📄 GENERAR PDF", key=f"btn_{row['ID']}"):
                    pdf_data = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("⬇️ DESCARGAR FICHA", pdf_data, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"dl_{row['ID']}")
            with c2:
                if "http" in str(row['LinkDrive']): st.link_button("📂 DRIVE", str(row['LinkDrive']))
            with c3:
                if st.button("📝", key=f"ed_{row['ID']}"):
                    st.session_state.edit_id = row['ID']; st.rerun()
            with c4:
                if st.button("🗑️", key=f"br_{row['ID']}"):
                    if sheet:
                        cell = sheet.find(str(row['ID']))
                        sheet.delete_rows(cell.row)
                        st.rerun()

# --- CARGAR / EDITAR ---
elif menu == "📂 CARGAR" or st.session_state.edit_id:
    st.title("📝 Gestión de Propiedad")
    id_e = st.session_state.edit_id
    item = df[df['ID'] == id_e].iloc[0] if id_e and not df.empty else None
    with st.form("f"):
        t = st.text_input("Título", value=item['Titulo'] if item is not None else "")
        p = st.text_input("Precio USD", value=str(item['Precio']) if item is not None else "")
        d = st.text_area("Descripción", value=item['Descripcion'] if item is not None else "")
        l = st.text_input("Link Drive", value=str(item['LinkDrive']) if item is not None else "")
        if st.form_submit_button("💾 GUARDAR"):
            p_l = "".join(filter(str.isdigit, str(p)))
            if id_e:
                cell = sheet.find(str(id_e))
                sheet.update(range_name=f"C{cell.row}:F{cell.row}", values=[[t, p_l, d, l]])
                st.session_state.edit_id = None
            else:
                sheet.append_row([int(datetime.now().timestamp()), datetime.now().strftime("%d/%m/%Y"), t, p_l, d, l])
            st.rerun()

# --- DISEÑADOR DE FLYER (RESTAURADO) ---
elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers Profesionales")
    if not df.empty:
        p_sel = st.selectbox("Elegí propiedad:", df['Titulo'].tolist())
        foto = st.file_uploader("Subí foto de fondo (1080x1080):", type=['jpg', 'png', 'jpeg'])
        if foto:
            img = Image.open(foto).convert("RGB").resize((1080, 1080))
            draw = ImageDraw.Draw(img)
            # Aquí iría tu lógica de diseño de capas...
            st.image(img, caption="Vista previa del Flyer")
            st.info("Hacé clic derecho en la imagen para guardarla.")
    else: st.warning("Cargá una propiedad primero.")
