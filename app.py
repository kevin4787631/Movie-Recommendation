import streamlit as st
import pickle
import pandas as pd
import requests
from datetime import datetime
import sqlite3
from streamlit_option_menu import option_menu
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ps = PorterStemmer()

if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

if "first_button_clicked" not in st.session_state:
    st.session_state.first_button_clicked = False

if "second_button_clicked" not in st.session_state:
    st.session_state.second_button_clicked = False

if "count" not in st.session_state:
    st.session_state.count = 0


def callback():
    st.session_state.button_clicked = True


def callback2():
    st.session_state.first_button_clicked = True


def callback3():
    st.session_state.second_button_clicked = True


connection = sqlite3.connect('user_data.db')
c = connection.cursor()


def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS user_table(username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS admin_table(username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS movies(id INT, title TEXT, genres TEXT, homepage TEXT, vote_average FLOAT, '
              'vote_count INT, crew TEXT, release_date TEXT, runtime INT, tags TEXT)')


def drop_table():
    c.execute('DROP TABLE movies')
    connection.commit()


def add_data(username, password):
    c.execute('INSERT INTO user_table(username, password) VALUES(?, ?)', (username, password))
    connection.commit()


def add_movie_data(movie_id, title, genres, homepage, vote_average, vote_count, crew, release_date, runtime, tags):
    c.execute('INSERT INTO movies(id, title, genres, homepage, vote_average, vote_count, crew, release_date, runtime, '
              'tags) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (int(movie_id), title, genres, homepage, vote_average,
                                                             int(vote_count), crew, release_date, runtime, tags))
    connection.commit()


def login_user(username, password):
    c.execute('SELECT * FROM user_table WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def login_admin(username, password):
    c.execute('SELECT * FROM admin_table WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def view_all():
    c.execute('SELECT * FROM movies')
    data = c.fetchall()
    return data


def main():
    create_table()
    # movie_dict2 = pickle.load(open('movies_dict2.pkl', 'rb'))
    # movie_dict2 = pd.DataFrame(movie_dict2)
    # for i in range(len(movie_dict2['title'])):
    #    movie_id = movie_dict2['id'][i]
    #    title = movie_dict2['title'][i]
    #    homepage = movie_dict2['homepage'][i]
    #    runtime = movie_dict2['runtime'][i]
    #    vote_average = movie_dict2['vote_average'][i]
    #   vote_count = movie_dict2['vote_count'][i]
    #    crew = movie_dict2['crew'][i]
    #    genres = movie_dict2['genres'][i]
    #    release_date = movie_dict2['release_date'][i]
    #    tags = movie_dict2['tags'][i]
    #    add_movie_data(movie_id, title, genres, homepage, vote_average, vote_count, crew, release_date, runtime, tags)

    # st.write(view_all())
    placeholder = st.empty()
    placeholder.title("Welcome to the website!")
    st.sidebar.title("Login or Sign Up")
    choice = st.sidebar.selectbox("Menu", ['Admin', 'Login', 'Sign Up'])

    if choice == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.button("Login", on_click=callback2) or st.session_state.first_button_clicked:
            create_table()
            result = login_user(username, password)
            if result:
                placeholder.empty()
                selected = option_menu(
                    menu_title=None,
                    options=["Home", "Search"],
                    orientation="horizontal",
                )
                if selected == "Home":
                    main_page()
                elif selected == "Search":
                    search_by()
            elif username == "" or password == "":
                st.header("No blank input allowed")
            else:
                st.header("You have inputted wrong credentials!")

    elif choice == "Sign Up":
        new_username = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("password", type='password')
        if st.sidebar.button("Sign Up"):
            if new_username != "" and new_password != "":
                create_table()
                add_data(new_username, new_password)
                st.success("You have created a valid account")
            else:
                st.header("No blank input allowed")

    elif choice == "Admin":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')

        if st.sidebar.button("Login", on_click=callback2) or st.session_state.first_button_clicked:
            create_table()
            result = login_admin(username, password)
            if result or st.session_state.second_button_clicked:
                placeholder.empty()
                movie_id = st.text_input("ID")
                title = st.text_input("Title")

                genres = st.text_input("Genre")
                genres = genres.split(",")
                genres = str(genres)

                homepage = st.text_input("Homepage")
                vote_average = st.text_input("Vote Average")
                vote_count = st.text_input("Vote Count")
                crew = st.text_input("Director")
                release_date = st.text_input("Release Date")
                runtime = st.text_input("Runtime")

                tags = st.text_input("Tags")
                tags = tags.split()
                tags = " ".join(tags)

                if st.button("Submit", on_click=callback3) or st.session_state.second_button_clicked:
                    add_movie_data(movie_id, title, genres, homepage, vote_average, vote_count, crew, release_date,
                                   runtime, tags)
                    train_model()

            elif username == "" or password == "":
                st.header("No blank input allowed")
            else:
                st.header("You have inputted wrong credentials!")


def search_by():
    choice = st.selectbox("Search By:", ['Genre', 'Popularity', 'Director'])
    movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movie_dict = pd.DataFrame(movie_dict)

    temp2 = ""
    temp3 = []
    for i in movie_dict['genres']:
        temp2 = eval(i)
        temp3.append(temp2)
    movie_dict['genres'] = temp3

    def get_image(movie_id):
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(
                movie_id))
        data = response.json()
        try:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        except:
            return "https://canterburypress.hymnsam.co.uk/images/products/large/noimage.png?width=400"

    def get_movies_by_genre(genre):
        movies = []
        movie_posters = []
        movie_links = []
        vote_avg = []
        runtime = []
        release_date = []

        num_of_movies = 0
        count = 0

        for i in movie_dict['genres']:
            if genre in i and num_of_movies < 200:
                movie_id = movie_dict['id'][count]
                movies.append(movie_dict['title'][count])
                movie_posters.append(get_image(movie_id))
                movie_links.append(movie_dict['homepage'][count])
                vote_avg.append(movie_dict['vote_average'][count])
                runtime.append(movie_dict['runtime'][count])
                release_date.append(movie_dict['release_date'][count])
                count += 1
                num_of_movies += 1
            else:
                count += 1
        return movies, movie_posters, movie_links, vote_avg, runtime, release_date

    def get_movies_by_vote():
        vote_average = movie_dict['vote_average']
        vote_count = movie_dict['vote_count']

        movies = []
        movie_posters = []
        movie_links = []
        vote_avg = []
        runtime = []
        release_date = []

        num_of_movies = 0

        for i in range(len(movie_dict['genres'])):
            if vote_average[i] > 7 and vote_count[i] > 2500 and num_of_movies < 200:
                movie_id = movie_dict['id'][i]
                movies.append(movie_dict['title'][i])
                movie_posters.append(get_image(movie_id))
                movie_links.append(movie_dict['homepage'][i])
                vote_avg.append(movie_dict['vote_average'][i])
                runtime.append(movie_dict['runtime'][i])
                release_date.append(movie_dict['release_date'][i])
                num_of_movies += 1

        return movies, movie_posters, movie_links, vote_avg, runtime, release_date

    def get_movies_by_crew(director):
        crew = movie_dict['crew']

        movies = []
        movie_posters = []
        movie_links = []
        vote_avg = []
        runtime = []
        release_date = []

        num_of_movies = 0

        for i in range(len(movie_dict['crew'])):
            if director == movie_dict['crew'][i]:
                movie_id = movie_dict['id'][i]
                movies.append(movie_dict['title'][i])
                movie_posters.append(get_image(movie_id))
                movie_links.append(movie_dict['homepage'][i])
                vote_avg.append(movie_dict['vote_average'][i])
                runtime.append(movie_dict['runtime'][i])
                release_date.append(movie_dict['release_date'][i])
                num_of_movies += 1

        return movies, movie_posters, movie_links, vote_avg, runtime, release_date

    def display_movies(movie_count, movies, images, links, vote_avg, runtime, release_date):
        if movie_count > 0:
            i = 0
            placeholder2 = st.empty()

            with placeholder2.container():
                columns = ['column1', 'column2', 'column3', 'column4', 'column5']
                columns = st.columns(5)

                for col in movie_count * columns:
                    with col:
                        if movies and images and links and vote_avg and runtime and release_date:
                            if int(runtime[i]) == 0:
                                runtime_string = "Undefined"
                            else:
                                runtime_h = int(int(runtime[i]) / 60)
                                runtime_m = int(int(runtime[i]) % 60)
                                if runtime_h != 0 and runtime_m != 0:
                                    runtime_string = str(runtime_h) + "h " + str(runtime_m) + "m"
                                elif runtime_h != 0 and runtime_m == 0:
                                    runtime_string = str(runtime_h) + "h"
                                else:
                                    runtime_string = str(runtime_m) + "m"

                            st.text(movies[i])
                            if pd.isnull(links[i]):
                                st.image(images[i])
                            else:
                                st.markdown('''
                                                            <a href="''' + links[i] + '''">
                                                                <img src=''' + images[i] + ''' width = "100%">
                                                            </a>''', unsafe_allow_html=True
                                            )

                            if vote_avg[i] == 0.0:
                                st.write("⭐ Undefined")
                            else:
                                st.write("⭐" + str(vote_avg[i]))

                            st.write("Release Year: " + str(datetime.strptime(release_date[i], '%Y-%m-%d').year))
                            st.write("Time        : " + runtime_string)
                            i += 1
        else:
            movie_count = len(movies)
            i = 0
            placeholder2 = st.empty()
            columns = []

            with placeholder2.container():
                for j in range(movie_count):
                    columns.append('column' + str(j + 1))
                columns = st.columns(movie_count)

                for col in columns:
                    with col:
                        if movies and images and links and vote_avg and runtime and release_date:
                            if int(runtime[i]) == 0:
                                runtime_string = "Undefined"
                            else:
                                runtime_h = int(int(runtime[i]) / 60)
                                runtime_m = int(int(runtime[i]) % 60)
                                if runtime_h != 0 and runtime_m != 0:
                                    runtime_string = str(runtime_h) + "h " + str(runtime_m) + "m"
                                elif runtime_h != 0 and runtime_m == 0:
                                    runtime_string = str(runtime_h) + "h"
                                else:
                                    runtime_string = str(runtime_m) + "m"

                            st.text(movies[i])
                            if pd.isnull(links[i]):
                                st.image(images[i])
                            else:
                                st.markdown('''
                                            <a href="''' + links[i] + '''">
                                                <img src=''' + images[i] + ''' width = "100%">
                                             </a>''', unsafe_allow_html=True
                                            )

                            if vote_avg[i] == 0.0:
                                st.write("⭐ Undefined")
                            else:
                                st.write("⭐" + str(vote_avg[i]))

                            st.write("Release Year: " + str(datetime.strptime(release_date[i], '%Y-%m-%d').year))
                            st.write("Time        : " + runtime_string)
                            i += 1

    if choice == "Genre":
        genres = pickle.load(open('genres.pkl', 'rb'))
        option = st.selectbox(
            'Choose a genre',
            genres)
        movies, images, links, vote_avg, runtime, release_date = get_movies_by_genre(option)
        movie_count = len(movies)
        movie_count = int(movie_count / 5)
        display_movies(movie_count, movies, images, links, vote_avg, runtime, release_date)

    elif choice == "Popularity":
        movies, images, links, vote_avg, runtime, release_date = get_movies_by_vote()
        movie_count = len(movies)
        movie_count = int(movie_count / 5)
        display_movies(movie_count, movies, images, links, vote_avg, runtime, release_date)

    elif choice == "Director":
        director = pickle.load(open('director.pkl', 'rb'))
        option = st.selectbox(
            'Choose a director',
            director)
        movies, images, links, vote_avg, runtime, release_date = get_movies_by_crew(option)
        movie_count = len(movies)
        movie_count = int(movie_count / 5)
        display_movies(movie_count, movies, images, links, vote_avg, runtime, release_date)


def train_model():
    c.execute('SELECT * FROM movies')
    df = pd.DataFrame(c.fetchall(), columns=['id', 'title', 'genres', 'homepage', 'vote_average', 'vote_count', 'crew',
                                             'release_date', 'runtime', 'tags'])
    df['tags'] = df['tags'].apply(lambda x: x.lower())

    genres = []
    genres_file = []

    for i in df['genres']:
        temp = eval(i)
        genres.append(temp)

    for i in genres:
        for j in i:
            if j and j not in genres_file:
                genres_file.append(j)

    director = []
    for i in df['crew']:
        if i not in director:
            director.append(i)

    ps = PorterStemmer()

    def stemming(string):
        list = []
        for i in string.split():
            list.append(ps.stem(i))
        return " ".join(list)

    df['tags'] = df['tags'].apply(stemming)
    df = df.sort_values('title')
    df = df.reset_index(drop=True)

    vector_count = CountVectorizer(max_features=5000, stop_words='english')
    vectors = vector_count.fit_transform(df['tags']).toarray()

    similarity = cosine_similarity(vectors)
    pickle.dump(df.to_dict(), open('movies_dict.pkl', 'wb'))
    pickle.dump(similarity, open('similarity.pkl', 'wb'))
    pickle.dump(genres_file, open('genres.pkl', 'wb'))
    pickle.dump(director, open('director.pkl', 'wb'))


def main_page():
    movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movie_dict = pd.DataFrame(movie_dict)

    similarity = pickle.load(open('similarity.pkl', 'rb'))

    def get_image(movie_id):
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(
                movie_id))
        data = response.json()
        try:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        except:
            return "https://canterburypress.hymnsam.co.uk/images/products/large/noimage.png?width=400"

    def give_rec(movies):
        index = movie_dict[movie_dict['title'] == movies].index[0]
        dist = similarity[index]
        movies_list = sorted(list(enumerate(dist)), reverse=True, key=lambda x: x[1])[1:11]

        recommended_movie = []
        movie_posters = []
        movie_links = []
        vote_avg = []
        runtime = []
        release_date = []

        for i in movies_list:
            movie_id = movie_dict.iloc[i[0]].id
            recommended_movie.append(movie_dict.iloc[i[0]].title)
            movie_posters.append(get_image(movie_id))
            movie_links.append(movie_dict.iloc[i[0]].homepage)
            vote_avg.append(movie_dict.iloc[i[0]].vote_average)
            runtime.append(movie_dict.iloc[i[0]].runtime)
            release_date.append(movie_dict.iloc[i[0]].release_date)

        return recommended_movie, movie_posters, movie_links, vote_avg, runtime, release_date

    _, col2, _ = st.columns([1, 4.5, 1])

    with col2:
        st.title('Movie Recommendation')

    option = st.selectbox(
        'Choose a movie to get recommendation from',
        movie_dict['title'].values)

    placeholder4 = st.empty()
    rec_button = placeholder4.button('Find Recommendation', on_click=callback)
    if rec_button or st.session_state.button_clicked:
        placeholder4.empty()
        recs, images, links, vote_avg, runtime, release_date = give_rec(option)
        i = 0
        placeholder2 = st.empty()

        with placeholder2.container():
            columns = ['column1', 'column2', 'column3', 'column4', 'column5']
            columns = st.columns(5)

            for col in columns:
                with col:
                    if int(runtime[i]) == 0:
                        runtime_string = "Undefined"
                    else:
                        runtime_h = int(int(runtime[i]) / 60)
                        runtime_m = int(int(runtime[i]) % 60)
                        if runtime_h != 0 and runtime_m != 0:
                            runtime_string = str(runtime_h) + "h " + str(runtime_m) + "m"
                        elif runtime_h != 0 and runtime_m == 0:
                            runtime_string = str(runtime_h) + "h"
                        else:
                            runtime_string = str(runtime_m) + "m"

                    st.text(recs[i])
                    if pd.isnull(links[i]):
                        st.image(images[i])
                    else:
                        st.markdown('''
                                    <a href="''' + links[i] + '''">
                                        <img src=''' + images[i] + ''' width = "100%">
                                    </a>''', unsafe_allow_html=True
                                    )

                    if vote_avg[i] == 0.0:
                        st.write("⭐ Undefined")
                    else:
                        st.write("⭐" + str(vote_avg[i]))

                    st.write("Release Year: " + str(datetime.strptime(release_date[i], '%Y-%m-%d').year))
                    st.write("Time        : " + runtime_string)
                    i += 1

        placeholder = st.empty()

        if placeholder.button('Next'):
            placeholder2.empty()
            columns = ['column1', 'column2', 'column3', 'column4', 'column5']
            columns = st.columns(5)

            for col in columns:
                with col:
                    if int(runtime[i]) == 0:
                        runtime_string = "Undefined"
                    else:
                        runtime_h = int(int(runtime[i]) / 60)
                        runtime_m = int(int(runtime[i]) % 60)
                        if runtime_h != 0 and runtime_m != 0:
                            runtime_string = str(runtime_h) + "h " + str(runtime_m) + "m"
                        elif runtime_h != 0 and runtime_m == 0:
                            runtime_string = str(runtime_h) + "h"
                        else:
                            runtime_string = str(runtime_m) + "m"

                    st.text(recs[i])
                    if pd.isnull(links[i]):
                        st.image(images[i])
                    else:
                        st.markdown('''
                            <a href="''' + links[i] + '''">
                                <img src=''' + images[i] + '''  width = "100%">
                            </a>''', unsafe_allow_html=True
                                    )
                    if vote_avg[i] == 0.0:
                        st.write("⭐ Undefined")
                    else:
                        st.write("⭐" + str(vote_avg[i]))
                    st.write("Release Year: " + str(datetime.strptime(release_date[i], '%Y-%m-%d').year))
                    st.write("Time        : " + runtime_string)
                    i += 1

            placeholder.empty()
            placeholder3 = st.empty()

            if placeholder3.button("Previous"):
                columns = ['column5', 'column4', 'column3', 'column2', 'column1']
                columns = st.columns(5)
                for col in columns:
                    with col:
                        if int(runtime[i]) == 0:
                            runtime_string = "Undefined"
                        else:
                            runtime_h = int(int(runtime[i]) / 60)
                            runtime_m = int(int(runtime[i]) % 60)
                            if runtime_h != 0 and runtime_m != 0:
                                runtime_string = str(runtime_h) + "h " + str(runtime_m) + "m"
                            elif runtime_h != 0 and runtime_m == 0:
                                runtime_string = str(runtime_h) + "h"
                            else:
                                runtime_string = str(runtime_m) + "m"

                        st.text(recs[i])
                        if pd.isnull(links[i]):
                            st.image(images[i])
                        else:
                            st.markdown('''
                                <a href="''' + links[i] + '''">
                                    <img src=''' + images[i] + '''  width = "100%">
                                </a>''', unsafe_allow_html=True
                                        )

                        if vote_avg[i] == 0.0:
                            st.write("⭐ Undefined")
                        else:
                            st.write("⭐" + str(vote_avg[i]))
                        st.write("Release Year: " + str(datetime.strptime(release_date[i], '%Y-%m-%d').year))
                        st.write("Time        : " + runtime_string)
                        i += 1


if __name__ == '__main__':
    main()
