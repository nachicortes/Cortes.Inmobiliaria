import streamlit as st
import pandas as pd
import os
from PIL import Image
from fpdf import FPDF

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")
ARCHIVO_DB = "db_inmuebles.csv"
CARPETA_RAIZ = "propiedades_datos"

# TUS DATOS (Ya integrados)
MI_CELU = "5493513083986"
LINK_IG = "https://www.instagram.com/cortes.inmo/"
LINK_TK = "https://www.tiktok.com/@cortes.inmobiliaria?_r=1&_t=ZS-93Wzt9Gbfd6"

if not os.path.exists(CARPETA_RAIZ):
    os.makedirs(CARPETA_RAIZ)

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        return pd.read_csv(ARCHIVO_DB)
    return pd.DataFrame(columns=["ID", "Título", "Tipo", "Precio", "Descripción"])

st.session_state.df = cargar_datos()

# --- FUNCIÓN PDF MEJORADA ---
def crear_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(200, 10, "Cortes Inmobiliaria", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, row['Título'].encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Precio: USD {row['Precio']:,}", ln=True)
    pdf.cell(200, 10, f"Tipo: {row['Tipo']}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Descripcion: {row['Descripción']}".encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(10)
    pdf.cell(200, 10, f"Contacto: {MI_CELU}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("Cortes Inmobiliaria")
    
    st.divider()
    st.subheader("📞 CONTACTO")
    link_wa_gral = f"https://wa.me/{MI_CELU}?text=Hola!%20Consulta%20desde%20tu%20Web"
    st.markdown(f'<a href="{link_wa_gral}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">WhatsApp</div></a>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Nuestras Redes")
    st.markdown(f'<a href="{LINK_IG}" target="_blank" style="text-decoration:none;"><div style="background:radial-gradient(circle at 30% 107%,#fdf497 0%,#fdf497 5%,#fd5949 45%,#d6249f 60%,#285AEB 90%);color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;margin-bottom:10px;">📸 Instagram</div></a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_TK}" target="_blank" style="text-decoration:none;"><div style="background-color:black;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">🎵 TikTok</div></a>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["📋 Catálogo", "➕ Registrar"])

with tab2:
    st.subheader("Cargar nuevo inmueble")
    with st.form("registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título")
            tipo = st.selectbox("Tipo", ["Casa", "Departamento", "Lote", "Local", "Campo"])
            precio = st.number_input("Precio (USD)", min_value=0)
        with col2:
            fotos = st.file_uploader("Fotos", type=["jpg","png","jpeg"], accept_multiple_files=True)
            video = st.file_uploader("Video", type=["mp4"])
            desc = st.text_area("Descripción")
        
        if st.form_submit_button("Guardar Propiedad"):
            nuevo_id = int(st.session_state.df['ID'].max() + 1) if not st.session_state.df.empty else 1
            carp = os.path.join(CARPETA_RAIZ, f"propiedad_{nuevo_id}")
            os.makedirs(carp, exist_ok=True)
            if fotos:
                for i, f in enumerate(fotos):
                    Image.open(f).save(os.path.join(carp, f"foto_{i}.jpg"))
            if video:
                with open(os.path.join(carp, "video.mp4"), "wb") as v:
                    v.write(video.getbuffer())
            
            nueva_fila = pd.DataFrame([{"ID": nuevo_id, "Título": titulo, "Tipo": tipo, "Precio": precio, "Descripción": desc}])
            st.session_state.df = pd.concat([st.session_state.df, nueva_fila], ignore_index=True)
            st.session_state.df.to_csv(ARCHIVO_DB, index=False)
            st.success("✅ ¡Guardado!")
            st.rerun()

with tab1:
    st.subheader("🔍 Buscador")
    c1, c2, c3 = st.columns(3)
    with c1: bus_t = st.text_input("Buscar por nombre")
    with c2: bus_tp = st.multiselect("Tipo", ["Casa", "Departamento", "Lote", "Local", "Campo"])
    with c3: bus_p = st.number_input("Precio Máximo", value=2000000)

    df_f = st.session_state.df.copy()
    if bus_t: df_f = df_f[df_f['Título'].str.contains(bus_t, case=False)]
    if bus_tp: df_f = df_f[df_f['Tipo'].isin(bus_tp)]
    df_f = df_f[df_f['Precio'] <= bus_p]

    for index, row in df_f.iterrows():
        with st.container(border=True):
            col_m, col_i = st.columns([1.5, 1])
            ruta = os.path.join(CARPETA_RAIZ, f"propiedad_{row['ID']}")
            
            with col_m:
                v_p = os.path.join(ruta, "video.mp4")
                if os.path.exists(v_p):
                    st.video(v_p)
                if os.path.exists(ruta):
                    fts = [f for f in os.listdir(ruta) if f.endswith(".jpg")]
                    if fts:
                        cg = st.columns(3)
                        for idx, fn in enumerate(fts):
                            with cg[idx % 3]:
                                st.image(os.path.join(ruta, fn), use_container_width=True)
            
            with col_i:
                st.header(row['Título'])
                st.subheader(f"USD {row['Precio']:,}")
                st.write(row['Descripción'])
                st.divider()
                
                # BOTONES CON KEYS ÚNICAS
                st.link_button("🟢 Consultar WhatsApp", f"https://wa.me/{MI_CELU}?text=Info%20sobre%20{row['Título']}")
                
                try:
                    pdf_bytes = crear_pdf(row)
                    st.download_button(label="📄 Ficha PDF", data=pdf_bytes, file_name=f"Ficha_{row['ID']}.pdf", mime="application/pdf", key=f"pdf_{row['ID']}")
                except:
                    st.error("Error al generar PDF")

                t_share = f"🏠 *{row['Título']}*\n💰 USD {row['Precio']:,}\n📍 {row['Tipo']}\n\n📲 Consulta al {MI_CELU}"
                if st.button("🔗 Texto para Redes", key=f"share_{row['ID']}"):
                    st.code(t_share, language=None)

                if st.button(f"🗑️ Eliminar", key=f"del_{row['ID']}"):
                    st.session_state.df = st.session_state.df[st.session_state.df.ID != row['ID']]
                    st.session_state.df.to_csv(ARCHIVO_DB, index=False)
                    st.rerun()