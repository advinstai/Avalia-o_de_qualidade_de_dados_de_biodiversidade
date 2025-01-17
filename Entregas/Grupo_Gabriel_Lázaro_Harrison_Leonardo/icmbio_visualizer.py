from package import icmbio_search as bio

import streamlit as st

import pandas as pd
import numpy as np 
import math


####################################################################################
#
# Initializing STREAMLIT APP


st.title("ICMBio Visualizer")
st.sidebar.header("Settings")

key = '09aadb1b1d8840acacfa0fcece0acb13'
key = st.sidebar.text_input("Product key", key)

FILES = ["PortalBio 00002.csv",
        "PortalBio 00043.csv",
        "PortalBio 00555.csv",
        "PortalBio 03912.csv",
        "PortalBio 58411.csv"]
url = "Arquivos_csv/" + st.sidebar.selectbox("Select a file", FILES)
st.write("Reading file %s" % url)

TAXONOMY_COLUMNS = ['Filo', 'Classe', 'Ordem', 'Familia', 'Genero', 'Especie']
TAXONOMY_COLUMNS = st.sidebar.multiselect("Taxonomy columns to analyse", TAXONOMY_COLUMNS, TAXONOMY_COLUMNS)

LOCATION_COLUMNS = ['Pais', 'Estado/Provincia', 'Municipio', 'Latitude', 'Longitude']
LOCATION_COLUMNS = st.sidebar.multiselect("Location columns to analyse", LOCATION_COLUMNS, LOCATION_COLUMNS)

LOCATION_SAMPLING = st.sidebar.slider("Number of samples to plot", 1, 20, 2)

# class initializer
biodiversity = bio.getBiodiversity(url, key, TAXONOMY_COLUMNS, LOCATION_COLUMNS)
#if st.checkbox("Show raw data (%d rows x %d columns)" % (biodiversity.df_data.shape[0],biodiversity.df_data.shape[1])):
#    st.dataframe(biodiversity.df_data)

# missing data analysis
biodiversity.checkEmpty()
if st.checkbox("Show missing data statistics (% of data missing)"):
    st.dataframe(biodiversity.df_dataNAN)

# run taxonomic analysis
biodiversity.getTaxonomy(col_name='Nível Taxonômico')
if st.checkbox("Show taxonomic data (%d rows x %d columns)" % (biodiversity.df_taxonomy.shape[0],biodiversity.df_taxonomy.shape[1])):
    st.dataframe(biodiversity.df_taxonomy)

# filtering data to show
FILTER_FIELDS = st.sidebar.multiselect("Please select one or more columns to filter by", list(biodiversity.df_data.columns))
FILTER_VALUES = [st.sidebar.multiselect("Filter values for column %s"%column, biodiversity.df_data[column].unique()) for column in FILTER_FIELDS]
biodiversity.filterFields(FILTER_FIELDS, FILTER_VALUES)
biodiversity.getTaxonomy(col_name='Nível Taxonômico')
if st.checkbox("Show filtered data (%d rows x %d columns)" % (biodiversity.df_filtered.shape[0],biodiversity.df_filtered.shape[1])):
    st.dataframe(biodiversity.df_filtered)

# check if latitude and longitude are correct or not
biodiversity.checkCoordinates(LOCATION_SAMPLING)
biodiversity.df_location_sample = biodiversity.df_location_sample.rename(columns={'AdjustedLatitude': 'lat', 'AdjustedLongitude': 'lon'})
if st.checkbox("Show locations sample data (%d rows x %d columns)" % (biodiversity.df_location_sample.shape[0],biodiversity.df_location_sample.shape[1])):
    st.dataframe(biodiversity.df_location_sample[["lat", "lon", "Municipio", "ReversedAddress"]])

# show map with sampled observations
try:
    rangelat = math.log2(170 / (biodiversity.df_location_sample['lat'].max()-biodiversity.df_location_sample['lat'].min()))
    rangelon = math.log2(360 / (biodiversity.df_location_sample['lon'].max()-biodiversity.df_location_sample['lon'].min()))
    zoom = int(min(rangelat, rangelon)) + 1
except:
    zoom = 10
st.deck_gl_chart(
    viewport={
        'latitude': biodiversity.df_location_sample['lat'].mean(),
        'longitude': biodiversity.df_location_sample['lon'].mean(),
        'zoom': zoom,
        'pitch': 0,
        'bearing': 0,
    },
    layers=[
        {
        'type': 'ScatterplotLayer', #'HexagonLayer', GridLayer, LineLayer, PointCloudLayer, TextLayer, ScreenGridLayer
        'data': biodiversity.df_location_sample[biodiversity.df_location_sample['Confidence']<=1],
        'getRadius': 1000, #'Radius', # inform a column name with values [0-100]
        'getColor': [0, 120, 0], 
        #'getColor': 'Color',
        'getLineColor': [220, 220, 220],
        'opacity': 1.0,
        'pickable': True,
        'autoHighlight': True,
        'stroked': True,
        'filled': True,
        'radiusScale': 1,
        'radiusMinPixels': 10, 
        'radiusMaxPixels': 100,
        'lineWidthMinPixels': 2,
        #'onHover': 'find documentation on how to implement this
        },
        {
        'type': 'ScatterplotLayer', #'HexagonLayer', GridLayer, LineLayer, PointCloudLayer, TextLayer, ScreenGridLayer
        'data': biodiversity.df_location_sample[biodiversity.df_location_sample['Confidence']>1],
        'getRadius': 1000, #'Radius', # inform a column name with values [0-100]
        'getColor': [120, 0, 0], 
        #'getColor': 'Color',
        'getLineColor': [220, 220, 220],
        'opacity': 1.0,
        'pickable': True,
        'autoHighlight': True,
        'stroked': True,
        'filled': True,
        'radiusScale': 1,
        'radiusMinPixels': 10,
        'radiusMaxPixels': 100,
        'lineWidthMinPixels': 2,
        #'onHover': 'find documentation on how to implement this
        }
        ])

