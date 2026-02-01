import streamlit as st
import os
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortes Inmo", layout="wide")

# --- CREAR CARPETAS SI NO EXISTEN ---
BASE_DIR = "propiedades"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

DB_FILE = "db_inmuebles.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Fecha", "Titulo", "Precio", "Descripcion", "Carpeta"]).to_csv(DB_FILE, index=False)

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; background-color: #000000; color: white; height: 3em; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Menú:", ["📂 Cargar Propiedad", "🖼️ Ver Portfolio"])
    st.markdown("---")
    st.markdown(f'<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA ---
if menu == "📂 Cargar Propiedad":
    st.title("📂 Publicar Nueva Propiedad")
    with st.form("form_final", clear_on_submit=True):
        t = st.text_input("Nombre / Dirección")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        f = st.file_uploader("Fotos y Videos", type=['jpg','png','jpeg','mp4','mov'], accept_multiple_files=True)
        
        if st.form_submit_button("🚀 PUBLICAR"):
            if t and p and f:
                # 1. Crear carpeta específica para esta propiedad
                prop_folder = os.path.join(BASE_DIR, t.replace(" ", "_"))
                if not os.path.exists(prop_folder):
                    os.makedirs(prop_folder)
                
                # 2. Guardar archivos físicamente
                for file in f:
                    file_path = os.path.join(prop_folder, file.name)
                    with open(file_path, "wb") as buffer:
                        buffer.write(file.getbuffer())
                
                # 3. Guardar en CSV
                fecha = datetime.now().strftime("%d/%m/%Y")
                nuevo = pd.DataFrame([[fecha, t, p, d, prop_folder]], columns=["Fecha", "Titulo", "Precio", "Descripcion", "Carpeta"])
                nuevo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                
                st.success(f"✅ ¡{t} guardado con éxito en el almacén!")
            else:
                st.error("Completá todos los campos.")

# --- VISTA DE PORTFOLIO ---
else:
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for i, row in df.iloc[::-1].iterrows():
            with st.expander(f"🏠 {row['Titulo']} - USD {row['Precio']}"):
                st.write(f"**Fecha:** {row['Fecha']}")
                st.write(f"**Descripción:** {row['Descripcion']}")
                
                # Mostrar multimedia desde la carpeta guardada
                folder = row['Carpeta']
                if os.path.exists(folder):
                    archivos = os.listdir(folder)
                    cols = st.columns(3)
                    for idx, arc in enumerate(archivos):
                        ruta_arc = os.path.join(folder, arc)
                        with cols[idx % 3]:
                            if arc.lower().endswith(('jpg', 'jpeg', 'png')):
                                st.image(ruta_arc)
                            elif arc.lower().endswith(('mp4', 'mov')):
                                st.video(ruta_arc)
