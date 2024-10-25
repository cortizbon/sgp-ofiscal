import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests
from io import BytesIO

DIC_COLORES = {'verde':["#009966"],
               'ro_am_na':["#FFE9C5", "#F7B261","#D8841C", "#dd722a","#C24C31", "#BC3B26"],
               'az_verd': ["#CBECEF", "#81D3CD", "#0FB7B3", "#009999"],
               'ax_viol': ["#D9D9ED", "#2F399B", "#1A1F63", "#262947"],
               'ofiscal': ["#F9F9F9", "#2635bf"]}
st.set_page_config(layout='wide')

@st.cache_data
def load_parquet_data(file_path):
    data = gpd.read_parquet(file_path)
    return data

@st.cache_data
def load_csv_data(file_path):
    data = pd.read_csv(file_path)
    return data

st.title("Sistema General de Participaciones")

cols = ['Educación',
       'Prestación Servicios', 'Calidad', 'Calidad (Gratuidad)',
       'Calidad (Matrícula)', 'Salud', 'Régimen Subsidiado', 'Salud Pública',
       'Subsidio a la Oferta', 'Agua Potable', 'Propósito General',
       'Libre Destinación', 'Deporte', 'Cultura', 'Libre Inversión', 'Fonpet',
       'Alimentación Escolar', 'Ribereños', 'Resguardos Indígenas',
       'Fonpet Asignaciones Especiales', 'Primera Infancia', 'Total']

cols_pc = [f"{i}_pc" for i in cols]
cols_pc_pop = [f"{i}_pop" for i in cols_pc]

df = load_csv_data('https://bucket-ofiscal.s3.us-east-1.amazonaws.com/datos_detalle3.csv')
df['CodigoDANEEntidad'] = [f"0{i}" if len(str(i)) == 4 else str(i) for i in df['CodigoDANEEntidad']]

tab1, tab2, tab3 = st.tabs(['General', 'Territorial', 'Mapa'])

with tab1:
    gen = load_csv_data('https://bucket-ofiscal.s3.us-east-1.amazonaws.com/detalle2.csv')
    gen['Valor_24'] /= 1_000_000_000
    piv = gen.groupby('Año')['Valor_24'].sum().reset_index()

    piv_conc = (gen
                        .groupby(['Año', 'Concepto'])['Valor_24']
                        .sum()
                        .reset_index())
    piv_conc['total'] = piv_conc.groupby(['Año'])['Valor_24'].transform('sum')

    piv_conc['%'] = ((piv_conc['Valor_24'] / piv_conc['total']) * 100).round(2)

    fig = make_subplots(rows=1, cols=2, x_title='Año',  )
        
    fig.add_trace(
            go.Line(
                x=piv['Año'], y=piv['Valor_24'], 
                name='Total', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )
    
    for i, group in piv_conc.groupby('Concepto'):
        fig.add_trace(go.Bar(
                x=group['Año'],
                y=group['%'],
                name=i
            ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


    st.plotly_chart(fig, key=1)

with tab2:
    deptos = gen['NombreDepartamento'].unique()
    depto = st.selectbox("Seleccione un departamento", deptos)
    fil = gen[gen['NombreDepartamento'] == depto]
    entidades = fil['NombreEntidad'].unique()
    entidad = st.selectbox("Seleccione una entidad territorial: ", entidades)
    fil = fil[fil['NombreEntidad'] == entidad]

    piv = fil.groupby('Año')['Valor_24'].sum().reset_index()

    piv_conc = (fil
                        .groupby(['Año', 'Concepto'])['Valor_24']
                        .sum()
                        .reset_index())
    piv_conc['total'] = piv_conc.groupby(['Año'])['Valor_24'].transform('sum')

    piv_conc['%'] = ((piv_conc['Valor_24'] / piv_conc['total']) * 100).round(2)

    fig = make_subplots(rows=1, cols=2, x_title='Año',  )
        
    fig.add_trace(
            go.Line(
                x=piv['Año'], y=piv['Valor_24'], 
                name='Total', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )
    
    for i, group in piv_conc.groupby('Concepto'):
        fig.add_trace(go.Bar(
                x=group['Año'],
                y=group['%'],
                name=i
            ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


    st.plotly_chart(fig, key=3)

    # CAGR territorial vs. CAGR nacional



with tab3: 

    url = "https://bucket-ofiscal.s3.us-east-1.amazonaws.com/muns.parquet"

    # Download the parquet file from the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the download was successful

    # Load the file into a pandas DataFrame
    file_data = BytesIO(response.content)

    years = df['Año'].unique()
    gdf = load_parquet_data(file_data)
    year = st.select_slider("Seleccione un año: ", years)

    filtro = df[df['Año'] == year]
    depto = st.selectbox("Seleccione un departamento: ", deptos)

    filtro = filtro[filtro['NombreDepartamento'] == depto]

    

    col = st.selectbox("Seleccione una variable", cols_pc_pop)

    columns = ['CodigoDANEEntidad', 'NombreEntidad'] + [col] + [col.split('_')[0]] + ['Total']
    filtro = filtro[columns]
    filtro['%'] = filtro[col.split('_')[0]] / filtro['Total']

    merge = filtro.merge(gdf[['mpio_cdpmp', 'geometry']], left_on='CodigoDANEEntidad', right_on='mpio_cdpmp').reset_index(drop=True)
    
    fil = gpd.GeoDataFrame(merge[['NombreEntidad', col, '%', 'geometry']])

    fig, axes = plt.subplots(1, 2, figsize=(6,6))

    fil.plot(column=col, 
             ax=axes[0], 
             cmap='viridis', 
             legend=True, legend_kwds={"label": col, 
                                       "orientation": "horizontal",
                                       "pad":0.01})
    fil.plot(column='%',
              ax=axes[1], 
              cmap='viridis', 
              legend=True, legend_kwds={"label": "%", 
                                        "orientation": "horizontal",
                                        "pad": 0.01})
    axes[0].set_axis_off()
    axes[1].set_axis_off()
    st.pyplot(fig)

    # Filtrar por departamento
    # Las variables expresarlas en términos percápita pero también en términos de porcentaje