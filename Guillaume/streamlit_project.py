import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go 

st.set_page_config(page_title='Movie Analysis', page_icon=':shark:')

st.title('Movie Analysis Project')

st.subheader('Movie Duration Evolution')

@st.cache
def load_basics():
    basics_df = pd.read_csv("https://datasets.imdbws.com/title.basics.tsv.gz", sep="\t", low_memory=False)
    basics_df = basics_df[basics_df['isAdult'] == '0']
    basics_df = basics_df[basics_df['titleType'] == 'movie']
    basics_df = basics_df.replace('\\N', pd.NaT)
    basics_df = basics_df[['startYear', 'runtimeMinutes']]
    basics_df.dropna(inplace=True)
    basics_df = basics_df.astype({'runtimeMinutes': int})
    basics_df = basics_df.astype({'startYear': int})
    basics_df = basics_df[(basics_df['runtimeMinutes'] >= 58) & (basics_df['runtimeMinutes'] <= 270)]
    basics_df = basics_df[(basics_df['startYear'] >= 1918) & (basics_df['startYear'] <= 2021)]
    basics_df = basics_df.groupby('startYear').mean()
    basics_df = round(basics_df['runtimeMinutes'], 2)
    return basics_df

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_basics()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

'We first wanted to analyze the evolution of the average duration of movies over the years.'
'We filtered the type to movies only, and removed the adult ones. Finally, the movies were grouped by their release year and the duration averaged for each year.'
'We decided to only take into account the movies released during or after 1918, due to the lack of consistent data before this time, and the more experimental nature of the film industry.'
'Finally, we removed the outliers regarding movie duration by setting the minimum duration to 58 minutes (the minimum to qualify as a feature film), and the maximum duration to 270 minutes.'

fig = px.line(
    data,
    y='runtimeMinutes',
    title='Average movie duration per year',
    line_shape='spline',
    labels={'startYear': 'Year', 'runtimeMinutes': 'Movie Duration in Minutes'},
    color_discrete_sequence=['green'],
    template='plotly_dark'
    )

st.plotly_chart(fig, use_container_width=True)

'We can notice here that the average movie duration has been steadily increasing until the early 60s, and then has been somewhat stable since then, around 95 minutes.'

