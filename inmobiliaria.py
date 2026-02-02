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

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

def formato_precio(valor):
    try:
        s_valor = str(valor).split('.')[0]
        limpio = "".join(filter(str.isdigit, s_valor))
        if not limpio: return "0"
        return f"{int(limpio):,}".replace(",", ".")
    except:
        return str(valor)

# --- FUNCIÓN FLYER (RESTAURADA) ---
def crear_flyer(foto_subida, titulo, precio):
    img = Image.open(foto_subida).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    overlay = Image.new('RGBA', (1080, 1080), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([0, 750, 1080, 1080], fill=(0, 0, 0, 180))
    img.paste(overlay, (0,0), overlay)
    try:
        res = requests.get("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png")
        logo = Image.open(BytesIO(res.content)).convert("RGBA")
        logo.thumbnail((280, 280))
        img.paste(logo, (40, 40), logo)
    except: pass
    draw.text((50, 780), titulo.upper(), fill="white")
    draw.text((50, 860), f"USD {formato_precio(precio)}", fill="#FFD700")
    draw.text((50, 950), "WHATSAPP: +54 9 351 308-3986", fill="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- FUNCIÓN PDF (LOGOS Y QR CORREGIDOS) ---
def crear_pdf(titulo, precio, fecha, desc):
    precio_lindo = formato_precio(precio)
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=10)
        with open("temp_logo.png", "wb") as f: f.write(res.content)
        pdf.image("temp_logo.png", x=75, y=10, w=60)
    except: pass

    pdf.ln(35)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio_lindo}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    
    # Descripción
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    
    # QR Abajo de la descripción
    pdf.ln(5)
    y_qr = pdf.get_y()
    if y_qr > 200: pdf.add_page(); y_qr = 20 # Evitar que el QR quede cortado
    try:
        qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
        qr.save("temp_qr.png")
        pdf.image("temp_qr.png", x=10, y=y_qr, w=30)
        pdf.set_xy(45, y_qr + 10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 5, txt="ESCANEÁ PARA VER MÁS EN REDES:", ln=True)
    except: pass

    # Contacto al pie de página (Siempre en hoja 1 si hay espacio)
    pdf.set_y(250)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    
    iconos = {
        "ws": "https://cdn-icons-png.flaticon.com/512/733/733585.png",
        "ig": "https://cdn-icons-png.flaticon.com/512/174/174855.png",
        "tk": "https://cdn-icons-png.flaticon.com/512/3046/3046121.png"
    }
    
    redes = [
        ("ws", "WhatsApp: +54 9 351 308-3986", 260),
        ("ig", "Instagram: @cortes.inmo", 267),
        ("tk", "TikTok: @cortes.inmobiliaria", 274)
    ]

    for key, texto, y_pos in redes:
        try:
            r = requests.get(iconos[key])
            with open(f"ico_{key}.png", "wb") as f: f.write(r.content)
            pdf.image(f"ico_{key}.png", x=10, y=y_pos, w=5)
        except: pass
        pdf.set_xy(17, y_pos + 0.5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=texto, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ STREAMLIT ---
st.markdown("""
    <style>
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100% !important; height: 3em; border: none; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])

df = pd.read_csv(DB_FILE)

# --- PORTFOLIO ---
if menu == "🖼️ PORTFOLIO" and not st.session_state.edit_id:
    st.title("🖼️ Portfolio Personal")
    for i, row in df.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {formato_precio(row["Precio"])}</h4></div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
            with c1:
                pdf_dat = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                st.download_button("📄 ENVIAR FICHA", pdf_dat, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
            with c2:
                lk = str(row['LinkDrive']).strip()
                if lk and lk != "nan" and "http" in lk:
                    st.markdown(f'<a href="{lk}" target="_blank"><button style="width:100%; height:3em; border-radius:10px; border:1px solid #ccc; cursor:pointer; background:#f8f9fa;">📂 DRIVE</button></a>', unsafe_allow_html=True)
                else: st.button("📂 SIN LINK", disabled=True, key=f"no_{row['ID']}")
            with c3:
                if st.button("📝", key=f"ed_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"dl_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()

# --- DISEÑADOR FLYER ---
elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers Profesionales")
    if not df.empty:
        prop = st.selectbox("Elegí una propiedad:", df['Titulo'].tolist())
        foto = st.file_uploader("Subí la mejor foto:", type=['jpg', 'png', 'jpeg'])
        if foto and st.button("✨ GENERAR FLYER"):
            d_f = df[df['Titulo'] == prop].iloc[0]
            f_img = crear_flyer(foto, d_f['Titulo'], d_f['Precio'])
            st.image(f_img, use_container_width=True)
            st.download_button("💾 DESCARGAR PARA REDES", f_img, file_name=f"Flyer_{prop}.png")
    else: st.warning("No hay propiedades cargadas.")

# --- CARGAR / EDITAR ---
else:
    if st.session_state.edit_id:
        st.title("📝 Editar Propiedad")
        f = df[df['ID'] == st.session_state.edit_id].iloc[0]
        v_t, v_p, v_d, v_l = f['Titulo'], f['Precio'], f['Descripcion'], f['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        v_t, v_p, v_d, v_l = "", "", "", ""

    with st.form("form_inmo"):
        t = st.text_input("Título", value=v_t)
        p = st.text_input("Precio USD", value=str(v_p).split('.')[0] if str(v_p) != "nan" else "")
        d = st.text_area("Descripción", value=v_d)
        l = st.text_input("Link de Drive", value=str(v_l) if str(v_l) != "nan" else "")
        if st.form_submit_button("💾 GUARDAR"):
            p_c = "".join(filter(str.isdigit, str(p)))
            if st.session_state.edit_id:
                df.loc[df['ID'] == st.session_state.edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_c, d, l]
                st.session_state.edit_id = None
            else:
                nueva = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_c, d, l]], columns=df.columns)
                df = pd.concat([df, nueva])
            df.to_csv(DB_FILE, index=False)
            st.success("¡Guardado!")
            st.rerun()
