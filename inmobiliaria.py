import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria - Gestión", layout="wide")

# --- INICIALIZACIÓN DE ESTADOS (Para que no se borren los datos al recargar) ---
if 'propiedades' not in st.session_state:
    st.session_state.propiedades = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- INFORMACIÓN DE CONTACTO (Tus datos guardados) ---
TELEFONO = "5493513083986"
INSTAGRAM = "https://www.instagram.com/cortes.inmo/"

# --- BARRA LATERAL (NAVEGACIÓN) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=100) # Aquí va tu logo de Cortes
    st.title("Navegación")
    # Si estamos editando, forzamos que la selección sea 'CARGAR'
    default_nav = "CARGAR" if st.session_state.edit_index is not None else "PORTFOLIO"
    menu = st.radio("Ir a:", ["CARGAR", "PORTFOLIO"], index=0 if default_nav == "CARGAR" else 1)
    
    st.write("---")
    st.subheader("Seguridad")
    if st.button("💾 COPIA DE SEGURIDAD"):
        st.success("Copia guardada")

# --- LÓGICA DE CARGA Y EDICIÓN ---
if menu == "CARGAR":
    st.header("🏠 Cargar / Editar Propiedad")
    
    # Si hay un índice de edición, precargamos los datos
    index = st.session_state.edit_index
    es_edicion = index is not None
    datos_previos = st.session_state.propiedades[index] if es_edicion else {}

    with st.form("form_propiedad", clear_on_submit=True):
        nombre = st.text_input("Nombre de la propiedad", value=datos_previos.get('nombre', ""))
        
        # CORRECCIÓN DE PRECIO: Usamos value=int() y format para evitar el .0
        precio = st.number_input("Precio (USD)", min_value=0, step=1, 
                                 value=int(datos_previos.get('precio', 0)), 
                                 format="%d")
        
        link_drive = st.text_input("Link de carpeta Drive", value=datos_previos.get('drive', ""))
        
        submitted = st.form_submit_button("GUARDAR PROPIEDAD")
        
        if submitted:
            nueva_prop = {
                "nombre": nombre,
                "precio": precio,
                "drive": link_drive
            }
            
            if es_edicion:
                st.session_state.propiedades[index] = nueva_prop
                st.session_state.edit_index = None # Resetear edición
                st.success("¡Propiedad actualizada!")
            else:
                st.session_state.propiedades.append(nueva_prop)
                st.success("¡Propiedad guardada con éxito!")
            
            st.rerun()

    if es_edicion:
        if st.button("Cancelar Edición"):
            st.session_state.edit_index = None
            st.rerun()

# --- PORTFOLIO (VISTA DE CLIENTE / ESPEJO) ---
elif menu == "PORTFOLIO":
    st.title("🖼️ Portfolio Personal")
    
    if not st.session_state.propiedades:
        st.info("No hay propiedades cargadas aún.")
    else:
        for i, prop in enumerate(st.session_state.propiedades):
            with st.container(border=True):
                col_info, col_btns = st.columns([3, 2])
                
                with col_info:
                    st.subheader(f"🏠 {prop['nombre']}")
                    # Formateo visual del precio con punto de miles
                    st.write(f"**USD {prop['precio']:,}**".replace(",", "."))
                
                with col_btns:
                    c1, c2, c3, c4 = st.columns(4)
                    
                    # 1. Enviar Ficha (Link Espejo simulado)
                    c1.button("📄", help="Enviar Ficha")
                    
                    # 2. WhatsApp (Link dinámico)
                    msg = f"Hola! Te comparto esta propiedad de Cortes Inmobiliaria: {prop['nombre']} - USD {prop['precio']}"
                    link_wa = f"https://wa.me/{TELEFONO}?text={msg.replace(' ', '%20')}"
                    c2.markdown(f"[![WA](https://img.shields.io/badge/WA-25D366?style=flat&logo=whatsapp)]({link_wa})")
                    
                    # 3. EDITAR
                    if c3.button("📝", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                    
                    # 4. BORRAR
                    if c4.button("🗑️", key=f"del_{i}"):
                        st.session_state.propiedades.pop(i)
                        st.rerun()
                
                st.link_button("📁 VER DRIVE", prop['drive'])
