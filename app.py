import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


st.title("Datos")

cols = ['Educación',
       'Prestación Servicios', 'Calidad', 'Calidad (Gratuidad)',
       'Calidad (Matrícula)', 'Salud', 'Régimen Subsidiado', 'Salud Pública',
       'Subsidio a la Oferta', 'Agua Potable', 'Propósito General',
       'Libre Destinación', 'Deporte', 'Cultura', 'Libre Inversión', 'Fonpet',
       'Alimentación Escolar', 'Ribereños', 'Resguardos Indígenas',
       'Fonpet Asignaciones Especiales', 'Primera Infancia', 'Total']
df = pd.read_csv('datasets/datos_detalle.csv')
years = df['Año'].unique()
gdf = gpd.read_file('bucket-ofiscal.s3.us-east-1.amazonaws.com/MGN_ADM_MPIO_GRAFICO.shp')
year = st.select_slider("Seleccione un año: ", years)

filtro = df[df['Año'] == year]

merge = filtro.merge(gdf[['mpio_cdpmp', 'geometry']], left_on='CodigoDANEEntidad', right_on='mpio_cdpmp').reset_index(drop=True)

col = st.selectbox("Seleccione una variable", cols)


fil = gpd.GeoDataFrame(merge)[[col, 'geometry']]


fig, ax = plt.subplots(1, 1)

fil.plot(ax=ax, cmap='viridis', legend=True)
ax.set_axis_off()

st.pyplot(fig)



# Seleccionar el año

# Seleccionar la cuenta
# Seleccionar el departamento
# Seleccionar