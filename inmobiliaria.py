import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria - Portfolio", layout="wide")

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; background-color: #000000; color: white; height: 3em; width: 100%; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    .card { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border-left: 5px solid #000; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Menú de Gestión:", ["📂 Cargar Propiedad", "🖼️ Ver Portfolio"])
    st.markdown("---")
    st.markdown(f'<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA ---
if menu == "📂 Cargar Propiedad":
    st.title("📂 Nueva Publicación")
    st.info("💡 Paso previo: Creá la carpeta en tu Drive, subí las fotos y pegá el link acá.")
    
    with st.form("form_final", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción Detallada")
        l = st.text_input("Enlace de la carpeta de Drive (Link compartido)")
        
        if st.form_submit_button("🚀 GUARDAR EN MI PORTFOLIO"):
            if t and p and l:
                fecha = datetime.now().strftime("%d/%m/%Y")
                id_prop = datetime.now().timestamp()
                nuevo = pd.DataFrame([[id_prop, fecha, t, p, d, l]], columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                nuevo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success(f"✅ Propiedad '{t}' guardada con éxito.")
            else:
                st.error("Por favor, completá Título, Precio y el Link de Drive.")

# --- VISTA DE PORTFOLIO ---
else:
    st.title("🖼️ Mi Portfolio de Propiedades")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("No hay propiedades cargadas.")
        else:
            for i, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <h3>🏠 {row['Titulo']} - USD {row['Precio']}</h3>
                        <p><b>Fecha:</b> {row['Fecha']}</p>
                        <p><b>Descripción:</b> {row['Descripcion']}</p>
                        <a href="{row['LinkDrive']}" target="_blank" style="color: #007bff; font-weight: bold;">📂 Ver Fotos y Videos en Drive →</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🗑️ Eliminar {row['Titulo']}", key=f"del_{row['ID']}"):
                        df_new = df[df['ID'] != row['ID']]
                        df_new.to_csv(DB_FILE, index=False)
                        st.rerun()

