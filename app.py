import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def load_ratings():
    return pd.read_csv('data/movies_ratings.csv')

def load_runtime():
    return pd.read_csv('data/movies_duration.csv')

def load_actors():
    return pd.read_csv('data/actors_movies_year.csv')

def load_actors_series():
    return pd.read_csv('data/actors_series_year.csv')


data_runtime = load_runtime()
data_ratings = load_ratings()
data_actors = load_actors()
data_actors_series = load_actors_series()



def main():

    pages = {
        'Home': home,
        'Movie Duration': movie_duration,
        'Ratings': movie_ratings,
        'Actors': actors_ratings,
        'Age': actors_age,
        'Recommendations': recommendations}

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
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('[Guillaume Arp](https://github.com/GuillaumeArp)')
        st.image('assets/guillaume.png')
        
    with col2:
        st.markdown('[Franck Joly](https://github.com/JOLYfranck)')
        st.image('assets/franck.jpeg')
    
    ''    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('[Catherine Le Calve](https://github.com/CathieLC)')
        st.image('assets/cath.png')
        
    with col4:
        st.markdown('[Josse Preis](https://github.com/jossepreis)')
        st.image('assets/josse.png')
        

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

def actors_ratings():

    st.subheader('Most Active Actors')

    'We wanted here to know which actors appear in the most movies.' 'In order to do that, we first had to fetch data regarding actors or actresses only. We have decided then to limit the scope to movies released after 1920.'
    'The data has finally been divided by decades in order to get a better insight into who were the most productive actors of their times.'


    depart = 1920
    fin = 1929
    subplot = []
    for i in range(11):
        actors_movies_decade = data_actors.loc[(data_actors['startYear']>=depart)&(data_actors['startYear']<=fin)]
        temp = actors_movies_decade['primaryName'].value_counts()[:5].rename_axis('name').reset_index(name='count')
        subplot.append(temp)
        depart+=10
        fin+=10
    globa = data_actors['primaryName'].value_counts()[:5].rename_axis('name').reset_index(name='count')

    fig = make_subplots(
        rows=4, cols=3,
        subplot_titles=('1920-1929', '1930-1939','1940-1949','1950-1959','1960-1969','1970-1979','1980-1989','1990-1999','2000-2009','2010-2019','2020-2029','Overall Results'),
        )

    fig.append_trace(
        go.Bar(x=subplot[0]['name'],
        y=subplot[0]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=1
    )

    fig.append_trace(
        go.Bar(x=subplot[1]['name'],
        y=subplot[1]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=2
    )

    fig.append_trace(
        go.Bar(x=subplot[2]['name'],
        y=subplot[2]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=3
    )

    fig.append_trace(
        go.Bar(x=subplot[3]['name'],
        y=subplot[3]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=1
    )

    fig.append_trace(
        go.Bar(x=subplot[4]['name'],
        y=subplot[4]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=2
    )

    fig.append_trace(
        go.Bar(x=subplot[5]['name'],
        y=subplot[5]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=3
    )

    fig.append_trace(
        go.Bar(x=subplot[6]['name'],
        y=subplot[6]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=1
    )

    fig.append_trace(
        go.Bar(x=subplot[7]['name'],
        y=subplot[7]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=2
    )

    fig.append_trace(
        go.Bar(x=subplot[8]['name'],
        y=subplot[8]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=3
    )

    fig.append_trace(
        go.Bar(x=subplot[9]['name'],
        y=subplot[9]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=1
    )

    fig.append_trace(
        go.Bar(x=subplot[10]['name'],
        y=subplot[10]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=2
    )

    fig.append_trace(
        go.Bar(x=globa['name'],
        y=globa['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=3
    )

    fig.update_layout(template='plotly_dark', title='5 Most Active Actors in Movies per Decade' ,showlegend=False,height = 1250,width=1000)
    st.plotly_chart(fig, use_container_width=True)

    'There are some noticeable patterns here. We can notice first, looking at the overall results, we can see that the top 5 most productive actors are Asian, with one Japanese actor, one Korean, and the other 3 being Indians.'
    'This trend is verified when we look into the details of the different decades, which shows the fast production style of the Indian and Japanese movie industries.'
    'There are some caveats though to note. We tried to filter out the adult movies for our analysis (on all topics), but we can\'t help noticing that a good number of them are still there. If we look at the most productive actor in the 2000s, we find that Seiji Nakamitsu is specialized in adult movies (from what I could gather after a quick look at his bio). However, after looking at a sample of his movies in the database, it appears that they are not tagged properly as Adult, nor do they have the Adult category in the genres. This is one of the most important limitations of the database, the quality of the indexation of the non american or european movies is quite lackluster, which is to be expected coming from an american website. Although it aims at being comprehensive, there will always be a western bias that needs to be taken into account.'
    'Let\'s have a look now at the same graphs but with the series instead, to see if we can see some identical names or if the actors are different.'
    
    depart2 = 1920
    fin2 = 1929
    subplot2 = []
    for i in range(11):
        actors_series_decade = data_actors_series[(data_actors_series['startYear']>=depart2)&(data_actors_series['startYear']<=fin2)]
        temp = actors_series_decade['primaryName'].value_counts()[:5].rename_axis('name').reset_index(name='count')
        subplot2.append(temp)
        depart2+=10
        fin2+=10
    globa2 = data_actors_series['primaryName'].value_counts()[:5].rename_axis('name').reset_index(name='count')
    
    fig2 = make_subplots(
        rows=4, cols=3,
        subplot_titles=('1920-1929', '1930-1939','1940-1949','1950-1959','1960-1969','1970-1979','1980-1989','1990-1999','2000-2009','2010-2019','2020-2029','Overall Results'),
        )

    fig2.append_trace(
        go.Bar(x=subplot2[0]['name'],
        y=subplot2[0]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=1
    )

    fig2.append_trace(
        go.Bar(x=subplot2[1]['name'],
        y=subplot2[1]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=2
    )

    fig2.append_trace(
        go.Bar(x=subplot2[2]['name'],
        y=subplot2[2]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=1, col=3
    )

    fig2.append_trace(
        go.Bar(x=subplot2[3]['name'],
        y=subplot2[3]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=1
    )

    fig2.append_trace(
        go.Bar(x=subplot2[4]['name'],
        y=subplot2[4]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=2
    )

    fig2.append_trace(
        go.Bar(x=subplot2[5]['name'],
        y=subplot[5]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=2, col=3
    )

    fig2.append_trace(
        go.Bar(x=subplot2[6]['name'],
        y=subplot2[6]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=1
    )

    fig2.append_trace(
        go.Bar(x=subplot2[7]['name'],
        y=subplot2[7]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=2
    )

    fig2.append_trace(
        go.Bar(x=subplot2[8]['name'],
        y=subplot2[8]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=3, col=3
    )

    fig2.append_trace(
        go.Bar(x=subplot2[9]['name'],
        y=subplot[9]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=1
    )

    fig2.append_trace(
        go.Bar(x=subplot2[10]['name'],
        y=subplot2[10]['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=2
    )

    fig2.append_trace(
        go.Bar(x=globa2['name'],
        y=globa2['count'],
        marker_color=px.colors.qualitative.Plotly),
        row=4, col=3
    )

    fig2.update_layout(template='plotly_dark', title='5 Most Active Actors in Series per Decade', showlegend=False, height = 1250, width=1000)
    st.plotly_chart(fig2, use_container_width=True)
    
    'There is little to analyze here, we can at first see that Series started to take off, expectedly, after the World War 2 and the advent of the television. We can also note, again as expected, that no actor appears in the two graphs, and TV Series actors are usually specialized in this genre.'
    'There are some more faults in the database that this graph points out though. It looks like the 1970s telenovelas episodes were improperly categorized as tvSeries instead of episodes, which explains the inhuman productivity of the actors showing in this decade. This is another bias of the database, which makes it quite difficult to interpret results on a wold scale.'


def actors_age():
    
    st.subheader('Actors and Actresses\'s Age Evolution')
    
def recommendations():
    pass

if __name__ == "__main__":
    main()