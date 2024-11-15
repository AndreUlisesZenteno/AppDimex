import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
def cargar_estilos():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Llama a la función para cargar los estilos CSS personalizados
cargar_estilos()
# Simulación de usuarios registrados
usuarios = {
    "user1@example.com": "password1",
    "user2@example.com": "password2"
}

# Cargar el archivo CSV
try:
    df_mo = pd.read_csv('df_mo_coords.csv')
    df_mo.columns = df_mo.columns.str.strip()

    if 'Solicitud_id' not in df_mo.columns:
        st.error("No se encontró la columna 'Solicitud_id'.")
        st.stop()
except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    st.stop()

# Diccionarios
atraso_dict = {
    0: 'atraso_120_149',
    1: 'atraso_150_179',
    2: 'atraso_180_más',
    3: 'atraso_1_29',
    4: 'atraso_30_59',
    5: 'atraso_60_89',
    6: 'atraso_90_119'
}

estatus_dict = {
    0: 'Cuenta Contenida',
    1: 'Cuenta Deteriorada',
    2: 'Cuenta Regularizada'
}

# Inicializar el estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'interacciones' not in st.session_state:
    st.session_state.interacciones = []
if 'mostrar_formulario' not in st.session_state:
    st.session_state.mostrar_formulario = False

def login(email, password):
    """Función para autenticar usuarios"""
    if email in usuarios and usuarios[email] == password:
        st.session_state.logged_in = True
        return True
    return False

def mostrar_lista_usuarios():
    """Muestra la lista de usuarios con filtros"""
    st.title("Listado de Usuarios")
    
    filtro_credito = st.number_input("Línea de Crédito mínima", min_value=0, step=1000, value=0)
    filtro_atraso = st.selectbox("Nivel de Atraso", ["Todos"] + list(atraso_dict.values()))

    df_filtrado = df_mo.copy()
    
    if filtro_credito > 0:
        df_filtrado = df_filtrado[df_filtrado['Linea credito'] >= filtro_credito]
    if filtro_atraso != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Nivel_Atraso_encoded'].map(atraso_dict) == filtro_atraso]
    
    st.subheader("Usuarios Filtrados")
    st.table(df_filtrado[['Solicitud_id', 'Linea credito', 'Nivel_Atraso_encoded']].rename(
        columns={'Solicitud_id': 'ID', 'Linea credito': 'Línea de Crédito', 'Nivel_Atraso_encoded': 'Nivel de Atraso'}
    ))
df_mo['Capacidad_Pago'] = df_mo['Capacidad_Pago'].apply(lambda x: f"{x:.2%}")
def mostrar_informacion_usuario(solicitud_id):
    """Muestra la información del usuario y un mapa con la ubicación."""
    solicitud_data = df_mo[df_mo['Solicitud_id'] == solicitud_id]
    if solicitud_data.empty:
        st.warning("No se encontró información para este ID.")
        return

    # Mostrar métricas principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Línea de crédito", f"${solicitud_data['Linea credito'].values[0]:,.0f}")
    col2.metric("Pago", f"${solicitud_data['Pago'].values[0]:,.0f}")
    col3.metric("Plazo a Meses", solicitud_data['Plazo_Meses'].values[0])
    col4.metric("Capacidad De Pago", solicitud_data['Capacidad_Pago'].values[0])
    # Mostrar mapa si hay coordenadas
    st.subheader("Ubicación del Cliente")
    if 'latitude' in solicitud_data.columns and 'longitude' in solicitud_data.columns:
        coordenadas = solicitud_data[['latitude', 'longitude']].dropna()
        
        if not coordenadas.empty:
            st.map(coordenadas)
        else:
            st.info("No hay coordenadas disponibles para mostrar en el mapa.")
    else:
        st.warning("Las columnas de coordenadas no están disponibles en el DataFrame.")
def mostrar_historial_interacciones(solicitud_id):
    """Muestra el historial de interacciones para un ID específico y permite crear nuevas interacciones"""
    st.subheader(f"Historial de Interacciones para ID: {solicitud_id}")
    
    # Mostrar interacciones previas desde el archivo CSV (df_mo)
    solicitud_data = df_mo[df_mo['Solicitud_id'] == solicitud_id]
    if not solicitud_data.empty:
        st.write("Interacciones previas registradas en el sistema:")
        
        required_columns = [
            'Tipo_Gestión Puerta a Puerta', 'Tipo_Call Center', 
            'Tipo_Agencias Especializadas', 'Resultado_Atendió cliente',
            'Promesa_Sí', 'Promesa_No'
        ]
        
        # Verificar si las columnas existen antes de mostrarlas
        if all(col in solicitud_data.columns for col in required_columns):
            for _, row in solicitud_data.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.write(f"Gestión Puerta a Puerta: {row['Tipo_Gestión Puerta a Puerta']}")
                col2.write(f"Gestión Call Center: {row['Tipo_Call Center']}")
                col3.write(f"Gestión Agencias Especializadas: {row['Tipo_Agencias Especializadas']}")
                col4.write(f"Resultado Atendió Cliente: {row['Resultado_Atendió cliente']}")
                col5.write(f"Promesa: {row['Promesa_Sí']}")
                col6.write(f"No hubo promesa: {row['Promesa_No']}")
                st.write("---")
        else:
            st.warning("Las columnas necesarias no están presentes en el archivo CSV.")
    else:
        st.info("No hay interacciones previas registradas para este ID.")

    # Mostrar interacciones guardadas en st.session_state
    st.write("Interacciones creadas por el usuario:")
    interacciones_filtradas = [i for i in st.session_state.interacciones if i["Solicitud_id"] == solicitud_id]
    if interacciones_filtradas:
        st.table(interacciones_filtradas)
    else:
        st.info("No hay interacciones creadas para este ID.")

    # Botón para crear una nueva interacción
    if st.button("Crear nueva interacción"):
        st.session_state.mostrar_formulario = True

    if st.session_state.get('mostrar_formulario', False):
        st.subheader("Crear Nueva Interacción")
        crear_interaccion(solicitud_id)

