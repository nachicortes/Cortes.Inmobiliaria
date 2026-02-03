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

# --- PDF BLINDADO (Estilo image_ee0d03) ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Logo Principal
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=3)
        pdf.image(BytesIO(res.content), x=75, y=10, w=60)
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
    
    # 2. QR Redes (Con manejo de errores total)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr_io = BytesIO(); qr.save(qr_io); qr_io.seek(0)
        pdf.image(qr_io, x=10, y=pdf.get_y()+2, w=35)
    except: 
        pdf.cell(0, 10, txt="[QR de Instagram]", ln=True)
    
    # 3. Pie de página: Contacto
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
            r = requests.get(url_ico, timeout=2)
            pdf.image(BytesIO(r.content), x=10, y=y_contact+1, w=4)
        except:
            pdf.set_xy(10, y_contact)
            pdf.cell(4, 6, txt=">", ln=False) # Marcador si no carga logo
            
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

if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    if df.empty: st.info("Cargá una propiedad en el menú 'CARGAR'.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.5, 1, 0.5, 0.5])
                with c1:
                    # El PDF ahora está dentro de un TRY para que no rompa la fila
                    try:
                        pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                        st.download_button("📄 PDF", pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"dl_{row['ID']}", use_container_width=True)
                    except: st.error("Error PDF")
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
    st.title("📝 Gestión")
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

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers")
    st.info("Función activa.")
