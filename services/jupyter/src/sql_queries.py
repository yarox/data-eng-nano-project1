# DROP TABLES

materialized_table_drop = 'DROP MATERIALIZED VIEW songplay_extra;'
any_temp_table_drop = 'DROP TABLE IF EXISTS temp_{table};'
songplay_table_drop = 'DROP TABLE IF EXISTS songplays;'
user_table_drop = 'DROP TABLE IF EXISTS users;'
song_table_drop = 'DROP TABLE IF EXISTS songs;'
artist_table_drop = 'DROP TABLE IF EXISTS artists;'
time_table_drop = 'DROP TABLE IF EXISTS time;'

# CREATE TABLES

materialized_table_create = '''
    CREATE MATERIALIZED VIEW songplay_extra
    AS
        SELECT
            s.song_id,
            a.artist_id,
            s.title as song_title,
            a.name as artist_name,
            s.duration as song_duration
        FROM songs s
            JOIN artists a ON s.artist_id = a.artist_id;
'''

any_temp_table_create = '''
    CREATE TEMP TABLE IF NOT EXISTS temp_{table}
    (LIKE {table} INCLUDING DEFAULTS);
'''

songplay_table_create = '''
    CREATE TABLE IF NOT EXISTS songplays (
        songplay_id SERIAL PRIMARY KEY,
        start_time BIGINT NOT NULL REFERENCES time(start_time) ON DELETE CASCADE,
        user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        level TEXT NOT NULL,
        song_id TEXT REFERENCES songs(song_id) ON DELETE CASCADE,
        artist_id TEXT REFERENCES artists(artist_id) ON DELETE CASCADE,
        session_id INT NOT NULL,
        location TEXT NOT NULL,
        user_agent TEXT NOT NULL
    );
'''

user_table_create = '''
    CREATE TABLE IF NOT EXISTS users (
        user_id INT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        level TEXT NOT NULL
    );
'''

song_table_create = '''
    CREATE TABLE IF NOT EXISTS songs (
        song_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        artist_id TEXT NOT NULL,
        year INT NOT NULL,
        duration FLOAT NOT NULL
    );
'''

artist_table_create = '''
    CREATE TABLE IF NOT EXISTS artists (
        artist_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT,
        latitude FLOAT,
        longitude FLOAT
    );
'''

time_table_create = '''
    CREATE TABLE IF NOT EXISTS time (
        start_time BIGINT PRIMARY KEY,
        hour INT NOT NULL,
        day INT NOT NULL,
        week INT NOT NULL,
        month INT NOT NULL,
        year INT NOT NULL,
        weekday INT NOT NULL
    );
'''

# INSERT RECORDS

any_table_insert_bulk = '''
    INSERT INTO {table}
    SELECT *
    FROM temp_{table}
    ON CONFLICT DO NOTHING;
'''

songplay_table_insert = '''
    INSERT INTO songplays (
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
'''

user_table_insert = '''
    INSERT INTO users (
        user_id,
        first_name,
        last_name,
        gender,
        level
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE SET
        level = EXCLUDED.level;
'''

song_table_insert = '''
    INSERT INTO songs (
        song_id,
        title,
        artist_id,
        year,
        duration
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
'''

artist_table_insert = '''
    INSERT INTO artists (
        artist_id,
        name,
        location,
        latitude,
        longitude
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
'''


time_table_insert = '''
    INSERT INTO time (
        start_time,
        hour,
        day,
        week,
        month,
        year,
        weekday
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
'''

# FIND SONGS

songplay_extra_select = '''
    SELECT
        song_id,
        artist_id
    FROM songplay_extra
    WHERE
        song_title = %s AND
        artist_name = %s AND
        song_duration = %s;
'''

song_select = '''
    SELECT
        s.song_id,
        a.artist_id
    FROM songs s
        JOIN artists a ON s.artist_id = a.artist_id
    WHERE
        s.title = %s AND
        a.name = %s AND
        s.duration = %s;
'''

# QUERY LISTS

create_table_queries = [user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
