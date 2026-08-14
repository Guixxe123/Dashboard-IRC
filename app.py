import streamlit as st
import pandas as pd
from datetime import date
import io
import tempfile
from fpdf import FPDF

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(page_title="Dashboard IRC", page_icon="🕊️", layout="wide")

# CSS personalizado para Modo Oscuro/Elegante y Botones Modernos
st.markdown("""
    <style>
    /* Fondo general de la aplicación */
    .stApp {
        background-color: #0A192F; /* Azul marino muy oscuro */
        color: #E2E8F0; /* Texto gris claro/blanco */
    }

    /* Título principal con degradado azul brillante adaptado a fondo oscuro */
    .titulo-portada {
        font-size: 65px;
        font-weight: 900;
        text-align: center;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        background: -webkit-linear-gradient(45deg, #63B3ED, #90CDF4, #E2E8F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
        line-height: 1.2;
    }
    
    /* Subtítulo elegante */
    .subtitulo-portada {
        font-size: 26px;
        font-weight: 500;
        text-align: center;
        color: #A0AEC0;
        margin-top: 10px;
        margin-bottom: 40px;
        letter-spacing: 2px;
    }
    
    /* Frase de bienvenida clara */
    .bienvenida {
        text-align: center; 
        font-size: 24px; 
        color: #F7FAFC; /* Blanco brillante */
        font-weight: 400;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    /* Logo Circular */
    [data-testid="stImage"] img {
        border-radius: 50%;
        box-shadow: 0 10px 30px rgba(99, 179, 237, 0.2); /* Sombra azulada */
        border: 4px solid #2B6CB0;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.05);
    }

    /* Estilo general para todos los botones */
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3182CE 100%) !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        border: 1px solid #63B3ED !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2B6CB0 0%, #4299E1 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 179, 237, 0.6) !important;
        transform: translateY(-3px) !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Recuadros de métricas (Totales) */
    [data-testid="metric-container"] {
        background-color: #112240;
        border: 1px solid #233554;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    [data-testid="metric-container"] label {
        color: #8892B0 !important;
        font-size: 18px !important;
    }
    [data-testid="metric-container"] div {
        color: #63B3ED !important;
    }

    /* Entradas de texto y selecciones más modernas */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #112240 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #2B6CB0 !important;
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

# Función para cambiar de página a través de botones
def ir_a(pagina):
    st.session_state.menu_option = pagina

# Configuramos la opción por defecto
opciones_menu = ["🏠 Inicio (Portada)", "📊 Dashboard Principal", "🎂 Cumpleaños del Mes", 
                 "➕ Agregar Miembro", "🗑️ Eliminar Miembro", "💾 Exportar Datos"]
                 
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = opciones_menu[0]

# ==========================================
# BARRA LATERAL DE NAVEGACIÓN
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2072/2072130.png", width=120) 
st.sidebar.title("Navegación")
# Ahora la barra lateral está conectada a nuestro estado de sesión
menu = st.sidebar.radio("Ir a:", opciones_menu, key="menu_option")

df = st.session_state.miembros_df

# ==========================================
# SECCIÓN 1: INICIO (PORTADA)
# ==========================================
if menu == "🏠 Inicio (Portada)":
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
    
    # Botón para ingresar al Dashboard
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        st.button("🚀 INGRESAR AL DASHBOARD", on_click=ir_a, args=("📊 Dashboard Principal",))

# ==========================================
# SECCIÓN 2: DASHBOARD PRINCIPAL
# ==========================================
elif menu == "📊 Dashboard Principal":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.header("📊 Dashboard de Miembros")
    with col_t2:
        # Botón rápido para agregar miembro
        st.write("") # Espaciador
        st.button("➕ Nuevo Miembro", on_click=ir_a, args=("➕ Agregar Miembro",))
    
    if df.empty:
        st.warning("No hay miembros registrados aún.")
    else:
        st.write("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total de Miembros", len(df))
        col2.metric("👑 Líderes Activos", len(df[df["Rol"] == "Líder del Ministerio"]))
        col3.metric("🔥 En Ministerios", len(df[df["Estado en Ministerio"] == "Activo en Ministerio"]))
        
        st.write("---")
        st.subheader("📋 Lista General de la Congregación")
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

# ==========================================
# SECCIÓN 3: CUMPLEAÑOS DEL MES
# ==========================================
elif menu == "🎂 Cumpleaños del Mes":
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
elif menu == "➕ Agregar Miembro":
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
            estado_ministerio = st.radio("¿Participa en algún ministerio?", ["Solo Miembro Normal", "Activo en Ministerio"])
            
            ministerios = ["Ninguno", "Alabanza", "Intercesión", "Diáconos (Servidores)", "Docentes de Escuela Dominical", "Evangelismo", "Danza"]
            ministerio = st.selectbox("Seleccione el Ministerio", ministerios)
            rol = st.selectbox("Rol en el Ministerio", ["Miembro del Ministerio", "Líder del Ministerio", "No Aplica"])

        st.write("* Campos obligatorios")
        submit = st.form_submit_button("💾 Guardar Miembro")
        
        if submit:
            if nombre == "" or telefono == "":
                st.error("Por favor, llena los campos obligatorios (Nombre y Teléfono).")
            else:
                edad = calcular_edad(fecha_nac)
                nuevo_id = len(df) + 1
                
                nuevo_registro = {
                    "ID": nuevo_id, "Nombre Completo": nombre, "Teléfono": telefono, "Correo": correo,
                    "Dirección": direccion, "Fecha de Nacimiento": fecha_nac, "Edad": edad, "Género": genero,
                    "Estado en Ministerio": estado_ministerio,
                    "Ministerio": ministerio if estado_ministerio == "Activo en Ministerio" else "Ninguno",
                    "Rol": rol if estado_ministerio == "Activo en Ministerio" else "No Aplica"
                }
                
                st.session_state.miembros_df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ ¡{nombre} ha sido registrado exitosamente!")

    st.write("---")
    # Botón para ir a eliminar miembros
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d2:
        st.button("🗑️ Ir a Eliminar Miembros", on_click=ir_a, args=("🗑️ Eliminar Miembro",))

# ==========================================
# SECCIÓN 5: ELIMINAR MIEMBRO
# ==========================================
elif menu == "🗑️ Eliminar Miembro":
    st.header("🗑️ Eliminar Miembros")
    
    if df.empty:
        st.info("No hay miembros para eliminar.")
    else:
        st.warning("⚠️ Atención: Al eliminar un miembro, sus datos se borrarán del sistema actual.")
        opciones_eliminar = df['ID'].astype(str) + " - " + df['Nombre Completo']
        miembro_a_eliminar = st.selectbox("Selecciona el miembro:", opciones_eliminar)
        
        # Botón normal (fuera del estilo estándar porque es para eliminar, pero tomará el diseño general)
        if st.button("❌ Eliminar Definitivamente"):
            id_eliminar = int(miembro_a_eliminar.split(" - ")[0])
            st.session_state.miembros_df = df[df["ID"] != id_eliminar]
            st.success("Miembro eliminado correctamente.")
            st.rerun() 

# ==========================================
# SECCIÓN 6: EXPORTAR DATOS (EXCEL / PDF)
# ==========================================
elif menu == "💾 Exportar Datos":
    st.header("💾 Exportar Base de Datos")
    
    if df.empty:
        st.warning("No hay datos para exportar.")
    else:
        st.dataframe(df.drop(columns=["ID"]))
        
        # --- EXCEL ---
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df.drop(columns=["ID"]).to_excel(writer, index=False, sheet_name='Miembros IRC')
            
        # --- PDF ---
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
        col1, col2, col3 = st.columns([1, 1, 1]) # Columnas ajustadas para los botones
        
        with col1:
            st.download_button("🟩 Descargar Excel", data=buffer_excel.getvalue(), file_name=f"Miembros_IRC_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col3:
            st.download_button("🟥 Descargar PDF", data=pdf_bytes, file_name=f"Miembros_IRC_{date.today()}.pdf", mime="application/pdf")
