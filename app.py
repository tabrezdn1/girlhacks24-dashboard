import streamlit as st
import plotly.express as px
import pandas as pd
from db import get_mongo_data, get_songs_data  # Import the MongoDB connection function
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Fetch data from MongoDB
songs_data = get_songs_data()
songs_df = pd.json_normalize(songs_data)


# Streamlit app layout
st.title("Music App Dashboard")

# Sidebar Configuration
st.sidebar.title("Options")

# Sidebar: Show raw data
show_data = st.sidebar.checkbox("Show raw data")

if show_data:
    #songs_df_new = songs_df.drop(columns=['_id'])
    st.subheader("Raw Data from MongoDB")
    st.write(songs_df)

# Sidebar: Select a chart to display
chart_option = st.sidebar.selectbox(
    "Select a chart to display", 
    ("Top 10 Most Played Songs", "Genre Distribution", "Song Distribution by Language", 
     )
)

# Sidebar: Artist filter
artists = songs_df['artists'].unique()
selected_artist = st.sidebar.selectbox("Select an Artist", artists)

# Sidebar: Plot height slider
plot_height = st.sidebar.slider("Specify plot height", 200, 500, 250)


#Job empowerment Ideas
music_jobs = st.sidebar.button("Bridging Employment Gaps",type="primary")

# Main Area
if not music_jobs:
    # Show raw data if checkbox is selected
    if show_data:
        songs_df_new = songs_df.drop(columns=['_id'])
        st.subheader("Raw Data from MongoDB")
        st.write(songs_df)

    # Bar chart: Most Played Songs
    if chart_option == "Top 10 Most Played Songs":
        st.subheader("Top 10 Most Played Songs")
        top_songs = songs_df[['name', 'play_count']].sort_values('play_count', ascending=False).head(10)
        fig_top_songs = px.bar(top_songs, x='name', y='play_count', title="Most Played Songs", height= plot_height)
        st.plotly_chart(fig_top_songs)

    # Pie chart: Genre Distribution
    if chart_option == "Genre Distribution":
        st.subheader("Genre Distribution")
        genre_count = songs_df.groupby('genre').size().reset_index(name='counts')
        fig_genre = px.pie(genre_count, values='counts', names='genre', title="Genre Distribution")
        st.plotly_chart(fig_genre)

    # Pie chart: Song Distribution by Language
    if chart_option == "Song Distribution by Language":
        st.subheader("Song Distribution by Language")
        song_by_lang = songs_df.groupby('language').size().reset_index(name='counts')
        fig_genre = px.pie(song_by_lang, values='counts', names='language', title="Song Distribution by Language")
        st.plotly_chart(fig_genre)

    
    # Example query to find the most popular genre and artist by play count
    if chart_option == "Genre Popularity Over Time":    
        most_popular_song = songs_data.find_one(sort=[("play_count", -1)])
        popular_genre = most_popular_song["genre"]
        popular_artist = most_popular_song["artists"]
        # Advanced Analytics: Genre Popularity Over Time
        def genre_popularity_over_time():
            genre_play_counts = songs_data.aggregate([
                {"$group": {
                    "_id": {"genre": "$genre", "date": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}}}, 
                    "total_plays": {"$sum": "$play_count"}
                }}
            ])
            
            # Convert to DataFrame
            df = pd.DataFrame(list(genre_play_counts))
            
            # Split the '_id' column into 'genre' and 'date'
            df[['genre', 'date']] = pd.DataFrame(df['_id'].tolist(), index=df.index)
            df.drop(columns=['_id'], inplace=True)  # Drop the '_id' column

            plt.figure(figsize=(10,6))
            sns.lineplot(data=df, x='date', y='total_plays', hue='genre')
            plt.title('Genre Popularity Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot()
        genre_popularity_over_time()
# 

    # Display filtered songs by selected artist
    st.subheader(f"Songs by {selected_artist}")
    filtered_songs = songs_df[songs_df['artists'] == selected_artist]
    filtered_songs = filtered_songs.drop(columns=['_id'])
    st.dataframe(filtered_songs)

    if chart_option == "Top 5 Artists by Play Count":
        def top_artists_ranking():
            top_artists = songs_data.aggregate([
                {"$group": {"_id": "$artists", "total_plays": {"$sum": "$play_count"}}},
                {"$sort": {"total_plays": -1}},
                {"$limit": 5}
            ])

            # Convert to DataFrame
            artist_df = pd.DataFrame(list(top_artists))

            plt.figure(figsize=(10,6))
            sns.barplot(data=artist_df, x='_id', y='total_plays')
            plt.title('Top 5 Artists by Play Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot()
        top_artists_ranking()

if music_jobs:
    tab2, tab1 = st.tabs(["Music Industry Side Hustles", "Innovative Music Business Ideas"])
    most_popular_song = max(songs_data, key=lambda x: x.get('play_count', 0))  # Use max() to find the song with the highest play_count

    # Get details from the most popular song
    popular_genre = most_popular_song.get("genre", "Unknown")
    popular_artist = most_popular_song.get("artists", "Unknown")
    
    with tab1:
        st.subheader("Innovative Music Business Ideas")
        st.write(f"Based on the popularity of {popular_genre} music and artists like {popular_artist}, consider the following business ideas:")

        # Provide suggestions based on analytics and data
        st.markdown(f"""
        1. **Start a Record Label**: {popular_genre} music and artists like {popular_artist} are seeing high play counts. A record label focusing on this genre could attract more emerging talent.
        2. **Music Licensing Company**: With the rise in demand for {popular_genre} music, a licensing company can focus on monetizing this trend in films, ads, and games.
        3. **Music Festival Organization**: Host a {popular_genre} music festival featuring artists like {popular_artist}, based on the growing interest.
        4. **Subscription Service for Exclusive Content**: Your data indicates strong engagement in this genre, making it ideal for a subscription-based service that offers exclusive artist content.
        """)
    
    with tab2:
        st.subheader("Music Industry Side Hustles")
        st.write(f"If you're looking to earn extra cash in the {popular_genre} space, here are some side hustle ideas based on data insights:")

        # Provide suggestions for side hustles based on MongoDB data
        st.markdown(f"""
        1. **Freelance Music Production**: Offer production services for artists in {popular_genre}, which shows high popularity in your dataset.
        2. **DJ at Events**: If {popular_genre} music is trending, explore DJing at events or starting an online radio show to capitalize on its growing demand.
        3. **Sell Beats Online**: Create and sell beats tailored to popular genres like {popular_genre}, which is performing well based on your data.
        4. **Music Blogging**: Start a blog focused on {popular_genre}, helping others discover new music while earning affiliate income from recommendations.
        """)
