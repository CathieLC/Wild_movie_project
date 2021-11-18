import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import math
from collections import Counter
import operator

st.set_page_config(page_title='Movie Analysis', page_icon=':movie_camera:')

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

@st.cache
def load_ratings():
    return pd.read_csv('data/movies_ratings.csv.zip')

@st.cache
def load_runtime():
    return pd.read_csv('data/movies_duration.csv.zip')

@st.cache
def load_actors():
    return pd.read_csv('data/actors_movies_year.csv.zip')

@st.cache
def load_actors_series():
    return pd.read_csv('data/actors_series_year.csv.zip')

@st.cache
def load_actors_age():
    return pd.read_csv('data/actors_age.csv.zip')

@st.cache
def load_movies():
    return pd.read_csv('data/movies_merged.csv.zip')


data_runtime = load_runtime()
data_ratings = load_ratings()
data_actors = load_actors()
data_actors_series = load_actors_series()
data_age = load_actors_age()
data_movies = load_movies()

# Cosine Algorithm Class
class CosineSimilarity:
    def __init__(self):
        print("Cosine Similarity initialized")

    @staticmethod
    def cosine_similarity_of(text1, text2):
        # Get words first
        first = re.compile(r"[\w']+").findall(text1)
        second = re.compile(r"[\w']+").findall(text2)

        # Get dictionary with each word and count
        vector1 = Counter(first)
        vector2 = Counter(second)

        # Convert vectors to set to find common words as intersection
        common = set(vector1.keys()).intersection(set(vector2.keys()))

        dot_product = 0.0

        for i in common:
            # Get amount of each common word for both vectors and multiply them then add them together
            dot_product += vector1[i] * vector2[i]

        squared_sum_vector1 = 0.0
        squared_sum_vector2 = 0.0

        # Get squared sum values of word counts from each vector
        for i in vector1.keys():
            squared_sum_vector1 += vector1[i]**2

        for i in vector2.keys():
            squared_sum_vector2 += vector2[i]**2

        #calculate magnitude with squared sums.
        magnitude = math.sqrt(squared_sum_vector1) * math.sqrt(squared_sum_vector2)

        if not magnitude:
           return 0.0
        else:
           return float(dot_product) / magnitude
       

# Recommendations Engine Class
class RecommenderEngine:
    def __init__(self):
        print("engine initialized")

    def get_recommendations(keywords):

        df = data_movies
        df.reset_index(inplace=True, drop=True)        

        score_dict = {}
        
        # Obtaining the score by the cosine similarity method
        for index, row in df.iterrows():
            score_dict[index] = CosineSimilarity.cosine_similarity_of(row['data'], keywords)

        # Sort movies by score and index
        sorted_scores = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)

        counter = 0

        # Create an empty results data frame
        resultDF = pd.DataFrame(columns=('tconst', 'originalTitle', 'data', 'score'))

        # Get highest scored 10 movies.
        for i in sorted_scores:

            resultDF = resultDF.append({'tconst': df.iloc[i[0]]['tconst'], 'originalTitle': df.iloc[i[0]]['originalTitle'], 'data': df.iloc[i[0]]['data'], 'score': i[1]}, ignore_index=True)
            counter += 1

            if counter>10:
                break

        # remove the first row
        return resultDF.iloc[1:]
    

