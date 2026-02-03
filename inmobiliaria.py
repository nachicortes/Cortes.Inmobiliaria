import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests
import qrcode
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortés Inmobiliaria", page_icon="🏠", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
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
        try:
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except: return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = obtener_datos()

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- FUNCIONES DE FORMATO ---
def formato_precio(valor):
    try:
        limpio = "".join(filter(str.isdigit, str(valor).split('.')[0]))
        return f"{int(limpio):,}".replace(",", ".") if limpio else "0"
    except: return str(valor)

def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # Intentar poner el logo principal
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=5)
        logo_data = BytesIO(res.content)
        pdf.image(logo_data, x=75, y=10, w=60)
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
    pdf.cell(0, 8, txt="Descripcion:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=str(desc))
    
    # QR de Instagram (Optimizado)
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr_img = BytesIO()
        qr.save(qr_img)
        qr_img.seek(0)
        pdf.image(qr_img, x=10, y=pdf.get_y() + 5, w=30)
    except: pass

    # Pie de página con contacto y redes
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="CONTACTO:", ln=True, border='T')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 5, txt="Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 5, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACION", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])
    if st.button("🔄 Refrescar"): st.rerun()
    st.write("---")
    st.success("Conectado a Google Drive ✅")

# --- PORTFOLIO ---
if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    st.markdown("<style>div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; font-weight: bold; width: 100%; }</style>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No hay propiedades guardadas.")
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
                    pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR PDF", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"p_{row['ID']}")
                with c2:
                    link = str(row['LinkDrive'])
                    if "http" in link: st.link_button("📂 DRIVE", link, use_container_width=True)
                    else: st.button("🚫 SIN LINK", disabled=True, use_container_width=True)
                with c3:
                    if st.button("📝", key=f"e_{row['ID']}", use_container_width=True):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"d_{row['ID']}", use_container_width=True):
                        if sheet:
                            cell = sheet.find(str(row['ID']))
                            sheet.delete_rows(cell.row)
                            st.rerun()

# --- CARGAR / EDITAR ---
elif menu == "📂 CARGAR" or st.session_state.edit_id:
    st.title("📝 Gestion de Datos")
    id_edit = st.session_state.edit_id
    item = df[df['ID'] == id_edit].iloc[0] if id_edit and not df.empty else None
    
    with st.form("carga"):
        t = st.text_input("Titulo", value=item['Titulo'] if item is not None else "")
        p = st.text_input("Precio USD", value=str(item['Precio']) if item is not None else "")
        d = st.text_area("Descripcion", value=item['Descripcion'] if item is not None else "")
        l = st.text_input("Link Drive", value=str(item['LinkDrive']) if item is not None else "")
        
        if st.form_submit_button("💾 GUARDAR"):
            p_limpio = "".join(filter(str.isdigit, str(p)))
            if id_edit:
                cell = sheet.find(str(id_edit))
                sheet.update(range_name=f"C{cell.row}:F{cell.row}", values=[[t, p_limpio, d, l]])
                st.session_state.edit_id = None
            else:
                nueva = [int(datetime.now().timestamp()), datetime.now().strftime("%d/%m/%Y"), t, p_limpio, d, l]
                sheet.append_row(nueva)
            st.success("Guardado en Google Sheets!")
            st.rerun()

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Flyers")
    st.info("Función de diseño para redes sociales.")