def crear_interaccion(solicitud_id):
    """Formulario para crear una nueva interacción vinculada a un ID y generar un PDF"""
    # Obtener el estatus de la cuenta desde el DataFrame
    solicitud_data = df_mo[df_mo['Solicitud_id'] == solicitud_id]
    if not solicitud_data.empty:
        estatus_cuenta = estatus_dict.get(solicitud_data['Estatus_Cuenta_encoded'].values[0], "Desconocido")
    else:
        estatus_cuenta = "Desconocido"

    # Campo autorrellenado y deshabilitado
    estatus_seleccionado = st.text_input("Estatus de la Cuenta", value=estatus_cuenta, disabled=True)
    
    # Otros campos del formulario
    resultado_seleccionado = st.selectbox("Resultado", ["Respondió", "No Respondió"])
    promesa_seleccionada = st.selectbox("Promesa", ["Sí", "No"])
    fecha_pago_estimada = st.date_input("Plazo de Pago Estimado", date.today())

    if st.button("Guardar Interacción"):
        nueva_interaccion = {
            "Solicitud_id": solicitud_id,
            "Estatus": estatus_seleccionado,
            "Resultado": resultado_seleccionado,
            "Promesa": promesa_seleccionada,
            "Fecha de Pago Estimada": fecha_pago_estimada
        }
        st.session_state.interacciones.append(nueva_interaccion)
        st.success("Interacción guardada exitosamente")

        # Generar PDF de la interacción guardada
        generar_pdf(nueva_interaccion)
        st.session_state.mostrar_formulario = False


def generar_pdf(interaccion):
    """Genera un PDF con la información de la interacción"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.cell(200, 10, txt="Reporte de Interacción", ln=True, align='C')
    pdf.ln(10)

    # Información de la interacción
    pdf.cell(200, 10, txt=f"ID de Solicitud: {interaccion['Solicitud_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Estatus de la Cuenta: {interaccion['Estatus']}", ln=True)
    pdf.cell(200, 10, txt=f"Resultado: {interaccion['Resultado']}", ln=True)
    pdf.cell(200, 10, txt=f"Promesa: {interaccion['Promesa']}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de Pago Estimada: {interaccion['Fecha de Pago Estimada']}", ln=True)

    # Guardar el PDF en un archivo temporal
    pdf_path = f"interaccion_{interaccion['Solicitud_id']}.pdf"
    pdf.output(pdf_path)

    # Mostrar un botón para descargar el PDF
    with open(pdf_path, "rb") as file:
        st.download_button(
            label="Descargar PDF",
            data=file,
            file_name=pdf_path,
            mime='application/pdf'
        )

# Pantalla de Inicio de Sesión y Navegación
if not st.session_state.logged_in:
    
    # Centrar la imagen y colocarla arriba del título "Iniciar Sesión"
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://fibotech.mx/images/dimex-logo.png" width="300">
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.title("Iniciar Sesión")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type='password')

    if st.button("Iniciar Sesión"):
        if login(email, password):
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Correo o contraseña incorrectos")
else:
    # Barra lateral para la navegación y selección de ID de solicitud
    st.sidebar.title("Navegación")
    opcion = st.sidebar.selectbox("Selecciona una opción", ["Listado de Usuarios", "Información de Solicitud", "Historial de Interacciones"])
    
    # Desplegador para seleccionar el ID de la solicitud
    solicitud_id = st.sidebar.selectbox("Selecciona el ID de la solicitud", ["Todos"] + list(df_mo['Solicitud_id'].unique()), key='solicitud_id')
    
    # Navegación según la opción seleccionada
    if opcion == "Listado de Usuarios":
        if solicitud_id != "Todos":
            df_mo = df_mo[df_mo['Solicitud_id'] == solicitud_id]  # Filtrar por ID si no es "Todos"
        mostrar_lista_usuarios()
    
    elif opcion == "Información de Solicitud" and solicitud_id != "Todos":
        mostrar_informacion_usuario(solicitud_id)
    
    elif opcion == "Historial de Interacciones" and solicitud_id != "Todos":
        mostrar_historial_interacciones(solicitud_id)