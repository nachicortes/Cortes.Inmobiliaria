import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortés Inmo", layout="wide")

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN GENERAR PDF PROFESIONAL ---
def crear_pdf(titulo, precio, fecha, desc, link):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado con Nombre de Inmobiliaria
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 15, txt="CORTÉS INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 5, txt="Ficha Técnica de Propiedad", ln=True, align='C')
    pdf.ln(10)
    
    # Cuerpo de la Ficha
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, txt=f" {titulo}", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"PRECIO: USD {precio}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, txt=f"Fecha de publicación: {fecha}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=desc)
    pdf.ln(10)
    
    # Enlace Multimedia
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, txt="LINK A FOTOS Y VIDEOS:", ln=True)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Arial", 'U', 10)
    pdf.multi_cell(0, 8, txt=link)
    
    # Pie de página con tus datos de contacto
    pdf.set_y(-50)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, txt="CONTACTO:", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, txt="Celular: +54 9 351 308-3986", ln=True)
    pdf.cell(0, 5, txt="Instagram: @cortes.inmo", ln=True)
    pdf.cell(0, 5, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- ESTILOS PARA MÓVIL ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 12px; height: 3.8em; width: 100%; font-weight: bold; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    h1, h2 { color: #1e1e1e; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
# He configurado el menú para que sea muy claro en el celular
menu = st.sidebar.radio("MENÚ PRINCIPAL", ["📂 Cargar Nueva", "🖼️ Ver Mi Portfolio"])
st.sidebar.markdown("---")
st.sidebar.write("**Mis Datos de Contacto:**")
st.sidebar.write("📞 3513083986")

# --- SECCIÓN 1: CARGA ---
if menu == "📂 Cargar Nueva":
    st.title("📂 Nueva Propiedad")
    with st.form("form_celular", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio (USD)")
        d = st.text_area("Descripción detallada")
        l = st.text_input("Link de Drive (Fotos/Videos)")
        
        if st.form_submit_button("✅ GUARDAR PROPIEDAD"):
            if t and p and l:
                fecha = datetime.now().strftime("%d/%m/%Y")
                id_prop = datetime.now().timestamp()
                nuevo = pd.DataFrame([[id_prop, fecha, t, p, d, l]], columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                nuevo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Propiedad guardada! Ya podés verla en el Portfolio.")
            else:
                st.error("Por favor completa Título, Precio y Link.")

# --- SECCIÓN 2: PORTFOLIO (VISIBLE Y FUNCIONAL) ---
else:
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("No hay propiedades registradas.")
        else:
            # Mostramos lo último cargado arriba de todo
            for i, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <h2 style="margin:0;">🏠 {row['Titulo']}</h2>
                        <h3 style="color: #2e7d32; margin:5px 0;">USD {row['Precio']}</h3>
                        <p style="font-size: 0.8em; color: gray;">Publicado: {row['Fecha']}</p>
                        <p>{row['Descripcion']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # Botón para generar y descargar PDF
                        pdf_data = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'], row['LinkDrive'])
                        st.download_button(
                            label="📄 FICHA PDF",
                            data=pdf_data,
                            file_name=f"Ficha_{row['Titulo']}.pdf",
                            mime="application/pdf"
                        )
                    with c2:
                        st.link_button("📂 FOTOS DRIVE", row['LinkDrive'])
                    
                    # Opción de borrado al final por si hubo error
                    if st.button(f"🗑️ Eliminar", key=f"del_{row['ID']}"):
                        df_new = df[df['ID'] != row['ID']]
                        df_new.to_csv(DB_FILE, index=False)
                        st.rerun()
                    st.markdown("---")
