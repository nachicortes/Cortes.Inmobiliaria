import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import qrcode
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO

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
    try: return f"{int(''.join(filter(str.isdigit, str(v)))):,}".replace(",", ".")
    except: return str(v)

# --- FUNCIÓN PDF OPTIMIZADA ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(40, 167, 69) # Verde Inmobiliaria
    
    # Encabezado
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(0, 15, txt=str(titulo).upper(), ln=True, align='L')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(40, 167, 69)
    pdf.cell(0, 10, txt=f"USD {formato_precio(precio)}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 7, txt=f"Publicado: {fecha}", ln=True, border='B')
    
    # Descripción
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="DESCRIPCION:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=str(desc))
    
    # Contacto Estilizado (Sin depender de imágenes externas)
    pdf.set_y(240)
    pdf.set_draw_color(40, 167, 69)
    pdf.cell(0, 0, border='T', ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, txt="CONTACTO PROFESIONAL:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, txt=f"WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 6, txt=f"Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 6, txt=f"TikTok: @cortes.inmobiliaria", ln=True)
    
    # QR con manejo de errores
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        b = BytesIO(); qr.save(b); b.seek(0)
        pdf.image(b, x=160, y=245, w=35)
    except: pass
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("MENÚ", ["🖼️ PORTFOLIO", "📂 CARGAR PROPIEDAD"])
    st.success("Conectado a la Base de Datos ✅")

if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio de Propiedades")
    if df.empty: st.info("No hay propiedades. Usá el menú lateral para cargar una.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""<div style="background:#f9f9f9;padding:15px;border-left:5px solid #28a745;border-radius:10px;margin-bottom:10px">
                    <h3 style="margin:0">🏠 {row['Titulo']}</h3>
                    <h4 style="color:#28a745;margin:0">USD {formato_precio(row['Precio'])}</h4>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([1, 1, 0.5, 0.5])
                with c1:
                    try:
                        btn_pdf = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                        st.download_button("📩 FICHA PDF", btn_pdf, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"p_{row['ID']}")
                    except: st.error("Error PDF")
                with c2:
                    if "http" in str(row['LinkDrive']): st.link_button("📂 DRIVE", str(row['LinkDrive']), use_container_width=True)
                with c3:
                    if st.button("📝", key=f"e_{row['ID']}", use_container_width=True):
                        st.session_state.edit_id = row['ID']; st.rerun()
                with c4:
                    if st.button("🗑️", key=f"d_{row['ID']}", use_container_width=True):
                        if sheet:
                            cell = sheet.find(str(row['ID']))
                            sheet.delete_rows(cell.row)
                            st.rerun()

elif menu == "📂 CARGAR PROPIEDAD" or st.session_state.edit_id:
    st.title("📝 Editor de Propiedades")
    id_e = st.session_state.edit_id
    item = df[df['ID'] == id_e].iloc[0] if id_e and not df.empty else None
    with st.form("carga"):
        t = st.text_input("Título", value=item['Titulo'] if item is not None else "")
        p = st.text_input("Precio (Solo números)", value=str(item['Precio']) if item is not None else "")
        d = st.text_area("Descripción", value=item['Descripcion'] if item is not None else "")
        l = st.text_input("Link de Drive", value=str(item['LinkDrive']) if item is not None else "")
        if st.form_submit_button("💾 GUARDAR TODO"):
            p_l = "".join(filter(str.isdigit, str(p)))
            if id_e:
                cell = sheet.find(str(id_e))
                sheet.update(range_name=f"C{cell.row}:F{cell.row}", values=[[t, p_l, d, l]])
                st.session_state.edit_id = None
            else:
                sheet.append_row([int(datetime.now().timestamp()), datetime.now().strftime("%d/%m/%Y"), t, p_l, d, l])
            st.rerun()