def get_recommendations(keywords):
    return RecommenderEngine.get_recommendations(keywords)


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
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Average'],
    line_shape='spline',
    line_color='green',
    name='Average'
    ))

    fig.update_layout(
            width=1300,
            height=600,
            template='plotly_dark',
            title='Average Movie Duration per Year',
            xaxis_title='Year',
            yaxis_title='Duration in Minutes'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    'We can notice here that the average movie duration has been steadily increasing until the early 60s, and then has been somewhat stable since then, around 95 minutes.'
    'The average duration increased with the quality of the projectors and the films reels themselves, allowing a safer use of multiple reels.'
    'It would also seem that there is a common acceptance that a movie should last for about one hour and half, and that has been the norm in the post-war era.'
    'Now let\'s have a deeper look at the duration per genre this time, using a sample of the 5 most common genres in the database, which are Comedy, Drama, Adventure, Action and Crime. It should be noted that about 25 different genres are present in the database, and we will only look at the most common ones here.'

    fig = go.Figure()

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Average'],
    line_shape='spline',
    line_color='green',
    line_width=8,
    opacity=0.9,
    name='Average'
    ))

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Comedy'],
    line_shape='spline',
    line_color='beige',
    line_width=1,
    opacity=0.8,
    name='Comedy'
    ))

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Drama'],
    line_shape='spline',
    line_color='blueviolet',
    line_width=1,
    opacity=0.8,
    name='Drama'
    ))

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Adventure'],
    line_shape='spline',
    line_color='coral',
    line_width=1,
    opacity=0.8,
    name='Adventure'
    ))

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Action'],
    line_shape='spline',
    line_color='royalblue',
    line_width=1,
    opacity=0.8,
    name='Action'
    ))

    fig.add_trace(go.Scatter(
    x=data_runtime['startYear'],
    y=data_runtime['Crime'],
    line_shape='spline',
    line_color='red',
    line_width=1,
    opacity=0.8,
    name='Crime'
    ))

    fig.update_layout(
        width=1300,
        height=600,
        template='plotly_dark',
        title='Average Movie Duration per Year and per Genres',
        legend_title='Genre',
        xaxis_title='Year',
        yaxis_title='Duration in Minutes'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    'As we can see, the genre can have a noticeable influence on the average duration. Action movies especially tend to last quite a bit longer, and this has been going on since the 90s, with a peak at nearly 2 hours on average. On the other side, comedies and adventure movies, usually aimed at a younger and familial audience, tend to be shorter or close to the average.'
    'There are some oddities as well, the most noticeable one is the apparent drop in movie length between 2008 and 2016 (give or take), that affects all the genres at the same time, and on the same scale. A deeper dive into the history of the film industry is necessary here to provide a proper explanation.'



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

    fig.update_layout(
        height=800,
        scene=dict(zaxis=dict(nticks=11)),
        title='IMDB Top Rated Movies (>= 8.4) per Genre, Number of Votes and Year'
    )
    
    st.plotly_chart(fig, use_container_width=True)

    'The mouseover shows the title of the movie, and the size of the bubble represents the number of votes. That way, it is easier to have a clear view of which movies are best rated, and by how many people.'
    "Let's have a look now at a histogram showing more specifically how many movies in that list belong to each genre."

    fig = px.histogram(data_frame=data_ratings, x='mainGenre', color='mainGenre', labels={'mainGenre': 'Genre'}, color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_layout(height=600, title='IMDB Top Rated Movies (>= 8.4) Genre Distribution', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    'As we can notice here, almost half of all the movies in the list are dramas or action movies. We should keep in mind that those genres are pretty generic and tend to be the default ones when trying to define a movie. The scatter plot for example shows us two very close points in the Drama category, Forrest Gump and Fight Club, in terms of rating and number of votes, but anyone having seen both will tell that those movies are extremely different. This is another bias of the data, and even though there are secondary genres (that we couldn\'t take into account here to limit the number of dimensions), it is still an arbitrary classification made by human beings, who will always have a tendency, when faced to a difficult choice, to go towards the comfortable and easy one. Both Drama and Action categories are way too broad to be efficient, we could guess that any movie with some fighting at one point can be tagged as Action, and regarding Drama, we should also remember that the word comes from the ancient greek δράμα that litteraly means "theatre play", and did not mean anything related to a genre.'
    'We should therefore always keep in mind that this data is populated by humans, and that categories are always somewhat subjective. Still, it is interesting to have a look at the 3D scatter and pointing the mouse to the bigger points to look at the name of the movie, and wonder if you agree with that rating and if you do yourself consider those films as classics indeed.'
    

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

    fig.update_layout(
        template='plotly_dark',
        title='5 Most Active Actors in Movies per Decade',
        showlegend=False,
        height = 1250,
        width=1300
    )
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

    fig2.update_layout(
        template='plotly_dark',
        title='5 Most Active Actors in Series per Decade',
        showlegend=False,
        height = 1250,
        width=1300
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    'There is little to analyze here, we can at first see that Series started to take off, expectedly, after the World War 2 and the advent of the television. We can also note, again as expected, that no actor appears in the two graphs, and TV Series actors are usually specialized in this genre.'
    'There are some more faults in the database that this graph points out though. It looks like the 1970s telenovelas episodes were improperly categorized as tvSeries instead of episodes, which explains the inhuman productivity of the actors showing in this decade. This is another bias of the database, which makes it quite difficult to interpret results on a world scale.'


def actors_age():
    
    st.subheader('Actors and Actresses\'s Mean Age Evolution Over the Years')
    
    'Here our goal was to find out how the average age of the cast evolved over the years, and see if there is a difference between genders on this regard.'
    'To do this, we gathered data regarding the age of all the credited cast at the time of the movie release, and and averaged them by year. We also split that data between genders, based on if the person was credited as an actor or an actress.'
    'The filters were the same as for the movies duration, meanning that we kept only movies released between 1918 and 2021, and with a duration between 58 and 270 minutes.'
    
    fig = go.Figure() 

    fig.add_trace(go.Scatter(x=data_age.startYear, 
                        y=data_age.mean_age_actors_actress, 
                        name="Both Genders",
                        line_shape='spline',
                        line_color='green'))

    fig.add_trace(go.Scatter(x=data_age.startYear, 
                        y=data_age.mean_age_actress,
                        name="Actress",
                        line_shape='spline',
                        line_color='rgb(231,107,243)'))

    fig.add_trace(go.Scatter(x=data_age.startYear, 
                        y=data_age.mean_age_actors,
                        name="Actors",
                        line_shape='spline',
                        line_color='blue'))

    fig.update_layout(title ='Mean Age of Actors and Actresses',
                        width=1300,
                        height=600,
                        legend_title="Gender",
                        template='plotly_dark'
                        )

    st.plotly_chart(fig, use_container_width=True)
    
    'There are several trends that can be noticed here. The most obvious one is that on average, the average age of the cast is steadily increasing over the years. There is also a difference based on gender, actresses being most of the time younger than their male counterparts. We could make conjectures about the reasons why, a possible reason is the weight of patriarchy and sexism before the 80s that could have, more often than not, limited the actresses to supporting roles where youth and beauty were important to help the main actor shine. As the casting in movies tend to be more diverse, that age factor is getting less and less important.'
    'It should also be noted that this data, even though it aims at being as comprehensive as possible, is still partial, and will mostly show the main cast of a movie. As actors and actresses remain active longer and longer, younger people who are just starting or trying to break through have very small roles that may not be credited here, leading to a bias showing the average age of the cast being older than it probably is.'
    'It should therefore not be considered as an absolute truth, but as a trends indicator only. Those trends being that the age difference between genders is shrinking, to the point of being nearly non existent nowadays, and that actors and actresses tend to work longer, in many cases way past the usual retirement age. A good recent example of that phenomenon is Clint Eastwood, who is just releasing a movie this week, that he directed himself and in which he plays the main actor, at the ripe age of 91.'
    
def recommendations():
    
    st.subheader("Movie Recommendations")
    
    'Finally we have built a recommendations engine that will provide a list of 10 movies based on one that you can select here. Please note that only movies rated 6.0 or more on the IMDb are present in the list.'
    'The dropdown menu will show as the default choice the movie A.I. Artificial Intelligence, as a tribute to this area we are barely touching here.'
    
    movie_title = st.selectbox('Select a movie to get recommendations for:', data_movies.originalTitle, index=10243)
    
    movie_data = data_movies.loc[data_movies['originalTitle']==movie_title,'data'].values[0]
    recommendations = get_recommendations(movie_data)
    
    'Here are the results!'
    'Click on the movies to open its page on the IMDb'
    
    url_base = 'https://www.imdb.com/title/'
    
    for i in range(10):
        movie_name = recommendations.iloc[i]['originalTitle']
        movie_id = recommendations.iloc[i]['tconst']
        st.markdown(f"""
                    [{movie_name}]({url_base}{movie_id})
                    """)
        

if __name__ == "__main__":
    main()