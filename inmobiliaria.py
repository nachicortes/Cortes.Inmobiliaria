import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import requests
from io import BytesIO
import qrcode

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Cortés Inmo", layout="wide")

DB_FILE = "db_inmuebles_v5.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"]).to_csv(DB_FILE, index=False)

# --- FUNCIÓN PDF PROFESIONAL CORREGIDA ---
def crear_pdf(titulo, precio, fecha, desc, link):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO A COLOR (Desde tu GitHub)
    try:
        url_logo = "https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png"
        response = requests.get(url_logo)
        logo_data = BytesIO(response.content)
        # Guardamos el logo temporalmente para evitar errores de lectura
        with open("temp_logo.png", "wb") as f:
            f.write(logo_data.getbuffer())
        pdf.image("temp_logo.png", x=10, y=8, w=40) 
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="CORTÉS INMOBILIARIA", ln=True, align='R')

    pdf.ln(25)
    
    # 2. CUERPO DE LA FICHA
    pdf.set_draw_color(46, 125, 50) 
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, txt=f"{titulo.upper()}", ln=True, border='B', align='L')
    pdf.ln(5)
    
    pdf.set_text_color(46, 125, 50)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"VALOR: USD {precio}", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, txt=f"Publicado el: {fecha}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="Descripción:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=desc)
    pdf.ln(10)
    
    # 3. LINK DRIVE
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="VER FOTOS Y VIDEOS AQUÍ:", ln=True)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Arial", 'U', 10)
    pdf.multi_cell(0, 8, txt=link)
    
    # 4. CÓDIGO QR (SOLUCIÓN AL ERROR ATTRIBUTEERROR)
    try:
        pdf.set_y(-70)
        msg = f"Hola, me interesa la propiedad: {titulo}"
        wa_link = f"https://wa.me/5493513083986?text={msg.replace(' ', '%20')}"
        
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(wa_link)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        # Guardamos el QR físicamente antes de insertarlo
        img_qr.save("temp_qr.png")
        pdf.image("temp_qr.png", x=150, y=pdf.get_y(), w=40)
    except:
        pass # Si falla el QR, que igual genere el PDF
    
    # 5. DATOS DE CONTACTO
    pdf.set_y(-60)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="CONTACTO COMERCIAL:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, txt="WhatsApp: +54 9 351 308-3986", ln=True)
    pdf.set_text_color(228, 64, 95) 
    pdf.cell(0, 6, txt="Instagram: @cortes.inmo", ln=True)
    pdf.set_text_color(0, 0, 0) 
    pdf.cell(0, 6, txt="TikTok: @cortes.inmobiliaria", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.markdown("""
    <style>
    .stDownloadButton>button { background-color: #2e7d32 !important; color: white !important; border-radius: 12px; height: 4em; width: 100%; font-weight: bold; }
    .card { background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #f0f0f0; margin-bottom: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("NAVEGACIÓN", ["📂 CARGAR", "🖼️ PORTFOLIO"])

if menu == "📂 CARGAR":
    st.title("📂 Nueva Propiedad")
    with st.form("form_carga", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción")
        l = st.text_input("Link de Drive")
        if st.form_submit_button("🚀 GUARDAR EN PORTFOLIO"):
            if t and p and l:
                id_p = datetime.now().timestamp()
                df_n = pd.DataFrame([[id_p, datetime.now().strftime("%d/%m/%Y"), t, p, d, l]], 
                                    columns=["ID", "Fecha", "Titulo", "Precio", "Descripcion", "LinkDrive"])
                df_n.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                st.success("¡Propiedad Guardada!")

else:
    st.title("🖼️ Mi Portfolio")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card"><h2>🏠 {row["Titulo"]}</h2><h3 style="color: #2e7d32;">USD {row["Precio"]}</h3></div>', unsafe_allow_html=True)
                
                # Generamos el PDF pasando los datos de la fila
                pdf_bytes = crear_pdf(row['Titulo'], row['Precio'], row['Fecha'], row['Descripcion'], row['LinkDrive'])
                
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(label="📄 GENERAR Y ENVIAR FICHA", data=pdf_bytes, file_name=f"Ficha_{row['Titulo']}.pdf", mime="application/pdf")
                with c2:
                    if st.button(f"🗑️ Borrar", key=f"del_{row['ID']}"):
                        df[df['ID'] != row['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
