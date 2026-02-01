import streamlit as st
import os
import pandas as pd

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Portfolio Cortes Inmo", layout="wide")

# --- ESTILOS CORPORATIVOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000000; color: white; }
    .btn-side { padding: 12px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; } .tk { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles.csv"
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Titulo", "Precio", "Imagen"])
    df.to_csv(DB_FILE, index=False)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Gestión:", ["📂 Cargar al Portfolio", "🖼️ Ver Mis Propiedades"])
    st.markdown("---")
    st.markdown('<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA ---
if menu == "📂 Cargar al Portfolio":
    st.title("📂 Administrar Mis Propiedades")
    with st.form("form_personal", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        f = st.file_uploader("Foto Principal", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("✅ GUARDAR EN PORTFOLIO"):
            if t and p:
                # Guardamos los datos en el CSV local
                nueva_fila = pd.DataFrame([[t, p, "Imagen Guardada"]], columns=["Titulo", "Precio", "Imagen"])
                nueva_fila.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success(f"¡{t} guardado en tu base de datos personal!")
            else:
                st.error("Por favor, completá los datos básicos.")

# --- VISTA DE PORTFOLIO ---
else:
    st.title("🖼️ Mi Portfolio de Propiedades")
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        for index, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col2:
                    st.subheader(row['Titulo'])
                    st.write(f"**Precio:** {row['Precio']}")
                st.markdown("---")
    else:
        st.info("Todavía no cargaste propiedades a tu portfolio.")
