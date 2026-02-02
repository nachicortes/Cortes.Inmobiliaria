import streamlit as st

# --- CONFIGURACIÓN Y ESTADO ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

if 'propiedades' not in st.session_state:
    # Datos de ejemplo iniciales
    st.session_state.propiedades = [
        {"nombre": "Lote en Cuesta de Manantiales", "precio": 42500, "drive": "#"},
        {"nombre": "Casa en las Sierras", "precio": 380000, "drive": "#"}
    ]
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=100) # Tu logo aquí
    st.write("### NAVEGACIÓN")
    
    # Manejo de navegación para permitir el salto automático al editar
    if st.session_state.edit_index is not None:
        nav_index = 0
    else:
        nav_index = 1 if "pagina" not in st.session_state or st.session_state.pagina == "PORTFOLIO" else 0

    menu = st.radio("", ["CARGAR", "PORTFOLIO"], index=nav_index, key="nav_radio")
    st.session_state.pagina = menu

    st.write("---")
    st.write("### Seguridad")
    st.button("💾 COPIA DE SEGURIDAD")

# --- LÓGICA DE CARGA / EDICIÓN ---
if st.session_state.pagina == "CARGAR":
    st.header("🏠 Cargar Propiedad")
    
    index = st.session_state.edit_index
    es_edicion = index is not None
    datos = st.session_state.propiedades[index] if es_edicion else {"nombre": "", "precio": 0, "drive": ""}

    with st.form("formulario"):
        nombre = st.text_input("Nombre de la propiedad", value=datos["nombre"])
        # Formato %d para evitar el .0 y permitir números grandes
        precio = st.number_input("Precio (USD)", value=int(datos["precio"]), step=1, format="%d")
        link_drive = st.text_input("Link de carpeta Drive", value=datos["drive"])
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            submit = st.form_submit_button("GUARDAR")
        
        if submit:
            nueva_prop = {"nombre": nombre, "precio": precio, "drive": link_drive}
            if es_edicion:
                st.session_state.propiedades[index] = nueva_prop
                st.session_state.edit_index = None
            else:
                st.session_state.propiedades.append(nueva_prop)
            st.session_state.pagina = "PORTFOLIO"
            st.rerun
