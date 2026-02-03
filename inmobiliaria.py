import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
from PIL import Image, ImageDraw
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Cortés Inmobiliaria", page_icon="🏠", layout="wide")

# --- CONEXIÓN PERMANENTE CON GOOGLE SHEETS ---
def conectar_google():
    try:
        # Cargamos las credenciales desde los Secrets de Streamlit
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(credentials)
        # Conectamos a tu planilla
        sheet = client.open("DB_Cortes_Inmo").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

sheet = conectar_google()

def obtener_datos():
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = obtener_datos()

# Inicialización de estado de edición
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- FUNCIONES DE FORMATO Y DISEÑO ---
def formato_precio(valor):
    try:
        limpio = "".join(filter(str.isdigit, str(valor).split('.')[0]))
        return f"{int(limpio):,}".replace(",", ".") if limpio else "0"
    except: return str(valor)

def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    # Logo corporativo
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=10)
        img_logo = BytesIO(res.content)
        pdf.image(img_logo, x=75, y=10, w=60)
    except: pass
    
    pdf.ln(35)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=titulo.upper(), ln=True, border='B', align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {formato_precio(precio)}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    
    # QR y Redes sociales (Forzado en una página)
    y_pos = pdf.get_y()
    if y_pos > 200: pdf.add_page(); y_pos = 20
    
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr_buf = BytesIO(); qr.save(qr_buf); qr_buf.seek(0)
    pdf.image(qr_buf, x=10, y=y_pos+5, w=30)
    pdf.set_xy(45, y_pos + 15)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, txt="ESCANEÁ PARA VER MÁS EN REDES", ln=True)
    
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    
    redes = [
        ("WhatsApp: +54 9 351 308-3986", 258),
        ("Instagram: @cortes.inmo", 264),
        ("TikTok: @cortes.inmobiliaria", 270)
    ]
    for txt, y in redes:
        pdf.set_xy(17, y + 0.5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=txt, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])
    st.divider()
    st.success("Conectado a Google Drive ✅")

# --- MÓDULO PORTFOLIO ---
if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    st.markdown("<style>div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; font-weight: bold; }</style>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No hay propiedades cargadas. Empezá por '📂 CARGAR'.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
                with c1:
                    pdf_data = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR FICHA", pdf_data, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
                with c2:
                    if "http" in str(row['LinkDrive']): st.link_button("📂 DRIVE", str(row['LinkDrive']))
                with c3:
                    if st.button("📝", key=f"ed_{row['ID']}"):
                        st.session_state.edit_id = row['ID']; st.rerun()
                with c4:
                    if st.button("🗑️", key=f"dl_{row['ID']}"):
                        # Borrar en Google Sheets
                        cell = sheet.find(str(row['ID']))
                        sheet.delete_rows(cell.row)
                        st.rerun()

# --- MÓDULO CARGAR / EDITAR ---
elif menu == "📂 CARGAR" or st.session_state.edit_id:
    st.title("📝 Gestión de Propiedad")
    id_e = st.session_state.edit_id
    f_e = df[df['ID'] == id_e].iloc[0] if id_e is not None and not df.empty else None
    
    with st.form("form_carga"):
        t = st.text_input("Título", value=f_e['Titulo'] if f_e is not None else "")
        p = st.text_input("Precio USD", value=str(f_e['Precio']) if f_e is not None else "")
        d = st.text_area("Descripción", value=f_e['Descripcion'] if f_e is not None else "")
        l = st.text_input("Link Drive", value=str(f_e['LinkDrive']) if f_e is not None else "")
        
        if st.form_submit_button("💾 GUARDAR CAMBIOS"):
            precio_limpio = "".join(filter(str.isdigit, str(p)))
            if id_e is not None:
                # Actualizar fila existente
                cell = sheet.find(str(id_e))
                sheet.update(range_name=f"C{cell.row}:F{cell.row}", values=[[t, precio_limpio, d, l]])
                st.session_state.edit_id = None
            else:
                # Agregar fila nueva
                nueva_fila = [int(datetime.now().timestamp()), datetime.now().strftime("%d/%m/%Y"), t, precio_limpio, d, l]
                sheet.append_row(nueva_fila)
            st.success("¡Sincronizado con Google Sheets!")
            st.rerun()

# --- MÓDULO FLYER ---
elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers")
    if not df.empty:
        p_sel = st.selectbox("Elegí propiedad:", df['Titulo'].tolist())
        foto = st.file_uploader("Subí foto de fondo:", type=['jpg', 'png', 'jpeg'])
        if foto and st.button("✨ GENERAR FLYER"):
            dat = df[df['Titulo'] == p_sel].iloc[0]
            # (Lógica del flyer simplificada para este bloque)
            img = Image.open(foto).convert("RGB").resize((1080, 1080))
            st.image(img)
            st.warning("Flyer generado. Podés guardarlo haciendo clic derecho.")
    else: st.warning("Cargá datos primero.")
