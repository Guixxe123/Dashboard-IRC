import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import tempfile
import base64
from fpdf import FPDF

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(page_title="Dashboard IRC", page_icon="✝️", layout="wide")

# CSS personalizado 
st.markdown("""
    <style>
    /* Importar fuente serif elegante de respaldo */
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;700&display=swap');

    /* Aplicar Bembo Book a TODO, con EB Garamond de respaldo */
    html, body, [class*="css"], .stApp, p, h1, h2, h3, div, span, label, button, input, select, textarea, table {
        font-family: 'Bembo Book', 'EB Garamond', 'Times New Roman', serif !important;
    }

    /* Fondo general de la aplicación */
    .stApp {
        background-color: #0A192F; 
        color: #E2E8F0; 
    }

    /* Título principal (SIN DISTORSIÓN) */
    .titulo-portada {
        font-size: 55px; 
        font-weight: 700;
        text-align: center;
        color: #FFFFFF; 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); 
        margin-bottom: 0px;
        padding-bottom: 10px;
        line-height: 1.2;
    }
    
    .subtitulo-portada {
        font-size: 22px;
        font-weight: 500;
        text-align: center;
        color: #A0AEC0;
        margin-top: 0px;
        margin-bottom: 30px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-family: 'Segoe UI', sans-serif !important; 
    }
    
    /* Adaptación para pantallas de Celular */
    @media (max-width: 768px) {
        .titulo-portada { font-size: 35px !important; }
        .subtitulo-portada { font-size: 14px !important; margin-bottom: 20px; }
    }
    
    .bienvenida {
        text-align: center; font-size: 24px; color: #F7FAFC; font-weight: 400;
        margin-top: 20px; margin-bottom: 30px;
    }

    /* ANIMACIÓN DE FLOTACIÓN (Cruz y Logo) */
    @keyframes float {
        0% { transform: translateY(0px); filter: drop-shadow(0 0 10px rgba(99, 179, 237, 0.4)); }
        50% { transform: translateY(-15px); filter: drop-shadow(0 0 25px rgba(99, 179, 237, 0.9)); }
        100% { transform: translateY(0px); filter: drop-shadow(0 0 10px rgba(99, 179, 237, 0.4)); }
    }
    
    .cruz-animada {
        width: 130px; animation: float 3.5s ease-in-out infinite; display: block;
        margin: 0 auto; margin-bottom: 20px;
    }

    /* ESTILO RESTAURADO: Logo Circular y Flotante */
    [data-testid="stImage"] img {
        border-radius: 50%; 
        box-shadow: 0 10px 30px rgba(99, 179, 237, 0.2);
        border: 4px solid #2B6CB0; 
        object-fit: cover; 
        animation: float 3.5s ease-in-out infinite;
    }

    /* NUEVO ESTILO: Fotos de Perfil (Cuadradas, bordes suaves, sin flotar) */
    .foto-perfil {
        border-radius: 12px; 
        width: 100%; 
        max-width: 350px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
        border: 2px solid #63B3ED;
        object-fit: cover;
    }

    /* Estilo para TODOS los botones */
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3182CE 100%) !important;
        color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #63B3ED !important;
        padding: 10px 15px !important; font-weight: 700 !important; letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4) !important; transition: all 0.3s ease !important; width: 100%;
        font-family: 'Segoe UI', sans-serif !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #2B6CB0 0%, #4299E1 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 179, 237, 0.8) !important; transform: translateY(-4px) !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Recuadros de métricas */
    [data-testid="metric-container"] {
        background-color: #112240; border: 1px solid #233554; border-radius: 12px;
        padding: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    [data-testid="metric-container"] label { color: #8892B0 !important; font-size: 18px !important; font-family: 'Segoe UI', sans-serif !important; }
    [data-testid="metric-container"] div { color: #63B3ED !important; font-size: 32px !important; }

    /* Entradas de texto */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
        background-color: #112240 !important; color: white !important; border-radius: 8px !important;
        border: 1px solid #2B6CB0 !important;
    }
    
    /* Pie de página */
    .footer-versiculo {
        text-align: center; font-size: 18px; font-style: italic; color: #8892B0;
        margin-top: 60px; padding-top: 20px; border-top: 1px solid #233554;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE DATOS Y COLUMNAS
# ==========================================
columnas_requeridas = [
    "ID", "Nombre Completo", "DPI", "Gafete", "Teléfono", "Correo", "Dirección", 
    "Fecha de Nacimiento", "Edad", "Género", 
    "Estado en Ministerio", "Ministerio", "Rol",
    "Tipo Vehículo", "Placas", "Marbete Pagado", "Tiene Foto", "Foto Base64"
]

if 'miembros_df' not in st.session_state:
    st.session_state.miembros_df = pd.DataFrame(columns=columnas_requeridas)
else:
    for col in columnas_requeridas:
        if col not in st.session_state.miembros_df.columns:
            st.session_state.miembros_df[col] = ""

if 'notas_db' not in st.session_state:
    st.session_state.notas_db = []

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def ir_a(pagina):
    st.session_state.menu_option = pagina

opciones_menu = ["🏠 Inicio", "📊 Dashboard", "➕ Agregar", "🚗 Vehículos", "📝 Notas", "📜 Carta Rec.", "🎂 Cumple", "🗑️ Eliminar", "💾 Exportar"]
                 
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = opciones_menu[0]

# ==========================================
# BARRA LATERAL 
# ==========================================
st.sidebar.markdown('''
    <svg class="cruz-animada" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="gradMadera" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8B5A2B;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#5C3A21;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#3E2723;stop-opacity:1" />
            </linearGradient>
        </defs>
        <path d="M40,10 L60,10 L60,40 L90,40 L90,60 L60,60 L60,110 L40,110 L40,60 L10,60 L10,40 L40,40 Z" 
              fill="url(#gradMadera)" stroke="#2E1A0F" stroke-width="2"/>
    </svg>
''', unsafe_allow_html=True)

st.sidebar.title("Menú Alterno")
menu = st.sidebar.radio("Ir a:", opciones_menu, key="menu_option")

df = st.session_state.miembros_df

# ==========================================
# FUNCIÓN DEL MENÚ SUPERIOR 
# ==========================================
def mostrar_menu_superior():
    st.write("") 
    r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
    with r1c1: st.button("🏠 Inicio", on_click=ir_a, args=("🏠 Inicio",))
    with r1c2: st.button("📊 Dashboard", on_click=ir_a, args=("📊 Dashboard",))
    with r1c3: st.button("➕ Agregar", on_click=ir_a, args=("➕ Agregar",))
    with r1c4: st.button("🚗 Vehículos", on_click=ir_a, args=("🚗 Vehículos",))
    with r1c5: st.button("📝 Notas", on_click=ir_a, args=("📝 Notas",))
    
    r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)
    with r2c1: st.button("📜 Carta Rec.", on_click=ir_a, args=("📜 Carta Rec.",))
    with r2c2: st.button("🎂 Cumple", on_click=ir_a, args=("🎂 Cumple",))
    with r2c3: st.button("🗑️ Eliminar", on_click=ir_a, args=("🗑️ Eliminar",))
    with r2c4: st.button("💾 Exportar", on_click=ir_a, args=("💾 Exportar",))
    st.write("---")

# ==========================================
# SECCIÓN 1: INICIO (PORTADA)
# ==========================================
if menu == "🏠 Inicio":
    st.markdown("""
        <style>
        .stApp {
            background-color: #0A192F !important;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(43, 108, 176, 0.25) 0%, transparent 65%),
                repeating-linear-gradient(45deg, rgba(255, 255, 255, 0.03) 0px, rgba(255, 255, 255, 0.03) 2px, transparent 2px, transparent 15px) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="titulo-portada">Pastor General José Manuel Rodríguez López</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-portada">DASHBOARD OFICIAL DE MIEMBROS (IRC)</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.image("https://images.unsplash.com/photo-1438032005730-c779502df39b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", use_container_width=True)
    
    mostrar_menu_superior()
    st.markdown("<p class='bienvenida'>Bienvenido al sistema integral de gestión congregacional.</p>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 2: DASHBOARD PRINCIPAL 
# ==========================================
elif menu == "📊 Dashboard":
    mostrar_menu_superior() 
    st.header("📊 Dashboard de Miembros")
    
    if df.empty:
        st.warning("No hay miembros registrados aún.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total Miembros", len(df))
        col2.metric("👑 Líderes Activos", len(df[df["Rol"] == "Líder del Ministerio"]))
        col3.metric("🚗 Vehículos Registrados", len(df[df["Tipo Vehículo"] != "Ninguno"]))
        col4.metric("📸 Con Foto", len(df[df["Tiene Foto"] == "Sí"]))
        
        st.write("---")
        st.subheader("🔍 Buscar y Filtrar")
        
        busqueda = st.text_input("Ingresa nombre, DPI o número de gafete para buscar...", "")
        
        if busqueda:
            df_mostrar = df[
                df["Nombre Completo"].astype(str).str.contains(busqueda, case=False, na=False) | 
                df["DPI"].astype(str).str.contains(busqueda, case=False, na=False) | 
                df["Gafete"].astype(str).str.contains(busqueda, case=False, na=False)
            ]
        else:
            df_mostrar = df

        # ================= PESTAÑAS =================
        tab1, tab2 = st.tabs(["📋 Vista de Tabla General", "👤 Ver Perfiles y Fotos"])
        
        with tab1:
            st.write("Datos generales de la congregación:")
            st.dataframe(df_mostrar.drop(columns=["ID", "Foto Base64"]), use_container_width=True)
            
        with tab2:
            st.write("Selecciona un miembro para ver su fotografía e información detallada:")
            if not df_mostrar.empty:
                miembro_seleccionado = st.selectbox("Seleccione el Miembro:", df_mostrar["Nombre Completo"].tolist())
                
                if miembro_seleccionado:
                    perfil = df_mostrar[df_mostrar["Nombre Completo"] == miembro_seleccionado].iloc[0]
                    
                    st.markdown("### 📌 Ficha de Miembro")
                    col_img, col_info = st.columns([1, 2])
                    
                    with col_img:
                        if pd.notna(perfil["Foto Base64"]) and perfil["Foto Base64"] != "":
                            try:
                                # Aquí usamos el HTML especial para que la foto de perfil no tome la animación del logo
                                html_foto = f'<img src="data:image/jpeg;base64,{perfil["Foto Base64"]}" class="foto-perfil">'
                                st.markdown(html_foto, unsafe_allow_html=True)
                            except Exception as e:
                                st.error("Error al cargar la imagen.")
                        else:
                            st.info("Este miembro no tiene fotografía registrada.")
                            
                    with col_info:
                        st.markdown(f"**Nombre:** {perfil['Nombre Completo']}")
                        st.markdown(f"**DPI:** {perfil['DPI']}")
                        st.markdown(f"**Gafete N°:** {perfil['Gafete']}")
                        st.markdown(f"**Teléfono:** {perfil['Teléfono']}")
                        st.markdown(f"**Edad:** {perfil['Edad']} años")
                        st.markdown(f"**Ministerio:** {perfil['Ministerio']} ({perfil['Rol']})")
                        
                        if perfil["Tipo Vehículo"] != "Ninguno":
                            st.markdown("---")
                            st.markdown("**🚗 Información de Vehículo:**")
                            st.markdown(f"**Tipo:** {perfil['Tipo Vehículo']} | **Placas:** {perfil['Placas']} | **Marbete:** {perfil['Marbete Pagado']}")

# ==========================================
# SECCIÓN 3: AGREGAR MIEMBRO
# ==========================================
elif menu == "➕ Agregar":
    mostrar_menu_superior()
    st.header("➕ Registro de Nuevo Miembro")
    
    with st.form("form_nuevo_miembro", clear_on_submit=True):
        st.subheader("Datos Personales")
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre = st.text_input("Nombre Completo *")
            dpi = st.text_input("DPI")
        with col2:
            fecha_nac = st.date_input("Fecha de Nac", min_value=date(1920, 1, 1), max_value=date.today())
            gafete = st.text_input("N° de Gafete")
        with col3:
            genero = st.selectbox("Género", ["Masculino", "Femenino"])
            foto = st.file_uploader("Subir Foto del Miembro", type=['png', 'jpg', 'jpeg'])
            
        st.subheader("Contacto y Control Automotriz")
        col4, col5, col6 = st.columns(3)
        with col4:
            telefono = st.text_input("Teléfono *")
            correo = st.text_input("Correo")
            direccion = st.text_input("Dirección")
        with col5:
            vehiculo = st.selectbox("Tipo de Vehículo", ["Ninguno", "Automóvil", "Motocicleta", "Microbús", "Otro"])
            placas = st.text_input("Placas (Si aplica)")
        with col6:
            marbete = st.selectbox("Marbete de Parqueo", ["No Aplica", "Pendiente", "Pagado/Vigente", "Cancelado"])

        st.subheader("Participación en la Iglesia")
        col7, col8 = st.columns(2)
        with col7:
            ministerios = ["Ninguno", "Alabanza", "Intercesión", "Diáconos (Servidores)", "Escuela Dominical", "Evangelismo", "Danza"]
            ministerio = st.selectbox("Ministerio", ministerios)
        with col8:
            rol = st.selectbox("Rol", ["No Aplica", "Miembro del Ministerio", "Líder del Ministerio"])

        st.write("* Campos obligatorios")
        submit = st.form_submit_button("💾 Guardar Registro Completo")
        
        if submit:
            if nombre == "" or telefono == "":
                st.error("Por favor, llena Nombre y Teléfono.")
            else:
                foto_b64 = ""
                tiene_foto = "No"
                if foto is not None:
                    foto_bytes = foto.read()
                    foto_b64 = base64.b64encode(foto_bytes).decode('utf-8')
                    tiene_foto = "Sí"

                edad = calcular_edad(fecha_nac)
                estado_ministerio = "Activo en Ministerio" if ministerio != "Ninguno" else "Solo Miembro"
                rol_final = rol if ministerio != "Ninguno" else "No Aplica"
                
                nuevo_registro = {
                    "ID": len(df) + 1, "Nombre Completo": nombre, "DPI": dpi, "Gafete": gafete, 
                    "Teléfono": telefono, "Correo": correo, "Dirección": direccion, 
                    "Fecha de Nacimiento": fecha_nac, "Edad": edad, "Género": genero,
                    "Estado en Ministerio": estado_ministerio, "Ministerio": ministerio, "Rol": rol_final,
                    "Tipo Vehículo": vehiculo, "Placas": placas, "Marbete Pagado": marbete, 
                    "Tiene Foto": tiene_foto, "Foto Base64": foto_b64
                }
                
                st.session_state.miembros_df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ ¡{nombre} registrado con éxito!")

# ==========================================
# SECCIÓN 4: VEHÍCULOS
# ==========================================
elif menu == "🚗 Vehículos":
    mostrar_menu_superior()
    st.header("🚗 Control de Vehículos y Marbetes")
    
    if df.empty:
        st.info("No hay datos en el sistema.")
    else:
        df_vehiculos = df[df["Tipo Vehículo"] != "Ninguno"][["Nombre Completo", "DPI", "Tipo Vehículo", "Placas", "Marbete Pagado"]]
        
        if df_vehiculos.empty:
            st.warning("Ningún miembro tiene vehículos registrados actualmente.")
        else:
            col1, col2 = st.columns(2)
            col1.metric("Total Vehículos Registrados", len(df_vehiculos))
            col2.metric("Marbetes Vigentes", len(df_vehiculos[df_vehiculos["Marbete Pagado"] == "Pagado/Vigente"]))
            
            st.dataframe(df_vehiculos, use_container_width=True)

# ==========================================
# SECCIÓN 5: NOTAS
# ==========================================
elif menu == "📝 Notas":
    mostrar_menu_superior()
    st.header("📝 Libreta de Notas Pastorales / Administrativas")
    
    with st.form("form_notas", clear_on_submit=True):
        titulo_nota = st.text_input("Título de la Nota")
        contenido_nota = st.text_area("Contenido / Observaciones", height=150)
        btn_nota = st.form_submit_button("💾 Guardar Nota")
        
        if btn_nota and titulo_nota != "":
            st.session_state.notas_db.append({
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Título": titulo_nota,
                "Contenido": contenido_nota
            })
            st.success("Nota guardada correctamente.")
            
    st.write("---")
    st.subheader("📚 Notas Guardadas")
    
    if len(st.session_state.notas_db) == 0:
        st.info("No hay notas guardadas aún.")
    else:
        for i, nota in enumerate(reversed(st.session_state.notas_db)):
            with st.expander(f"📌 {nota['Título']} ({nota['Fecha']})"):
                st.write(nota['Contenido'])

# ==========================================
# SECCIÓN 6: CARTA DE RECOMENDACIÓN
# ==========================================
elif menu == "📜 Carta Rec.":
    mostrar_menu_superior()
    st.header("📜 Generador de Carta de Recomendación")
    
    if df.empty:
        st.warning("No hay miembros registrados para generar cartas.")
    else:
        opciones_miembros = df['Nombre Completo'].tolist()
        miembro_seleccionado = st.selectbox("Seleccione el Miembro:", opciones_miembros)
        motivo = st.text_input("Dirigida a (Ej: A quien corresponda, Empresa X, etc.)", "A quien corresponda")
        
        if st.button("📄 Generar PDF"):
            datos_miembro = df[df['Nombre Completo'] == miembro_seleccionado].iloc[0]
            dpi_texto = str(datos_miembro['DPI']) if str(datos_miembro['DPI']) != "" else "[DPI NO REGISTRADO]"
            
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Times", 'B', 18)
            pdf.cell(0, 15, "IGLESIA RESTAURACIÓN CRISTIANA", ln=True, align='C')
            pdf.set_font("Times", 'B', 14)
            pdf.cell(0, 10, "CARTA DE RECOMENDACIÓN", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Times", '', 12)
            fecha_hoy = date.today().strftime("%d de %B de %Y")
            pdf.cell(0, 10, f"Fecha: {fecha_hoy}", ln=True, align='R')
            pdf.ln(10)
            
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 10, motivo.upper() + ":", ln=True, align='L')
            pdf.ln(5)
            
            pdf.set_font("Times", '', 12)
            texto_cuerpo = (
                f"Por este medio hacemos constar y extendemos la presente recomendación a favor de "
                f"{miembro_seleccionado}, quien se identifica con el Documento Personal de Identificación (DPI) "
                f"número {dpi_texto}. "
                f"\n\nDurante el tiempo de conocerle en nuestra congregación, ha demostrado ser una persona "
                f"responsable, honorable y de sólidos principios cristianos y morales, participando activamente "
                f"en nuestras actividades y mostrando un comportamiento ejemplar."
                f"\n\nPor lo anterior, no tenemos ningún inconveniente en recomendarle ampliamente para los fines "
                f"que considere convenientes."
            )
            pdf.multi_cell(0, 8, texto_cuerpo.encode('latin-1', 'ignore').decode('latin-1'))
            pdf.ln(25)
            
            pdf.cell(0, 8, "_________________________________________", ln=True, align='C')
            pdf.set_font("Times", 'B', 12)
            pdf.cell(0, 8, "Pastor General José Manuel Rodríguez López", ln=True, align='C')
            pdf.set_font("Times", '', 11)
            pdf.cell(0, 8, "Iglesia Restauración Cristiana (IRC)", ln=True, align='C')
            pdf.cell(0, 8, "(Firma y Sello)", ln=True, align='C')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    pdf_bytes = f.read()
            
            st.success("Carta generada con éxito.")
            st.download_button("🟥 Descargar Carta PDF", data=pdf_bytes, file_name=f"Recomendacion_{miembro_seleccionado.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# SECCIÓN 7: CUMPLEAÑOS
# ==========================================
elif menu == "🎂 Cumple":
    mostrar_menu_superior()
    st.header("🎂 Cumpleañeros del Mes")
    mes_actual = date.today().month
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    st.subheader(f"Mes actual: {meses_nombres[mes_actual - 1]}")
    
    if not df.empty:
        df['Mes_Nac'] = pd.to_datetime(df['Fecha de Nacimiento']).dt.month
        cumpleañeros = df[df['Mes_Nac'] == mes_actual].copy()
        
        if not cumpleañeros.empty:
            st.success(f"¡Tenemos {len(cumpleañeros)} cumpleañero(s) este mes!")
            st.table(cumpleañeros[["Nombre Completo", "Fecha de Nacimiento", "Edad", "Teléfono"]])
        else:
            st.info("No hay cumpleaños registrados para este mes.")
    else:
        st.warning("No hay datos registrados.")

# ==========================================
# SECCIÓN 8: ELIMINAR MIEMBRO
# ==========================================
elif menu == "🗑️ Eliminar":
    mostrar_menu_superior()
    st.header("🗑️ Eliminar Miembros")
    
    if df.empty:
        st.info("No hay miembros para eliminar.")
    else:
        st.warning("⚠️ Atención: Al eliminar un miembro, sus datos se borrarán permanentemente.")
        
        busqueda_eliminar = st.text_input("🔍 Buscar miembro a eliminar (Nombre o DPI)...", "")
        
        if busqueda_eliminar:
            df_filtro = df[
                df["Nombre Completo"].astype(str).str.contains(busqueda_eliminar, case=False, na=False) | 
                df["DPI"].astype(str).str.contains(busqueda_eliminar, case=False, na=False)
            ]
        else:
            df_filtro = df
            
        if not df_filtro.empty:
            opciones_eliminar = df_filtro['ID'].astype(str) + " - " + df_filtro['Nombre Completo']
            miembro_a_eliminar = st.selectbox("Selecciona el miembro a eliminar:", opciones_eliminar)
            
            if st.button("❌ Eliminar Definitivamente"):
                id_eliminar = int(miembro_a_eliminar.split(" - ")[0])
                st.session_state.miembros_df = df[df["ID"] != id_eliminar]
                st.success("Miembro eliminado correctamente.")
                st.rerun() 
        else:
            st.info("No se encontraron coincidencias en tu búsqueda.")

# ==========================================
# SECCIÓN 9: EXPORTAR DATOS
# ==========================================
elif menu == "💾 Exportar":
    mostrar_menu_superior()
    st.header("💾 Exportar Base de Datos")
    
    if df.empty:
        st.warning("No hay datos para exportar.")
    else:
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df.drop(columns=["ID", "Foto Base64"]).to_excel(writer, index=False, sheet_name='Miembros IRC')
        
        st.download_button("🟩 Descargar Directorio Completo en Excel", data=buffer_excel.getvalue(), file_name=f"Directorio_IRC_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==========================================
# FOOTER (VERSÍCULO)
# ==========================================
st.markdown('<div class="footer-versiculo">Colosenses 3:23: Hagan todo lo que hagan de corazón, como para el Señor y no para los hombres.</div>', unsafe_allow_html=True)
