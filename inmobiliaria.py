import streamlit as st
import os
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Portfolio Cortes Inmo", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000000; color: white; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles.csv"
if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
    pd.DataFrame(columns=["Fecha", "Titulo", "Precio", "Descripcion"]).to_csv(DB_FILE, index=False)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Gestión:", ["📂 Cargar Propiedad", "🖼️ Ver Portfolio"])
    st.markdown("---")
    st.markdown('<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA ---
if menu == "📂 Cargar Propiedad":
    st.title("📂 Nueva Publicación")
    with st.form("form_full", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad (ej: Casa Valle Escondido)")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción de la propiedad")
        f = st.file_uploader("Subir Fotos y Videos", type=['jpg','png','jpeg','mp4','mov'], accept_multiple_files=True)
        
        if st.form_submit_button("✅ GUARDAR Y PREVISUALIZAR"):
            if t and p and f:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                nuevo = pd.DataFrame([[fecha, t, p, d]], columns=["Fecha", "Titulo", "Precio", "Descripcion"])
                nuevo.to_csv(DB_FILE, mode='a', header=False, index=False)
                
                st.success(f"¡{t} guardado! Mirá cómo quedó abajo:")
                # Previsualización inmediata
                for file in f:
                    if file.type.startswith('image'):
                        st.image(file, caption=t, use_container_width=True)
                    elif file.type.startswith('video'):
                        st.video(file)
            else:
                st.warning("Completá Título, Precio y subí archivos.")

# --- VISTA DE PORTFOLIO ---
else:
    st.title("🖼️ Mi Portfolio de Propiedades")
    try:
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            for i, row in df.iloc[::-1].iterrows(): # Mostrar lo último primero
                with st.expander(f"🏠 {row['Titulo']} - USD {row['Precio']}"):
                    st.write(f"**Fecha de carga:** {row['Fecha']}")
                    st.write(f"**Descripción:** {row['Descripcion']}")
                    st.info("💡 En esta versión de portfolio privado, los archivos cargados se procesan en el momento. Para que queden guardados permanentemente y se vean siempre, necesitamos alojarlos en una carpeta de GitHub.")
        else:
            st.info("No hay propiedades en el portfolio.")
    except Exception as e:
        st.error(f"Error al leer: {e}")
