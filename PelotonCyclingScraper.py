import requests
import re
import datetime
import time
import json
import os
import mysql.connector
from mysql.connector import connect, Error
from datetime import datetime

cycling_workout_types = {"7579b9edbdf9464fa19eb58193897a73": "Intervals",
                         "59a49f882ea9475faa3110d50a8fb3f3": "Low Impact",
                         "bf6639f2e50a4f0395cb1479542ed4bd": "Climb",
                         "a2ee6b0a98e2431baf60e5261b8605e2": "Live DJ",
                         "665395ff3abf4081bf315686227d1a51": "Power Zone",
                         "8c34b36dba084e22b91426621759230d": "Heart Rate Zone",
                         "f10471dcd6a34e5f8ed54eb634b5df19": "Theme",
                         "9f9be657134e4d868d76ae4988da01f1": "Beginner",
                         "c87e20095d80463db5ce04df7fe2b989": "Music",
                         "9745b8e2cb274a28b096387073a5d993": "Groove",
                         "4228e9e57bf64c518d58a1d0181760c4": "Pro Cyclist"}


class CyclingWorkout:
    def __init__(self, latest_workout_json):
        self.workout_id = latest_workout_json['id']
        self.user_rating = round(float(latest_workout_json['overall_estimate']) * 100, 3)
        self.peloton_difficulty_rating = round(float(latest_workout_json['difficulty_estimate']), 2)
        workout_info = self.get_local_workout_info_json()
        self.title = workout_info['ride']['title']
        self.instructor = workout_info['ride']['instructor']['name']
        self.duration = int(workout_info['ride']['duration']) / 60
        workout_type_id = workout_info['ride']['class_type_ids'][0]
        self.air_date = datetime.utcfromtimestamp(workout_info['ride']['original_air_time']).strftime('%Y-%m-%d')
        self.image_link = workout_info['ride']['image_url']
        self.workout_category = cycling_workout_types[workout_type_id]
        self.current_date = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d')
        self.target_lower_output = 0
        self.target_upper_output = 1
        self.difficulty_rating = 0
        try:
            self.target_lower_output = int(
                workout_info['target_class_metrics']['total_expected_output']['expected_lower_output'])
            self.target_upper_output = int(
                workout_info['target_class_metrics']['total_expected_output']['expected_upper_output'])
            # Scaling factor to better normalize class difficulty on a scale of 1-10 (max difficulty desired).
            # A few outliers will come out over 10, but most will be 1-10. Could have used more math, but
            # linear scaling was more simple since we only use this to determine difficulty categories
            scaling_factor = 1.66
            self.difficulty_rating = round(
                ((self.target_lower_output + self.target_upper_output) / 2) / (int(self.duration) * scaling_factor), 2)
        except KeyError:
            print(f"Output Targets Not Defined")
        # Custom difficulty range/categories based on expected output
        self.difficulty_category = "Power Zone" if self.difficulty_rating == 0 \
            else "Very Easy" if self.difficulty_rating < 3.6 \
            else "Easy" if self.difficulty_rating < 4.6 \
            else "Medium" if self.difficulty_rating <= 5.6 \
            else "Hard" if self.difficulty_rating <= 6.5 \
            else "Very Hard"
        self.workout_link = f'https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={self.workout_id}'
        # Rebuild Artist/Song JSON because there was a lot metadata we didn't need that was slowing Database queries
        songs = workout_info['playlist']['songs']
        song_array = []
        artist_array = []
        for song in songs:
            song_title = song['title']
            song_artist = song['artists'][0]['artist_name']
            song_array.append(song_title)
            artist_array.append(song_artist)
        self.songs_json = json.dumps([{"Artist": a, "Song": s} for a, s in zip(artist_array, song_array)])

    def print(self):
        print(f"\nInstructor: {self.instructor}")
        print(f"Title: {self.title}")
        print(f"Difficulty: {self.difficulty_rating}")
        print(f"Expected Lower Output: {self.target_lower_output}")
        print(f"Expected Higher Output: {self.target_upper_output}")
        print(f"Peloton Difficulty: {self.peloton_difficulty_rating}")
        print(f"Difficulty Category: {self.difficulty_category}")
        print(f"Workout Category: {self.workout_category}")
        print(f"Duration: {int(self.duration)} Minutes")
        print(f"Air Date {self.air_date}")
        print(f"Current Date {self.current_date}")
        print(f"Image Link: {self.image_link}")
        print(f"Workout Link:{self.workout_link}")

    def get_local_workout_info_json(self):
        # Keep local copies of classes as to not spam the API
        if os.path.isfile(f"./classes/{self.workout_id}.json"):
            with open(f'./classes/{self.workout_id}.json', 'r', encoding='utf8') as workout_file:
                workout_info = json.load(workout_file)
        else:
            workout_api_url = f'https://api.onepeloton.com/api/ride/{self.workout_id}/details?stream_source=multichannel'
            workout_info_raw = requests.get(workout_api_url, headers=headers, cookies=cookies)
            workout_info = workout_info_raw.json()
            # To prevent me from spamming their API, I elected to add a 1s artificial timer between page requests
            time.sleep(1)
            with open(f'./classes/{self.workout_id}.json', 'w', encoding='utf8') as workout_file:
                try:
                    workout_file.write(workout_info_raw.text)
                except UnicodeEncodeError:
                    print(f"Error with workout id: {self.workout_id}")
        return workout_info

    def db_add_or_update(self, db):
        sql_cursor = db.cursor()
        query = "SELECT * FROM Cycling_Records WHERE Workout_ID=%s"
        sql_cursor.execute(query, (self.workout_id,))
        cycling_entry = sql_cursor.fetchone()
        if cycling_entry is None:
            print(f"New Entry Found:{self.workout_id} \nAdding to the database...")
            query = f"INSERT INTO Cycling_Records( Title, Workout_ID, Difficulty_Rating, Peloton_Difficulty_Rating, " \
                    f"Workout_Length, User_Rating, Instructor, Workout_Type, Workout_Link, Difficulty_Category," \
                    f" Expected_Min, Expected_Max, Release_Date, Last_Modified, Hide, Thumbnail, Songs) " \
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            sql_cursor.execute(query, (
                self.title, self.workout_id, self.difficulty_rating, self.peloton_difficulty_rating,
                self.duration,
                self.user_rating, self.instructor, self.workout_category, self.workout_link,
                self.difficulty_category,
                self.target_lower_output, self.target_upper_output, self.air_date, self.current_date,
                0, self.image_link, self.songs_json))

            sql_cursor.execute("SELECT * FROM Cycling_Records WHERE Workout_ID=%s", (self.workout_id,))
            new_workout_entry = sql_cursor.fetchone()
            if new_workout_entry is None:
                print("Error adding tv entry to database")
            else:
                print(f"New Workout: {self.workout_id} successfully added\n")
        else:
            # Update Entries with the latest Difficulty and User Ratings
            query = "UPDATE Cycling_Records SET Peloton_Difficulty_Rating=%s, User_Rating=%s WHERE Workout_ID=%s"
            sql_cursor.execute(query, (self.peloton_difficulty_rating, self.user_rating, self.workout_id))


