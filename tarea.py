import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl

# Carga de datos desde el archivo 'vendedores.xlsx'
df = pd.read_excel("vendedores.xlsx")  # Carga del archivo

# Título de la aplicación
st.title("Dashboard de Ventas de Vendedores")

# Contenedor para filtro de región
with st.container():
    st.header("Filtrado por Región")
    # Obtener las regiones únicas
    regiones = df["REGION"].unique()
    # Selectbox para elegir la región
    region_seleccionada = st.selectbox("Selecciona una Región:", options=["Todas"] + list(regiones))

    # Filtrar datos por la región seleccionada
    if region_seleccionada != "Todas":
        df_filtrado = df[df["REGION"] == region_seleccionada]
    else:
        df_filtrado = df

    # Mostrar tabla filtrada
    st.subheader("Tabla de Datos")
    st.dataframe(df_filtrado)

# Contenedor para gráficos de métricas
with st.container():
    st.header("Gráficas de Métricas de Ventas")

    # Gráfico de Unidades Vendidas por vendedor
    fig1, ax1 = plt.subplots()
    df_filtrado.groupby("APELLIDO")["UNIDADES VENDIDAS"].sum().plot(kind="bar", ax=ax1)
    ax1.set_title("Unidades Vendidas por Vendedor")
    ax1.set_ylabel("UNIDADES VENDIDAS")
    st.pyplot(fig1)

    # Gráfico de Ventas Totales
    fig2, ax2 = plt.subplots()
    df_filtrado.groupby("APELLIDO")["VENTAS TOTALES"].sum().plot(kind="bar", ax=ax2)
    ax2.set_title("Ventas Totales por Vendedor x:")
    ax2.set_ylabel("VENTAS TOTALES")
    st.pyplot(fig2)

    # Gráfico de Porcentaje de Ventas
    fig3, ax3 = plt.subplots()
    ventas_totales = df_filtrado["VENTAS TOTALES"].sum()
    # Calcular el porcentaje de ventas para cada vendedor
    df_filtrado.groupby("APELLIDO")["VENTAS TOTALES"].sum().apply(lambda x: x / ventas_totales * 100).plot(kind="bar", ax=ax3)
    ax3.set_title("Porcentaje de Ventas por Vendedor")
    ax3.set_ylabel("Porcentaje de Ventas (%):")
    st.pyplot(fig3)

# Contenedor para búsqueda de un apellido específico
with st.container():
    st.header("Buscar Información de Vendedor Específico.")

    # Selección de apellidoa
    vendedores = df["APELLIDO"].unique()
    vendedor_seleccionado = st.selectbox("Selecciona un Vendedor:", vendedores)

    # Mostrar datos del vendedor seleccionado
    datos_vendedor = df[df["APELLIDO"] == vendedor_seleccionado]
    st.subheader(f"Datos de {vendedor_seleccionado}")
    st.write(datos_vendedor)
