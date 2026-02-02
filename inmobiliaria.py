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

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PRECIO (Corregida para que no agregue ceros) ---
def formato_precio(valor):
    try:
        # Convertimos a string y quitamos cualquier punto o coma que ya tenga
        s_valor = str(valor).split('.')[0] # Ignoramos decimales si existieran
        limpio = "".join(filter(str.isdigit, s_valor))
        if not limpio: return "0"
        # Formateamos: 4250 -> 4.250
        return f"{int(limpio):,}".replace(",", ".")
    except:
        return str(valor)

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
    precio_lindo = formato_precio(precio)
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
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio_lindo}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(10)
    
    qr = qrcode.make("https://www.instagram.com/cortes.inmo/")
    qr.save("temp_qr.png")
    pdf.image("temp_qr.png", x=10, y=pdf.get_y()+2, w=35)
    
    pdf.set_y(-55)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONTACTO:", ln=True, border='T')
    
    iconos = {"ws": "https://cdn-icons-png.flaticon.com/512/733/733585.png",
              "ig": "https://cdn-icons-png.flaticon.com/512/174/174855.png",
              "tk": "https://cdn-icons-png.flaticon.com/512/3046/3046121.png"}

    def agregar_linea(tipo, texto, y):
        try:
            r = requests.get(iconos[tipo], timeout=5)
            with open(f"icon_{tipo}.png", "wb") as f: f.write(r.content)
            pdf.image(f"icon_{tipo}.png", x=10, y=y, w=5)
        except: pass
        pdf.set_xy(17, y + 0.5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=texto, ln=True)

    y_pos = pdf.get_y() + 2
    agregar_linea("ws", "WhatsApp: +54 9 351 308-3986", y_pos)
    agregar_linea("ig", "Instagram: @cortes.inmo", y_pos + 7)
    agregar_linea("tk", "TikTok: @cortes.inmobiliaria", y_pos + 14)
    
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
    idx = 0 if st.session_state.edit_id is not None else 1
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"], index=idx)

df = pd.read_csv(DB_FILE)

# --- CARGAR / EDITAR ---
if menu == "📂 CARGAR":
    if st.session_state.edit_id:
        st.title("📝 Editar Propiedad")
        f = df[df['ID'] == st.session_state.edit_id].iloc[0]
        v_t, v_p, v_d, v_l = f['Titulo'], f['Precio'], f['Descripcion'], f['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        v_t, v_p, v_d, v_l = "", "", "", ""

    with st.form("form_inmo", clear_on_submit=True):
        t = st.text_input("Título", value=v_t)
        p = st.text_input("Precio USD (Escribí solo los números)", value=str(v_p).split('.')[0] if str(v_p) != "nan" else "")
        d = st.text_area("Descripción", value=v_d)
        l = st.text_input("Link de Drive", value=str(v_l) if str(v_l) != "nan" else "")
        if st.form_submit_button("💾 GUARDAR"):
            if t and p:
                # Limpieza absoluta: solo números
                p_c = "".join(filter(str.isdigit, str(p)))
                if st.session_state.edit_id:
                    df.loc[df['ID'] == st.session_state.edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_c, d, l]
                    st.session_state.edit_id = None
                else:
                    nueva = pd.DataFrame([[datetime.now().timestamp(), datetime.now().strftime("%d/%m/%Y"), t, p_c, d, l]], columns=df.columns)
                    df = pd.concat([df, nueva], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Guardado!")
                st.rerun()

# --- PORTFOLIO ---
else:
    st.title("🖼️ Portfolio Personal")
    for idx_row, row in df.iloc[::-1].iterrows():
        with st.container():
            p_display = formato_precio(row['Precio'])
            st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {p_display}</h4></div>', unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
            
            with c1:
                pdf_data = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                st.download_button("📄 ENVIAR FICHA", pdf_data, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
            
            with c2:
                raw_link = str(row['LinkDrive']).strip()
                if raw_link and raw_link != "nan" and "http" in raw_link:
                    link_html = f'<a href="{raw_link}" target="_blank" style="text-decoration: none;"><button style="width: 100%; height: 3em; border-radius: 10px; border: 1px solid #ccc; cursor: pointer; background: #f8f9fa;">📂 DRIVE</button></a>'
                    st.markdown(link_html, unsafe_allow_html=True)
                else:
                    st.button("📂 SIN LINK", disabled=True, key=f"no_{row['ID']}")
            
            with c3:
                if st.button("📝", key=f"ed_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
            
            with c4:
                if st.button("🗑️", key=f"del_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
