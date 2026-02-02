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

# --- FUNCIÓN FLYER ---
def crear_flyer(foto_subida, titulo, precio):
    img = Image.open(foto_subida).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    overlay = Image.new('RGBA', (1080, 1080), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([0, 800, 1080, 1080], fill=(0, 0, 0, 160))
    img.paste(overlay, (0,0), overlay)
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo)
        logo = Image.open(BytesIO(res.content)).convert("RGBA")
        logo.thumbnail((250, 250))
        img.paste(logo, (40, 40), logo)
    except: pass
    draw.text((50, 850), titulo.upper(), fill="white")
    draw.text((50, 930), f"USD {formato_precio(precio)}", fill="#FFD700")
    draw.text((50, 1010), "CONTACTO: 5493513083986", fill="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- FUNCIÓN PDF (OPTIMIZADA PARA 1 SOLA HOJA) ---
def crear_pdf(titulo, precio, fecha, desc):
    precio_lindo = formato_precio(precio)
    pdf = FPDF()
    pdf.add_page()
    
    # Logo Superior
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png"
        res = requests.get(url_logo, timeout=10)
        with open("temp_logo.png", "wb") as f: f.write(res.content)
        pdf.image("temp_logo.png", x=75, y=10, w=60)
    except: pass

    pdf.ln(35) # Espacio reducido para que entre todo
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 12, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio_lindo}", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, txt=desc)
    
    # QR Code
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=160, y=pdf.get_y() + 5, w=30)

    # Redes Sociales al pie (Fijado al final de la página 1)
    pdf.set_y(250) 
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="CONTACTO:", ln=True, border='T')
    
    iconos = {
        "ws": "https://cdn-icons-png.flaticon.com/512/733/733585.png",
        "ig": "https://cdn-icons-png.flaticon.com/512/174/174855.png",
        "tk": "https://cdn-icons-png.flaticon.com/512/3046/3046121.png"
    }
    
    def agregar_red(icono_url, texto, y_pos):
        try:
            r = requests.get(icono_url)
            with open("temp_icon.png", "wb") as f: f.write(r.content)
            pdf.image("temp_icon.png", x=10, y=y_pos, w=5)
        except: pass
        pdf.set_xy(17, y_pos + 0.5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=texto, ln=True)

    agregar_red(iconos["ws"], "WhatsApp: 5493513083986", 260)
    agregar_red(iconos["ig"], "Instagram: @cortes.inmo", 267)
    agregar_red(iconos["tk"], "TikTok: @cortes.inmobiliaria", 274)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS ---
st.markdown("""
    <style>
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100% !important; height: 3.5em; border: none; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    menu = st.radio("NAVEGACIÓN", ["🖼️ PORTFOLIO", "🎨 DISEÑADOR FLYER", "📂 CARGAR"])

df = pd.read_csv(DB_FILE)

# --- LÓGICA CARGAR / EDITAR ---
if menu == "📂 CARGAR" or st.session_state.edit_id:
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

elif menu == "🎨 DISEÑADOR FLYER":
    st.title("🎨 Creador de Flyers")
    if not df.empty:
        prop = st.selectbox("Seleccioná la propiedad:", df['Titulo'].tolist())
        foto = st.file_uploader("Subí una foto:", type=['jpg', 'png', 'jpeg'])
        if foto and st.button("Generar Flyer"):
            d_f = df[df['Titulo'] == prop].iloc[0]
            f_img = crear_flyer(foto, d_f['Titulo'], d_f['Precio'])
            st.image(f_img)
            st.download_button("Descargar Flyer", f_img, file_name="flyer_cortes.png")
    else: st.warning("Cargá una propiedad primero.")

else:
    st.title("🖼️ Portfolio")
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