def mysql_database_initialization(username, password):
    try:
        with connect(
                host="localhost",
                user=username,
                passwd=password
        ) as db_init:
            db_init_cursor = db_init.cursor()
            db_init_cursor.execute("""CREATE DATABASE IF NOT EXISTS Peloton""")
    except Error as e:
        print(e)


def mysql_cycling_record_table_create(username, password):
    try:
        with connect(
                host="localhost",
                user=username,
                passwd=password,
                database="Peloton"
        ) as db:
            sql_cursor = db.cursor()
            sql_cursor.execute("""CREATE TABLE IF NOT EXISTS Cycling_Records(
                                            Title VARCHAR(50),
                                            Workout_ID VARCHAR(32),
                                            Difficulty_Rating FLOAT(4,2),
                                            Peloton_Difficulty_Rating FLOAT(4,2),
                                            Workout_Length smallint,
                                            User_Rating FLOAT(6,3),
                                            Instructor VARCHAR(50),
                                            Workout_Type VARCHAR(15),
                                            Workout_Link VARCHAR(111),
                                            Difficulty_Category VARCHAR(10),
                                            Expected_Min smallint UNSIGNED,
                                            Expected_Max smallint UNSIGNED,
                                            Release_Date VARCHAR(10),
                                            Last_Modified VARCHAR(10),
                                            Hide smallint UNSIGNED,
                                            Thumbnail VARCHAR(150),
                                            Songs JSON,
                                            PRIMARY KEY (WORKOUT_ID)
                                            )""")
    except Error as e:
        print(e)


def get_multiple_class_json_data(web_cookies, web_headers, web_workout_request_limit):
    url = f"https://api.onepeloton.com/api/v2/ride/archived?browse_category=cycling&limit={web_workout_request_limit}&content_format=audio%2Cvideo&page=0&sort_by=original_air_time&desc=true"
    multiple_class_api_raw = requests.get(url, headers=web_headers, cookies=web_cookies)
    multiple_class_api_parsed = json.loads(multiple_class_api_raw.text)
    return multiple_class_api_parsed


if __name__ == "__main__":
    MYSQL_username = "root"
    MYSQL_password = os.getenv('MYSQL_Password')
    # Create database and/or table if it does not exist yet
    mysql_database_initialization(MYSQL_username, MYSQL_password)
    mysql_cycling_record_table_create(MYSQL_username, MYSQL_password)
    # Change workout request limit to set the number of classes to fetch details on
    workout_request_limit = 9000
    # My peloton_session_id cookie is stored in the OS system environment variables
    cookies = {'peloton_session_id': os.getenv('peloton_session_id')}
    headers = {'peloton-platform': 'web'}
    class_data = get_multiple_class_json_data(cookies, headers, workout_request_limit)
    # Walk through individual class records and add or update class records
    # Opening the db connection once rather than for every record update sped up the program 10x
    try:
        with connect(
                host="localhost",
                user=MYSQL_username,
                passwd=MYSQL_password,
                database="Peloton"
        ) as database_conn:
            for workout in class_data['data']:
                workout_instance = CyclingWorkout(workout)
                workout_instance.print()
                workout_instance.db_add_or_update(database_conn)
            database_conn.commit()
    except Error as e:
        print(e)
