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

# CSS personalizado ultra moderno
st.markdown("""
    <style>
    /* Título principal con degradado premium */
    .titulo-portada {
        font-size: 65px;
        font-weight: 900;
        text-align: center;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        background: -webkit-linear-gradient(45deg, #1A365D, #2B6CB0, #3182CE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
        line-height: 1.2;
    }
    
    /* Subtítulo elegante */
    .subtitulo-portada {
        font-size: 28px;
        font-weight: 400;
        text-align: center;
        color: #718096;
        margin-top: 10px;
        margin-bottom: 50px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Frase de bienvenida */
    .bienvenida {
        text-align: center; 
        font-size: 26px; 
        color: #2D3748; 
        font-weight: 500;
        margin-top: 30px;
    }

    /* Convertir cualquier imagen de Streamlit en un círculo elegante con sombra */
    [data-testid="stImage"] img {
        border-radius: 50%;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        border: 5px solid #ffffff;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.03);
    }

    /* Botones modernos y redondeados */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2B6CB0 0%, #2C5282 100%);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 30px;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(43, 108, 176, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #3182CE 0%, #2B6CB0 100%);
        box-shadow: 0 8px 20px rgba(43, 108, 176, 0.4);
        transform: translateY(-3px);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE LA BASE DE DATOS
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

# ==========================================
# BARRA LATERAL DE NAVEGACIÓN
# ==========================================
# Cambié el logo lateral por uno más moderno también
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2072/2072130.png", width=120) 
st.sidebar.title("Navegación")
menu = st.sidebar.radio(
    "Ir a:",
    ["🏠 Inicio (Portada)", "📊 Dashboard Principal", "🎂 Cumpleaños del Mes", 
     "➕ Agregar Miembro", "🗑️ Eliminar Miembro", "💾 Exportar Datos"]
)

df = st.session_state.miembros_df

# ==========================================
# SECCIÓN 1: INICIO (PORTADA)
# ==========================================
if menu == "🏠 Inicio (Portada)":
    st.markdown('<p class="titulo-portada">IGLESIA RESTAURACIÓN CRISTIANA</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-portada">Dashboard Oficial de Miembros (IRC)</p>', unsafe_allow_html=True)
    
    # Se usan columnas para centrar perfectamente la imagen del logo
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        # Asegúrate de que tu imagen se llame exactamente "logo.png" y esté en la misma carpeta
        try:
            st.image("logo.png", use_container_width=True)
        except:
            # Si aún no subes el logo, mostrará una imagen por defecto elegante
            st.image("https://images.unsplash.com/photo-1438032005730-c779502df39b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80", use_container_width=True)
            st.info("💡 Sube tu archivo 'logo.png' a GitHub para que reemplace esta imagen por la de tu Iglesia.")
    
    st.write("---")
    st.markdown("<p class='bienvenida'>Bienvenido al sistema moderno de gestión de la congregación.</p>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 2: DASHBOARD PRINCIPAL
# ==========================================
elif menu == "📊 Dashboard Principal":
    st.header("📊 Dashboard de Miembros")
    
    if df.empty:
        st.warning("No hay miembros registrados aún. Ve a 'Agregar Miembro'.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Miembros", len(df))
        col2.metric("Líderes Activos", len(df[df["Rol"] == "Líder del Ministerio"]))
        col3.metric("En Ministerios", len(df[df["Estado en Ministerio"] == "Activo en Ministerio"]))
        
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
        submit = st.form_submit_button("Guardar Miembro")
        
        if submit:
            if nombre == "" or telefono == "":
                st.error("Por favor, llena los campos obligatorios (Nombre y Teléfono).")
            else:
                edad = calcular_edad(fecha_nac)
                nuevo_id = len(df) + 1
                
                nuevo_registro = {
                    "ID": nuevo_id,
                    "Nombre Completo": nombre,
                    "Teléfono": telefono,
                    "Correo": correo,
                    "Dirección": direccion,
                    "Fecha de Nacimiento": fecha_nac,
                    "Edad": edad,
                    "Género": genero,
                    "Estado en Ministerio": estado_ministerio,
                    "Ministerio": ministerio if estado_ministerio == "Activo en Ministerio" else "Ninguno",
                    "Rol": rol if estado_ministerio == "Activo en Ministerio" else "No Aplica"
                }
                
                st.session_state.miembros_df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ ¡{nombre} ha sido registrado exitosamente!")

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
        
        if st.button("Eliminar Definitivamente"):
            id_eliminar = int(miembro_a_eliminar.split(" - ")[0])
            st.session_state.miembros_df = df[df["ID"] != id_eliminar]
            st.success(f"Miembro eliminado correctamente.")
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
        
        # Encabezados del PDF
        pdf.set_font("Arial", 'B', 10)
        anchos = [70, 30, 20, 75, 75] 
        encabezados = ["Nombre", "Telefono", "Edad", "Ministerio", "Rol"]
        for i, col in enumerate(encabezados):
            pdf.cell(anchos[i], 10, col, border=1, align='C')
        pdf.ln()
        
        # Filas de datos
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="🟩 Descargar en Excel (.xlsx)",
                data=buffer_excel.getvalue(),
                file_name=f"Miembros_IRC_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        with col2:
            st.download_button(
                label="🟥 Descargar en PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"Miembros_IRC_{date.today()}.pdf",
                mime="application/pdf"
            )
