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

# Estado de sesión para la edición
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF ---
def crear_pdf(titulo, precio, fecha, desc):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO PRINCIPAL
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
    
    # Formateo de precio para el PDF
    try:
        p_num = float(str(precio).replace(".", "").replace(",", ""))
        p_formateado = f"{p_num:,.0f}".replace(",", ".")
    except:
        p_formateado = precio

    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"VALOR: USD {p_formateado}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Descripción de la propiedad:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS CSS (Tu diseño original) ---
st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/Cortes.Inmobiliaria/main/logo.png", width=180)
    st.divider()
    
    # Si estamos editando, forzamos a que el menú esté en CARGAR
    default_nav = 0 if st.session_state.edit_id is not None else 1
    menu = st.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"], index=default_nav)
    
    st.divider()
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("💾 COPIA DE SEGURIDAD", f, file_name="Respaldo.csv", mime="text/csv")

# Cargar datos
df = pd.read_csv(DB_FILE)

# --- PÁGINA CARGAR / EDITAR ---
if menu == "📂 CARGAR":
    edit_id = st.session_state.edit_id
    
    if edit_id is not None:
        st.title("📝 Editar Propiedad")
        # Obtenemos los datos de la fila a editar
        fila = df[df['ID'] == edit_id].iloc[0]
        val_t, val_p, val_d, val_l = fila['Titulo'], fila['Precio'], fila['Descripcion'], fila['LinkDrive']
    else:
        st.title("📂 Nueva Propiedad")
        val_t, val_p, val_d, val_l = "", "", "", ""

    with st.form("carga_form", clear_on_submit=True):
        t = st.text_input("Título", value=val_t)
        # Aquí el usuario escribe el número puro (ej: 1500000)
        p = st.text_input("Precio USD (Escribir sin puntos, ej: 380000)", value=str(val_p))
        d = st.text_area("Descripción", value=val_d)
        l = st.text_input("Link de Drive", value=str(val_l) if str(val_l) != "nan" else "")
        
        btn_txt = "🚀 ACTUALIZAR" if edit_id is not None else "🚀 GUARDAR"
        if st.form_submit_button(btn_txt):
            if t and p:
                # Limpiamos el precio de cualquier punto o coma accidental
                p_clean = p.replace(".", "").replace(",", "").strip()
                
                if edit_id is not None:
                    # Sobrescribimos la fila
                    df.loc[df['ID'] == edit_id, ['Titulo', 'Precio', 'Descripcion', 'LinkDrive']] = [t, p_clean, d, l]
                    st.session_state.edit_id = None
                else:
                    # Nueva propiedad
                    nuevo_id = datetime.now().timestamp()
                    nueva_fila = pd.DataFrame([[nuevo_id, datetime.now().strftime("%d/%m/%Y"), t, p_clean, d, l]], columns=df.columns)
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                
                df.to_csv(DB_FILE, index=False)
                st.success("¡Propiedad guardada!")
                st.rerun()

    if edit_id is not None:
        if st.button("❌ Cancelar Edición"):
            st.session_state.edit_id = None
            st.rerun()

# --- PÁGINA PORTFOLIO ---
else:
    st.title("🖼️ Portfolio Personal")
    
    if df.empty:
        st.info("No hay propiedades.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                # Formateo de precio con puntos para visualización: 1.500.000
                try:
                    # Convertimos a entero para quitar el .0 y luego ponemos puntos de miles
                    precio_final = f"{int(float(row['Precio'])):,}".replace(",", ".")
                except:
                    precio_final = row['Precio']

                # Tarjeta visual
                st.markdown(f'<div class="card"><h3>🏠 {row["Titulo"]}</h3><h4>USD {precio_final}</h4></div>', unsafe_allow_html=True)
                
                # Fila de botones
                c1, c2, c3, c4 = st.columns([2, 1, 0.5, 0.5])
                
                with c1:
                    pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'])
                    st.download_button("📄 ENVIAR FICHA", data=pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", key=f"pdf_{row['ID']}")
                
                with c2:
                    link = str(row['LinkDrive']).strip()
                    if link and link != "nan" and link != "":
                        st.link_button("📂 DRIVE", link, key=f"drv_{row['ID']}")
                    else:
                        st.button("📂 SIN LINK", disabled=True, key=f"no_{row['ID']}")
                
                with c3:
                    # BOTÓN EDITAR
                    if st.button("📝", key=f"ed_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
                
                with c4:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        df = df[df['ID'] != row['ID']]
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
