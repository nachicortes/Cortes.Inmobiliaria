import streamlit as st
import os
import pandas as pd
import shutil
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortes Inmo", layout="wide")

# --- DIRECTORIOS ---
BASE_DIR = "propiedades"
DB_FILE = "db_inmuebles.csv"

if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; background-color: #000000; color: white; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Menú:", ["📂 Cargar Propiedad", "🖼️ Ver Portfolio", "⚙️ Ajustes"])
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
                folder_name = t.replace(" ", "_").replace("/", "-")
                prop_folder = os.path.join(BASE_DIR, folder_name)
                if not os.path.exists(prop_folder): os.makedirs(prop_folder)
                
                for file in f:
                    with open(os.path.join(prop_folder, file.name), "wb") as b:
                        b.write(file.getbuffer())
                
                fecha = datetime.now().strftime("%d/%m/%Y")
                nuevo = pd.DataFrame([[fecha, t, p, d, prop_folder]], columns=["Fecha", "Titulo", "Precio", "Descripcion", "Carpeta"])
                nuevo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success(f"✅ ¡{t} guardado!")
            else:
                st.error("Faltan datos.")

# --- VISTA DE PORTFOLIO (ANTI-ERROR) ---
elif menu == "🖼️ Ver Portfolio":
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for i, row in df.iloc[::-1].iterrows():
                try: # BLINDAJE INDIVIDUAL POR FILA
                    titulo = row.get('Titulo', 'Sin Nombre')
                    precio = row.get('Precio', '0')
                    desc = row.get('Descripcion', '')
                    folder = row.get('Carpeta', '')
                    
                    with st.expander(f"🏠 {titulo} - USD {precio}"):
                        st.write(f"**Descripción:** {desc}")
                        if folder and os.path.exists(folder):
                            archivos = os.listdir(folder)
                            cols = st.columns(3)
                            for idx, arc in enumerate(archivos):
                                ruta = os.path.join(folder, arc)
                                with cols[idx % 3]:
                                    if arc.lower().endswith(('jpg','png','jpeg')): st.image(ruta)
                                    elif arc.lower().endswith(('mp4','mov')): st.video(ruta)
                except: continue
        except: st.warning("Cargá una propiedad para activar el portfolio.")
    else:
        st.info("Portfolio vacío.")

# --- AJUSTES PARA BORRAR TODO ---
else:
    st.title("⚙️ Configuración")
    if st.button("🗑️ REINICIAR TODO (BORRA TODO EL PORTFOLIO)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        if os.path.exists(BASE_DIR): shutil.rmtree(BASE_DIR)
        st.success("Sistema reseteado. Empezamos de cero sin errores.")
        st.rerun()

