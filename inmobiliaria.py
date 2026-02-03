import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
from PIL import Image
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
        client = gspread.authorize(credentials)
        sheet = client.open("DB_Cortes_Inmo").sheet1
        return sheet
    except: return None

sheet = conectar_google()

def obtener_datos():
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = obtener_datos()

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- FORMATO ---
def formato_precio(valor):
    try:
        limpio = "".join(filter(str.isdigit, str(valor).split('.')[0]))
        return f"{int(limpio):,}".replace(",", ".") if limpio else "0"
    except: return str(valor)

def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=5)
        logo_path = "temp_logo.png"
        with open(logo_path, "wb") as f: f.write(res.content)
        pdf.image(logo_path, x=75, y=10, w=60)
    except: pass
    
    pdf.ln(35)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=str(titulo).upper(), ln=True, border='B')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {formato_precio(precio)}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 7, txt=f"Publicado: {fecha}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=str(desc))
    
    # QR Robusto
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr.save("temp_qr.png")
        pdf.image("temp_qr.png", x=10, y=pdf.get_y()+5, w=30)
    except: pass
    
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 5, txt="Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 5, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])
    if st.sidebar.button("🔄 Refrescar Datos"): st.rerun()

if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    st.markdown("<style>div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; font-weight: bold; width: 100%; }</style>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No hay propiedades. Cargá una en el menú 'CARGAR'.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""
                <div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)">
                    <h3 style="margin:0">🏠 {row['Titulo']}</h3>
                    <h4 style="color:#28a745;margin:5px 0">USD {formato_precio(row['Precio'])}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([1.5, 1, 0.5, 0.5])
                with c1:
                    try:
                        pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                        st.download_button("📄 ENVIAR PDF", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
                    except: st.error("Error PDF")
                with c2:
                    link = str(row['LinkDrive'])
                    if "http" in link: st.link_button("📂 DRIVE", link, use_container_width=True)
                    else: st.button("🚫 SIN LINK", disabled=True, use_container_width=True)
                with c3:
                    if st.button("📝", key=f"ed_{row['ID']}", use_container_width=True):
                        st.session_state.edit_id = row['ID']; st.rerun()
                with c4:
                    if st.button("🗑️", key=f"dl_{row['ID']}", use_container_width=True):
                        if sheet:
                            cell = sheet.find(str(row['ID']))
                            sheet.delete_rows(cell.row)
                            st.rerun()

elif menu == "📂 CARGAR" or st.session_state.edit_id:
    st.title("📝 Gestión")
    id_edit = st.session_state.edit_id
    # Buscar datos si es edición
    f_edit = df[df['ID'] == id_edit].iloc[0] if id_edit and not df.empty else None
    
    with st.form("f_carga"):
        t = st.text_input("Título", value=f_edit['Titulo'] if f_edit is not None else "")
        p = st.text_input("Precio USD (solo números)", value=str(f_edit['Precio']) if f_edit is not None else "")
        d = st.text_area("Descripción", value=f_edit['Descripcion'] if f_edit is not None else "")
        l = st.text_input("Link Drive", value=str(f_edit['LinkDrive']) if f_edit is not None else "")
        
        if st.form_submit_button("💾 GUARDAR"):
            p_limpio = "".join(filter(str.isdigit, str(p)))
            if id_edit:
                cell = sheet.find(str(id_edit))
                sheet.update(range_name=f"C{cell.row}:F{cell.row}", values=[[t, p_limpio, d, l]])
                st.session_state.edit_id = None
            else:
                nueva = [int(datetime.now().timestamp()), datetime.now().strftime("%d/%m/%Y"), t, p_limpio, d, l]
                sheet.append_row(nueva)
            st.success("¡Sincronizado!")
            st.rerun()

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Flyers")
    st.info("Función en mantenimiento para asegurar compatibilidad con Google Drive.")
