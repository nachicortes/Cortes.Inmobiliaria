import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# Inicialización de estados
if 'propiedades' not in st.session_state:
    st.session_state.propiedades = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- BARRA LATERAL (LOGO Y NAVEGACIÓN) ---
with st.sidebar:
    # Usamos una URL de imagen o el nombre de tu archivo local si lo tienes en el repo
    # st.image("logo.png", width=200) 
    st.markdown("### 🏠 CORTES INMOBILIARIA") 
    st.write("---")
    
    opciones = ["CARGAR", "PORTFOLIO"]
    # Si estamos editando, forzamos la vista a CARGAR
    idx_default = 0 if st.session_state.edit_index is not None else 1
    menu = st.radio("NAVEGACIÓN", opciones, index=idx_default)
    
    st.write("---")
    st.button("💾 COPIA DE SEGURIDAD")

# --- LÓGICA DE CARGA Y EDICIÓN ---
if menu == "CARGAR":
    st.header("Gestionar Propiedad")
    
    index_edit = st.session_state.edit_index
    es_edicion = index_edit is not None
    
    # Datos precargados si es edición
    datos_previos = st.session_state.propiedades[index_edit] if es_edicion else {"nombre": "", "precio": 0, "drive": ""}

    with st.form("form_gestion", clear_on_submit=True):
        nombre = st.text_input("Nombre de la propiedad", value=datos_previos["nombre"])
        
        # Soportamos millones: min_value 0, sin decimales (.0)
        precio = st.number_input("Precio (USD)", value=int(datos_previos["precio"]), step=1000, format="%d")
        
        url_drive = st.text_input("Link de carpeta Drive", value=datos_previos["drive"])
        
        texto_boton = "ACTUALIZAR" if es_edicion else "GUARDAR PROPIEDAD"
        if st.form_submit_button(texto_boton):
            nueva_data = {"nombre": nombre, "precio": precio, "drive": url_drive}
            
            if es_edicion:
                st.session_state.propiedades[index_edit] = nueva_data
                st.session_state.edit_index = None
            else:
                st.session_state.propiedades.append(nueva_data)
            
            st.rerun()

    if es_edicion:
        if st.button("Cancelar Edición"):
            st.session_state.edit_index = None
            st.rerun()

# --- PORTFOLIO ---
else:
    st.title("🖼️ Portfolio Personal")
    
    if not st.session_state.propiedades:
        st.info("No hay propiedades cargadas.")
    else:
        for i, prop in enumerate(st.session_state.propiedades):
            with st.container(border=True):
                # Formato Argentina: 1.500.000
                precio_millones = f"{prop['precio']:,}".replace(",", ".")
                
                st.subheader(f"🏠 {prop['nombre']}")
                st.write(f"### USD {precio_millones}")
                
                col1, col2, col3, col4 = st.columns([1, 1, 0.2, 0.2])
                
                with col1:
                    st.button("📄 ENVIAR FICHA", key=f"fich_{i}")
                
                with col2:
                    # CORRECCIÓN DE ERROR: Solo mostrar botón si hay link, sino poner texto
                    if prop['drive'] and
