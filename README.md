# Project 1: Data Modeling with Postgres
This is the code for the first project of the [Udacity Data Engineering Nanodegree](https://www.udacity.com/course/data-engineer-nanodegree--nd027).

## Quickstart
Make sure you have already installed both Docker Engine and Docker Compose. You don't need to install PostgreSQL or Jupyter, as both are provided by the Docker images.

From the project directory, start up the application by running `docker-compose up --build -d`. Compose builds an image for both the `postgres` and `jupyter` services and starts the containers in the background and leaves them running.

Execute `docker-compose logs -f jupyter` and check the server logs for a URL to the notebook server.

In addition to the data files, the project workspace includes these other files:

+ `test.ipynb` displays the first few rows of each table to let you check your database.
+ `create_tables.py` drops and creates the tables. Run this file to reset the tables before each time you run the ETL scripts.
+ `etl.ipynb` reads and processes a single file from `song_data` and `log_data` and loads the data into the tables.
+ `etl.py` reads and processes files from `song_data` and `log_data` and loads them into the database.
+ `etl_bulk.py` is a version of `etl.py` that inserts data using the COPY command to bulk insert log files instead of using INSERT on one row at a time.
+ `sql_queries.py` contains all the sql queries.
+ `dashboard.ipynb` displays a few example queries and results for song play analysis.
+ `README.md`.

To populate the tables run `python create_tables.py` followed by either `python etl.py` or `python etl_bulk.py`. Remember to run `python create_tables.py` before any `etl*.py` command in order to reset the database.

## Project Overview
### Introduction
A startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app. The analytics team is particularly interested in understanding what songs users are listening to. Their data resides in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

They'd like to create a Postgres database with tables designed to optimize queries on song play analysis.

### Schema Design
We created a star schema optimized for queries on song play analysis using the provided datasets. This includes the following tables.

#### Fact Table
1. **songplays** - records in log data associated with song plays i.e. records with page `NextSong`
    + songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

#### Dimension Tables
1. **users** - users in the app
    + user_id, first_name, last_name, gender, level

2. **songs** - songs in music database
    + song_id, title, artist_id, year, duration

3. **artists** - artists in music database
    + artist_id, name, location, latitude, longitude

4. **time** - timestamps of records in songplays broken down into specific units
    + start_time, hour, day, week, month, year, weekday

### ETL Pipeline
The pipeline is divided into two main parts. In the first part, we perform ETL on the `song_data` dataset to create the `songs` and `artists` dimensional tables.

In the second part, we do a similar process on the `log_data` dataset in order to create the `time` and `users` dimensional tables, as well as the `songplays` fact table. This one is a little more complicated since information from the songs table, artists table, and original log file are all needed for the `songplays` table. Since the log file does not specify an ID for either the song or the artist, we need to get the song ID and artist ID by querying the songs and artists tables to find matches based on song title, artist name, and song duration time.

The code in `etl.py` transforms the files in the dataset one by one and loads the results one row at a time into the approppiate tables.

On the other hand, the code in `etl_bulk.py` is based around the `COPY` command and loads the whole dataset from a CSV representation of each table in the schema. It uses temporary tables in order to easily handle table constraints. We tried to speed things up by using a materialized view instead of joining the `songs` and `artists` tables each time. We also implemented a simple cache that we check before hitting the database.

Both scripts produce the same results, but the bulk version is ~2.5 times faster for this amount of data.
