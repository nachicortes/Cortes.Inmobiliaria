import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- ESTADOS DE SESIÓN ---
if 'propiedades' not in st.session_state:
    st.session_state.propiedades = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=100) # Tu logo
    st.write("### NAVEGACIÓN")
    
    # Manejo de navegación para edición
    opciones = ["CARGAR", "PORTFOLIO"]
    default_idx = 0 if st.session_state.edit_index is not None else 1
    
    menu = st.radio("Ir a:", opciones, index=default_idx)

    st.write("---")
    st.write("### Seguridad")
    st.button("💾 COPIA DE SEGURIDAD")

# --- SECCIÓN CARGAR / EDITAR ---
if menu == "CARGAR":
    st.header("🏠 Cargar / Editar Propiedad")
    
    idx = st.session_state.edit_index
    datos = st.session_state.propiedades[idx] if idx is not None else {"nombre": "", "precio": 0, "drive": ""}

    with st.form("form_carga"):
        nombre = st.text_input("Nombre de la propiedad", value=datos["nombre"])
        # Formato %d elimina el .0
        precio = st.number_input("Precio (USD)", value=int(datos["precio"]), step=1, format="%d")
        link_drive = st.text_input("Link de carpeta Drive", value=datos["drive"])
        
        submitted = st.form_submit_button("GUARDAR")
        
        if submitted:
            nueva_prop = {"nombre": nombre, "precio": precio, "drive": link_drive}
            if idx is not None:
                st.session_state.propiedades[idx] = nueva_prop
                st.session_state.edit_index = None
            else:
                st.session_state.propiedades.append(nueva_prop)
            st.rerun() # Esto ahora funcionará sin mostrar texto raro

    if idx is not None:
        if st.button("Cancelar Edición"):
            st.session_state.edit_index = None
            st.rerun()

# --- SECCIÓN PORTFOLIO ---
else:
    st.title("🖼️ Portfolio Personal")
    
    for i, prop in enumerate(st.session_state.propiedades):
        with st.container(border=True):
            # Formateo de miles para que se vea USD 8.888 o 380.000
            precio_formateado = f"{prop['precio']:,}".replace(",", ".")
            
            st.subheader(f"🏠 {prop['nombre']}")
            st.write(f"**USD {precio_formateado}**")
            
            # Botones abajo como en tu primer diseño
            col_ficha, col_drive, col_edit, col_del = st.columns([1.5, 1.5, 0.5, 0.5])
            
            with col_ficha:
                st.button("📄 ENVIAR FICHA", key=f"f_{i}")
            
            with col_drive:
                # Usamos link_button para que realmente abra el Drive
                st.link_button("📁 VER DRIVE", prop['drive'], key=f"d_{i}")
            
            with col_edit:
                if st.button("📝", key=f"e_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
            
            with col_del:
                if st.button("🗑️", key=f"b_{i}"):
                    st.session_state.propiedades.pop(i)
                    st.rerun()
