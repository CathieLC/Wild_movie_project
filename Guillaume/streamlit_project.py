import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go 

st.set_page_config(page_title='Movie Analysis', page_icon=':cat:')

def _max_width_():
    max_width_str = "max-width: 1300px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

_max_width_()

st.title('Movie Analysis Project')

# add_selectbox = st.sidebar.selectbox(
#     "Select a KPI (test, does nothing yet)",
#     ("Movie Duration", "Ratings")
# )

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

@st.cache
def load_ratings():
    ratings_df = pd.read_csv("https://datasets.imdbws.com/title.ratings.tsv.gz", sep="\t")
    basics_df = pd.read_csv("https://datasets.imdbws.com/title.basics.tsv.gz", sep="\t", low_memory=False)
    basics_df = basics_df[basics_df['isAdult'] == '0']
    basics_df = basics_df[basics_df['titleType'] == 'movie']
    basics_df = basics_df[['tconst', 'primaryTitle', 'startYear', 'genres']]
    movies_ratings = pd.merge(basics_df, ratings_df, how='inner', left_on='tconst', right_on='tconst')
    movies_ratings.reset_index(drop=True, inplace=True)
    movies_ratings = movies_ratings[movies_ratings['averageRating'] >= 8.4]
    movies_ratings = movies_ratings[movies_ratings['numVotes'] >= 20000]
    movies_ratings[['mainGenre', 'secondaryGenres']] = movies_ratings['genres'].str.split(',', n=1, expand=True)
    return movies_ratings


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data_runtime = load_basics()
data_ratings = load_ratings()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')



def main():

    pages = {
        'Home': home,
        'Movie Duration': movie_duration,
        'Ratings': movie_ratings}

    if "page" not in st.session_state:
        st.session_state.update({
        # Default page
        'page': 'Home'
        })

    with st.sidebar:
        page = st.selectbox("Choose a page", tuple(pages.keys()))

    pages[page]()


def home():

    st.subheader('About this project')

    'The purpose of this project is to help a new movie theatre owner to get a better idea what the film industry looks like at the moment, and how it has evolved over the years.'
    'Then, we will provide a recommendation algorithm to help him select the best movies to play at the theatre, based on the tastes of his audience.'
    ''
    'This app is brought to you by the awesome Wild Data Green Team 1 (yes we need a better name):'
    '   - Guillaume Arp'
    '   - Franck Joly'
    '   - Catherine Le Calve'
    '   - Josse Preis'

def movie_duration():
    
    st.subheader('Movie Duration Evolution')

    'We first wanted to analyze the evolution of the average duration of movies over the years.'
    'We filtered the type to movies only, and removed the adult ones. Finally, the movies were grouped by their release year and the duration averaged for each year.'
    'We decided to only take into account the movies released during or after 1918, due to the lack of consistent data before this time, and the more experimental nature of the film industry.'
    'Finally, we removed the outliers regarding movie duration by setting the minimum duration to 58 minutes (the minimum to qualify as a feature film), and the maximum duration to 270 minutes.'

    fig = px.line(
        data_runtime,
        y='runtimeMinutes',
        title='Average movie duration per year',
        line_shape='spline',
        labels={'startYear': 'Year', 'runtimeMinutes': 'Movie Duration in Minutes'},
        color_discrete_sequence=['green'],
        template='plotly_dark'
        )

    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    'We can notice here that the average movie duration has been steadily increasing until the early 60s, and then has been somewhat stable since then, around 95 minutes.'

def movie_ratings():

    st.subheader('Top Rated Movies')

    'Another point we wanted to look into regarded the best rated movies in the database.'
    'We filtered the movies to only include movies with an average rating of 8.4 or higher, and a minimum number of votes of 20000. That leaves us with a list of 109 movies, split by genre. When multiple genres were specified in the movie description, we only kept the first one, which is considered to be the main genre of the movie.'
    'The filter of 20000 votes is there to make sure that the selected movies are indeed considered to be very good by a large and diverse audience.'
    'First we can use a 3D Scatter Plot to see which movies are best rated, by year, genre and number of votes.'

    fig = px.scatter_3d(data_ratings,
        x='startYear',
        y='averageRating',
        z='mainGenre',
        color='averageRating',
        size='numVotes',
        opacity = 0.8,
        labels={
            'startYear': 'Year',
            'averageRating': 'Rating',
            'mainGenre': 'Genre',
            'numVotes': 'Number of Votes'
        },
        size_max=25,
        template='plotly_dark',
        hover_name='primaryTitle'
    )

    fig.update_layout(height=800, scene=dict(zaxis=dict(nticks=11)), title='IMDB Top Rated Movies (>= 8.4) per Genre, Number of Votes and Year')
    st.plotly_chart(fig, use_container_width=True)

    'The mouseover shows the title of the movie, and the size of the bubble represents the number of votes. That way, it is easier to have a clear view of which movies are best rated, and by how many people.'
    "Let's have a look now at a histogram showing more specifically how many movies in that list belong to each genre."

    fig = px.histogram(data_frame=data_ratings, x='mainGenre', color='mainGenre', labels={'mainGenre': 'Genre'}, color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_layout(height=600, title='IMDB Top Rated Movies (>= 8.4) Genre Distribution', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    'As we can notice here, almost half of all the movies in the list are dramas or action movies.'

if __name__ == "__main__":
    main()