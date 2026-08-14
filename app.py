import streamlit as st
import pandas as pd
from datetime import date
import io
import tempfile
from fpdf import FPDF

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(page_title="Dashboard IRC", page_icon="✝️", layout="wide")

# CSS personalizado para Modo Oscuro/Elegante, Animaciones, Fuentes y Botones
st.markdown("""
    <style>
    /* Importar fuente de letra de carta (cursiva y elegante) */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');

    /* Fondo general de la aplicación */
    .stApp {
        background-color: #0A192F; 
        color: #E2E8F0; 
    }

    /* Título principal más grande y con letra de carta */
    .titulo-portada {
        font-size: 90px;
        font-weight: 700;
        text-align: center;
        font-family: 'Dancing Script', cursive;
        background: -webkit-linear-gradient(45deg, #63B3ED, #90CDF4, #E2E8F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 10px;
        line-height: 1.1;
    }
    
    .subtitulo-portada {
        font-size: 22px;
        font-weight: 500;
        text-align: center;
        color: #A0AEC0;
        margin-top: 0px;
        margin-bottom: 40px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .bienvenida {
        text-align: center; 
        font-size: 24px; 
        color: #F7FAFC; 
        font-weight: 400;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    /* ANIMACIÓN DE FLOTACIÓN (Cruz y Logo) */
    @keyframes float {
        0% { transform: translateY(0px); filter: drop-shadow(0 0 10px rgba(99, 179, 237, 0.4)); }
        50% { transform: translateY(-15px); filter: drop-shadow(0 0 25px rgba(99, 179, 237, 0.9)); }
        100% { transform: translateY(0px); filter: drop-shadow(0 0 10px rgba(99, 179, 237, 0.4)); }
    }
    
    .cruz-animada {
        width: 130px;
        animation: float 3.5s ease-in-out infinite;
        display: block;
        margin: 0 auto;
        margin-bottom: 20px;
    }

    /* Logo Circular con animación de flotación */
    [data-testid="stImage"] img {
        border-radius: 50%;
        box-shadow: 0 10px 30px rgba(99, 179, 237, 0.2);
        border: 4px solid #2B6CB0;
        object-fit: cover;
        animation: float 3.5s ease-in-out infinite;
    }

    /* Estilo general para todos los botones */
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3182CE 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #63B3ED !important;
        padding: 10px 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2B6CB0 0%, #4299E1 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 179, 237, 0.8) !important;
        transform: translateY(-3px) !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Recuadros de métricas */
    [data-testid="metric-container"] {
        background-color: #112240;
        border: 1px solid #233554;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    [data-testid="metric-container"] label { color: #8892B0 !important; font-size: 18px !important; }
    [data-testid="metric-container"] div { color: #63B3ED !important; font-size: 32px !important; }

    /* Entradas de texto */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #112240 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #2B6CB0 !important;
    }
    
    /* Pie de página (Versículo) */
    .footer-versiculo {
        text-align: center;
        font-size: 18px;
        font-style: italic;
        color: #8892B0;
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #233554;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE DATOS Y ESTADO DE NAVEGACIÓN
# ==========================================
if 'miembros_df' not in st.session_state:
    st.session_state.miembros_df = pd.DataFrame(columns=[
        "ID", "Nombre Completo", "Teléfono", "Correo", "Dirección", 
        "Fecha de Nacimiento", "Edad", "Género", 
        "Estado en Ministerio", "Ministerio", "Rol"
    ])

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def ir_a(pagina):
    st.session_state.menu_option = pagina

opciones_menu = ["🏠 Inicio", "📊 Dashboard", "🎂 Cumpleaños", "➕ Agregar", "🗑️ Eliminar", "💾 Exportar"]
                 
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = opciones_menu[0]

# ==========================================
# BARRA LATERAL (Con la cruz animada)
# ==========================================
st.sidebar.markdown('<img src="https://cdn-icons-png.flaticon.com/512/1051/1051474.png" class="cruz-animada">', unsafe_allow_html=True)

st.sidebar.title("Menú Alterno")
menu = st.sidebar.radio("Ir a:", opciones_menu, key="menu_option")

df = st.session_state.miembros_df

# ==========================================
# BARRA DE NAVEGACIÓN SUPERIOR
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
nav1, nav2, nav3, nav4, nav5, nav6 = st.columns(6)
with nav1: st.button("🏠 Inicio", on_click=ir_a, args=("🏠 Inicio",), use_container_width=True)
with nav2: st.button("📊 Dashboard", on_click=ir_a, args=("📊 Dashboard",), use_container_width=True)
with nav3: st.button("🎂 Cumple", on_click=ir_a, args=("🎂 Cumpleaños",), use_container_width=True)
with nav4: st.button("➕ Agregar", on_click=ir_a, args=("➕ Agregar",), use_container_width=True)
with nav5: st.button("🗑️ Eliminar", on_click=ir_a, args=("🗑️ Eliminar",), use_container_width=True)
with nav6: st.button("💾 Exportar", on_click=ir_a, args=("💾 Exportar",), use_container_width=True)
st.write("---")

# ==========================================
# SECCIÓN 1: INICIO (PORTADA)
# ==========================================
if menu == "🏠 Inicio":
    st.markdown('<p class="titulo-portada">IGLESIA RESTAURACIÓN CRISTIANA</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-portada">DASHBOARD OFICIAL DE MIEMBROS (IRC)</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.image("https://images.unsplash.com/photo-1438032005730-c779502df39b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", use_container_width=True)
            st.info("💡 Sube tu archivo 'logo.png' a GitHub.")
    
    st.markdown("<p class='bienvenida'>Bienvenido al sistema moderno de gestión de la congregación.</p>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        st.button("🚀 INGRESAR AL DASHBOARD", on_click=ir_a, args=("📊 Dashboard",), use_container_width=True)

# ==========================================
# SECCIÓN 2: DASHBOARD PRINCIPAL
# ==========================================
elif menu == "📊 Dashboard":
    st.header("📊 Dashboard de Miembros")
    
    if df.empty:
        st.warning("No hay miembros registrados aún. Usa el botón '➕ Agregar' del menú superior.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total de Miembros", len(df))
        col2.metric("👑 Líderes Activos", len(df[df["Rol"] == "Líder del Ministerio"]))
        col3.metric("🔥 En Ministerios", len(df[df["Estado en Ministerio"] == "Activo en Ministerio"]))
        col4.metric("🚶 No Activos / Miembros", len(df[df["Estado en Ministerio"] == "Solo Miembro Normal"]))
        
        st.write("---")
        st.subheader("📋 Lista General de la Congregación")
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

# ==========================================
# SECCIÓN 3: CUMPLEAÑOS DEL MES
# ==========================================
elif menu == "🎂 Cumpleaños":
    st.header("🎂 Cumpleañeros de este Mes")
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
# SECCIÓN 4: AGREGAR MIEMBRO
# ==========================================
elif menu == "➕ Agregar":
    st.header("➕ Registro de Nuevo Miembro")
    
    with st.form("form_nuevo_miembro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre Completo *")
            telefono = st.text_input("Número de Teléfono *")
            correo = st.text_input("Correo Electrónico (Opcional)")
            direccion = st.text_input("Dirección (Opcional)")
            genero = st.selectbox("Género", ["Masculino", "Femenino"])
            
        with col2:
            fecha_nac = st.date_input("Fecha de Nacimiento *", min_value=date(1920, 1, 1), max_value=date.today())
            
            st.write("### Participación en la Iglesia")
            ministerios = ["Ninguno", "Alabanza", "Intercesión", "Diáconos (Servidores)", "Docentes de Escuela Dominical", "Evangelismo", "Danza"]
            ministerio = st.selectbox("Seleccione el Ministerio", ministerios)
            
            rol = st.selectbox("Rol en el Ministerio", ["No Aplica", "Miembro del Ministerio", "Líder del Ministerio"])

        st.write("* Campos obligatorios")
        submit = st.form_submit_button("💾 Guardar Miembro")
        
        if submit:
            if nombre == "" or telefono == "":
                st.error("Por favor, llena los campos obligatorios (Nombre y Teléfono).")
            else:
                edad = calcular_edad(fecha_nac)
                nuevo_id = len(df) + 1
                
                estado_ministerio = "Activo en Ministerio" if ministerio != "Ninguno" else "Solo Miembro Normal"
                rol_final = rol if ministerio != "Ninguno" else "No Aplica"
                
                nuevo_registro = {
                    "ID": nuevo_id, "Nombre Completo": nombre, "Teléfono": telefono, "Correo": correo,
                    "Dirección": direccion, "Fecha de Nacimiento": fecha_nac, "Edad": edad, "Género": genero,
                    "Estado en Ministerio": estado_ministerio,
                    "Ministerio": ministerio,
                    "Rol": rol_final
                }
                
                st.session_state.miembros_df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ ¡{nombre} ha sido registrado exitosamente!")

# ==========================================
# SECCIÓN 5: ELIMINAR MIEMBRO
# ==========================================
elif menu == "🗑️ Eliminar":
    st.header("🗑️ Eliminar Miembros")
    
    if df.empty:
        st.info("No hay miembros para eliminar.")
    else:
        st.warning("⚠️ Atención: Al eliminar un miembro, sus datos se borrarán del sistema actual.")
        opciones_eliminar = df['ID'].astype(str) + " - " + df['Nombre Completo']
        miembro_a_eliminar = st.selectbox("Selecciona el miembro:", opciones_eliminar)
        
        if st.button("❌ Eliminar Definitivamente"):
            id_eliminar = int(miembro_a_eliminar.split(" - ")[0])
            st.session_state.miembros_df = df[df["ID"] != id_eliminar]
            st.success("Miembro eliminado correctamente.")
            st.rerun() 

# ==========================================
# SECCIÓN 6: EXPORTAR DATOS (EXCEL / PDF)
# ==========================================
elif menu == "💾 Exportar":
    st.header("💾 Exportar Base de Datos")
    
    if df.empty:
        st.warning("No hay datos para exportar.")
    else:
        st.dataframe(df.drop(columns=["ID"]))
        
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df.drop(columns=["ID"]).to_excel(writer, index=False, sheet_name='Miembros IRC')
            
        pdf = FPDF(orientation='L') 
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "IGLESIA RESTAURACION CRISTIANA (IRC)", ln=True, align='C')
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, "Directorio Oficial de Miembros", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        anchos = [70, 30, 20, 75, 75] 
        encabezados = ["Nombre", "Telefono", "Edad", "Ministerio", "Rol"]
        for i, col in enumerate(encabezados):
            pdf.cell(anchos[i], 10, col, border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", '', 9)
        for _, row in df.iterrows():
            nombre = str(row['Nombre Completo']).encode('latin-1', 'ignore').decode('latin-1')[:35]
            tel = str(row['Teléfono']).encode('latin-1', 'ignore').decode('latin-1')
            edad = str(row['Edad'])
            minis = str(row['Ministerio']).encode('latin-1', 'ignore').decode('latin-1')[:35]
            rol = str(row['Rol']).encode('latin-1', 'ignore').decode('latin-1')[:35]
            
            pdf.cell(anchos[0], 10, nombre, border=1)
            pdf.cell(anchos[1], 10, tel, border=1, align='C')
            pdf.cell(anchos[2], 10, edad, border=1, align='C')
            pdf.cell(anchos[3], 10, minis, border=1)
            pdf.cell(anchos[4], 10, rol, border=1)
            pdf.ln()
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                pdf_bytes = f.read()
        
        st.write("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.download_button("🟩 Descargar Excel", data=buffer_excel.getvalue(), file_name=f"Miembros_IRC_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col3:
            st.download_button("🟥 Descargar PDF", data=pdf_bytes, file_name=f"Miembros_IRC_{date.today()}.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# FOOTER (VERSÍCULO)
# ==========================================
st.markdown('<div class="footer-versiculo">Colosenses 3:23: Hagan todo lo que hagan de corazón, como para el Señor y no para los hombres.</div>', unsafe_allow_html=True)
