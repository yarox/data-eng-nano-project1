import pandas as pd
import numpy as np
import psycopg2

import tempfile
import glob
import os

from sql_queries import *


def get_files(filepath):
    glob_path = os.path.join(filepath,'**/*.json')
    return glob.glob(glob_path, recursive=True)


def concat_files(files):
    df = pd.DataFrame()

    for f in files:
        temp = pd.read_json(f, lines=True)
        df = df.append(temp)

    return df


def get_songplay_extra(row, cur):
    # get song_id and artist_id from song and artist tables
    cur.execute(song_select, (row.song, row.artist, row.length))
    result = cur.fetchone()

    if result:
        song_id, artist_id = result
    else:
        song_id, artist_id = None, None

    return { 'songId': song_id, 'artistId': artist_id }


def bulk_insert(cur, data, table, unique_column=None, table_columns=None):
    # drop duplicates based on a specific column
    if unique_column is not None:
        data = data.astype({unique_column: str})
        data = data.drop_duplicates(subset=unique_column)

    # create temp table
    temp_table_create = any_temp_table_create.format(table=table)
    cur.execute(temp_table_create)

    # dump data to CSV file and import into temp table using the copy command
    with tempfile.NamedTemporaryFile() as f:
        data.to_csv(f.name, header=False, index=False, sep='\t')
        cur.copy_from(f, f'temp_{table}', sep='\t', null='', columns=table_columns)

    # insert data into the final table
    table_insert_bulk = any_table_insert_bulk.format(table=table)
    cur.execute(table_insert_bulk)

    # drop the temp table
    table_drop = any_temp_table_drop.format(table=table)
    cur.execute(table_drop)


def process_song_files(cur, files):
    # concatenate all song files into one dataframe
    df = concat_files(files)

    # replace blanks with NaNs
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    # insert song records
    song_columns = ['song_id', 'title', 'artist_id', 'year', 'duration']
    song_data = df[song_columns]
    bulk_insert(cur, song_data, 'songs', 'song_id')

    # insert artist records
    artist_columns = ['artist_id', 'artist_name', 'artist_location',
        'artist_latitude', 'artist_longitude']
    artist_data = df[artist_columns]
    bulk_insert(cur, artist_data, 'artists', 'artist_id')


def process_log_files(cur, files):
    # concatenate all log files into one dataframe
    df = concat_files(files)

    # filter by NextSong action and replace blanks with NaNs
    df = df[df.page == 'NextSong']
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')

    # insert time records
    time_values = [df.ts.values, t.dt.hour.values, t.dt.day.values,
        t.dt.weekofyear.values, t.dt.month.values, t.dt.year.values,
        t.dt.weekday.values]

    time_columns = ['start_time', 'hour', 'day', 'week', 'month', 'year',
        'weekday']

    time_data = pd.DataFrame(dict(zip(time_columns, time_values)))
    bulk_insert(cur, time_data, 'time', 'start_time')

    # insert user records
    user_columns = ['userId', 'firstName', 'lastName', 'gender', 'level']
    user_data = df[user_columns]
    bulk_insert(cur, user_data, 'users', 'userId')

    # insert songplay records
    songplay_extra = df.apply(get_songplay_extra, axis=1, result_type='expand', cur=cur)
    df = pd.concat([df, songplay_extra], axis=1)

    songplay_columns = ['ts', 'userId', 'level', 'songId', 'artistId', 'sessionId',
        'location', 'userAgent']
    songplay_data = df[songplay_columns]

    table_columns = ['start_time', 'user_id', 'level', 'song_id', 'artist_id',
        'session_id', 'location', 'user_agent']

    bulk_insert(cur, songplay_data, 'songplays', table_columns=table_columns)


def process_data(cur, conn, filepath, func):
    # get all files matching extension from directory
    all_files = get_files(filepath)

    # get total number of files found
    num_files = len(all_files)
    print(f'{num_files} files found in {filepath}')

    # process files
    func(cur, all_files)
    conn.commit()

    print('all files processed.')


def main():
    conn = psycopg2.connect("host=postgres dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_files)
    process_data(cur, conn, filepath='data/log_data', func=process_log_files)

    conn.close()


if __name__ == "__main__":
    main()
