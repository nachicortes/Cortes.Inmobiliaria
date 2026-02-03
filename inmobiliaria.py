import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Cortés Inmobiliaria",
    page_icon="https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png",
    layout="wide"
)

DB_FILE = "db_inmuebles_v5.csv"

# Inicialización de estados
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- CARGA DE DATOS ---
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])

df = cargar_datos()

# --- BARRA LATERAL (BOTÓN DE CARGA REUBICADO) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    
    # SECCIÓN DE SEGURIDAD (BIEN ARRIBA)
    st.subheader("💾 Seguridad de Datos")
    
    # Botón para subir el archivo (Este es el que buscás)
    archivo_subido = st.file_uploader("SUBIR RESPALDO (.csv)", type="csv", help="Si se borró todo, subí acá tu archivo guardado.")
    if archivo_subido:
        df_restaurado = pd.read_csv(archivo_subido)
        df_restaurado.to_csv(DB_FILE, index=False)
        st.success("¡Datos recuperados!")
        st.rerun()

    # Botón para descargar el archivo
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 GUARDAR MI BASE ACTUAL", csv_data, "respaldo_cortes.csv", "text/csv")
    
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])

# --- FUNCIONES CORE (PDF, FLYER, PRECIO) ---

def formato_precio(valor):
    try:
        s_valor = str(valor).split('.')[0]
        limpio = "".join(filter(str.isdigit, s_valor))
        return f"{int(limpio):,}".replace(",", ".") if limpio else "0"
    except: return str(valor)

def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", timeout=10)
        with open("temp_logo.png", "wb") as f: f.write(res.content)
        pdf.image("temp_logo.png", x=75, y=10, w=60)
    except: pass
    pdf.ln(35)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=titulo.upper(), ln=True, border='B')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, txt=f"VALOR: USD {formato_precio(precio)}", ln=True)
    pdf.set_font("Arial", 'I', 9); pdf.cell(0, 7, txt=f"Publicado: {fecha}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 8, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(5)
    y_q = pdf.get_y()
    if y_q < 210:
        qrcode.make("https://www.instagram.com/cortes.inmo/").save("t_qr.png")
        pdf.image("t_qr.png", x=10, y=y_q, w=30)
        pdf.set_xy(45, y_q + 12); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, txt="ESCANEÁ PARA VER MÁS EN REDES")
    pdf.set_y(245)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    redes = [
        ("https://cdn-icons-png.flaticon.com/512/733/733585.png", "WhatsApp: +54 9 351 308-3986", 255),
        ("https://cdn-icons-png.flaticon.com/512/174/174855.png", "Instagram: @cortes.inmo", 262),
        ("https://cdn-icons-png.flaticon.com/512/3046/3046121.png", "TikTok: @cortes.inmobiliaria", 269)
    ]
    for url, txt, y in redes:
        try:
            r = requests.get(url)
            with open("temp_ico.png", "wb") as f: f.write(r.content)
            pdf.image("temp_ico.png", x=10, y=y, w=5)
        except: pass
        pdf.set_xy(17, y + 0.5); pdf.set_font("Arial", '', 10); pdf.cell(0, 5, txt=txt, ln=True)
    return pdf.output(dest='S').encode('latin-1')

def crear_flyer(foto, titulo, precio):
    img = Image.open(foto).convert("RGB").resize((1080, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    overlay = Image.new('RGBA', (1080, 1080), (0,0,0,0))
    ImageDraw.Draw(overlay).rectangle([0, 750, 1080, 1080], fill=(0, 0, 0, 180))
    img.paste(overlay, (0,0), overlay)
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png")
        logo = Image.open(BytesIO(res.content)).convert("RGBA")
        logo.thumbnail((280, 280))
        img.paste(logo, (40, 40), logo)
    except: pass
    draw.text((50, 780), titulo.upper(), fill="white")
    draw.text((50, 860), f"USD {formato_precio(precio)}", fill="#FFD700")
    draw.text((50, 950), "CONTACTO: +54 9 351 308-3986", fill="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- ESTILOS ---
st.markdown("<style>div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; width: 100%; border-radius: 10px; font-weight: bold; }</style>", unsafe_allow_html=True)

# --- PORTFOLIO ---
if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    if df.empty:
        st.info("El portfolio está vacío. Si tenés un respaldo, subilo desde la izquierda.")
    for i, row in df.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div style="background:white;padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1)"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
            with c1:
                st.download_button("📄 ENVIAR FICHA", crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion']), file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
            with c2:
                if "http" in str(row['LinkDrive']): st.link_button("📂 DRIVE", str(row['LinkDrive']))
            with c3:
                if st.button("📝", key=f"ed_{row['ID']}"):
                    st.session_state.edit_id = row['ID']; st.rerun()
            with c4:
                if st.button("🗑️", key=f"dl_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    df.to_csv(DB_FILE, index=False); st.rerun()

# --- CARGAR / EDITAR ---
elif menu == "📂 CARGAR" or st.session_state.edit_id:
    id_e = st.session_state.edit_id
    f_e = df[df['ID'] == id_e].iloc[0] if id_e else None
    st.title("📝 Datos de Propiedad")
    with st.form("f"):
        t = st.text_input("Título", value=f_e['Titulo'] if f_e is not None else "")
        p = st.text_input("Precio USD", value=str(f_e['Precio']).split('.')[0] if f_e is not None else "")
        d = st.text_area("Descripción", value=f_e['Descripcion'] if f_e is not None else "")
        l = st.text_input("Link Drive", value=str(f_e['LinkDrive']) if f_e is not None else "")
        if st.form_submit_button("💾 GUARDAR"):
            p_l = "".join(filter(str.isdigit, str(p)))
            if id_e: df.loc[df['ID'] == id_e, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_l, d, l]
            else:
                n = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_l, d, l]], columns=df.columns)
                df = pd.concat([df, n])
            df.to_csv(DB_FILE, index=False); st.session_state.edit_id = None; st.rerun()

# --- FLYER ---
elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers")
    if not df.empty:
        p_sel = st.selectbox("Elegí propiedad:", df['Titulo'].tolist())
        foto = st.file_uploader("Subí foto de fondo:", type=['jpg', 'png', 'jpeg'])
        if foto and st.button("✨ GENERAR"):
            dat = df[df['Titulo'] == p_sel].iloc[0]
            flyer = crear_flyer(foto, dat['Titulo'], dat['Precio'])
            st.image(flyer); st.download_button("💾 DESCARGAR FLYER", flyer, file_name=f"Flyer_{p_sel}.png")
    else: st.warning("Cargá datos primero.")
