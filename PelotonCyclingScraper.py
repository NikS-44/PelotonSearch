import requests
import re
import datetime
import time
import json
import os
import mysql.connector
from datetime import datetime


def Cycling_Scrape_MySQL():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=os.getenv('MYSQL_Password')
    )
    sql_cursor = db.cursor()
    sql_cursor.execute("""CREATE DATABASE IF NOT EXISTS Peloton""")

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=os.getenv('MYSQL_Password'),
        database="Peloton"
    )
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

    workout_types = [("Intervals", "7579b9edbdf9464fa19eb58193897a73"),
                     ("Low Impact", "59a49f882ea9475faa3110d50a8fb3f3"),
                     ("Climb", "bf6639f2e50a4f0395cb1479542ed4bd"), ("Live DJ", "a2ee6b0a98e2431baf60e5261b8605e2"),
                     ("Power Zone", "665395ff3abf4081bf315686227d1a51"),
                     ("Heart Rate Zone", "8c34b36dba084e22b91426621759230d"),
                     ("Theme", "f10471dcd6a34e5f8ed54eb634b5df19"), ("Beginner", "9f9be657134e4d868d76ae4988da01f1"),
                     ("Music", "c87e20095d80463db5ce04df7fe2b989"), ("Groove", "9745b8e2cb274a28b096387073a5d993"),
                     ("Pro Cyclist", "4228e9e57bf64c518d58a1d0181760c4")]

    headers = {'peloton-platform': 'web'}
    cookies = {'peloton_session_id': os.getenv('peloton_session_id')}
    # Change workout request limit to set the number of classes to fetch details on.
    # For initial database build, start with a value of 9000, then you can rerun this daily with a value of 100
    workout_request_limit = 100
    url = f"https://api.onepeloton.com/api/v2/ride/archived?browse_category=cycling&limit={workout_request_limit}&content_format=audio%2Cvideo&page=0&sort_by=original_air_time&desc=true"
    page_raw = requests.get(url, headers=headers, cookies=cookies)
    page = json.loads(page_raw.text)
    # Local copy of a page request as to not call it every time I rebuild the database from scratch
    # with open('PelotonCycling.txt') as f:
    #     page = json.load(f)
    for workout in page['data']:
        workout_id = workout['id']
        # Keep local copies of classes as to not spam the API
        if os.path.isfile(f"./classes/{workout_id}.json"):
            with open(f'./classes/{workout_id}.json', 'r', encoding='utf8') as workout_file:
                workout_info = json.load(workout_file)
        else:
            workout_api_url = f'https://api.onepeloton.com/api/ride/{workout_id}/details?stream_source=multichannel'
            workout_info_raw = requests.get(workout_api_url, headers=headers, cookies=cookies)
            workout_info = workout_info_raw.json()
            print(workout_api_url)
            # To prevent me from spamming their API, I elected to add a 1s artificial timer between page requests
            time.sleep(1)
            with open(f'./classes/{workout_id}.json', 'w', encoding='utf8') as workout_file:
                try:
                    workout_file.write(workout_info_raw.text)
                except UnicodeEncodeError:
                    print(f"Error with workout id: {workout_id}")
        print("\n")
        songs = workout_info['playlist']['songs']
        title = workout_info['ride']['title']
        instructor = workout_info['ride']['instructor']['name']
        # User_rating will be updated from the initial multi-class page request as to get latest ratings when
        # updating existing records
        user_rating = round(float(workout['overall_estimate']) * 100, 3)
        peloton_difficulty_rating = round(float(workout['difficulty_estimate']), 2)
        duration = int(workout_info['ride']['duration']) / 60
        workout_type_id = workout_info['ride']['class_type_ids'][0]
        air_date = datetime.utcfromtimestamp(workout_info['ride']['original_air_time']).strftime('%Y-%m-%d')
        image_link = workout_info['ride']['image_url']
        for workout_type in workout_types:
            category, workout_type_id_lookup = workout_type
            if workout_type_id == workout_type_id_lookup:
                workout_category = category
                break
        current_date = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d')
        target_lower_output = 0
        target_upper_output = 1
        difficulty_rating = 0
        try:
            target_lower_output = int(
                workout_info['target_class_metrics']['total_expected_output']['expected_lower_output'])
            target_upper_output = int(
                workout_info['target_class_metrics']['total_expected_output']['expected_upper_output'])
            print(f"Expected Lower Output: {target_lower_output}")
            print(f"Expected Higher Output: {target_upper_output}")
            # Scaling factor to better normalize class difficulty on a scale of 1-10 (max difficulty desired).
            # A few outliers will come out over 10, but most will be 1-10. Could have used more math, but
            # linear scaling was more simple since we only use this to determine difficulty categories
            scaling_factor = 1.66
            difficulty_rating = round(
                ((target_lower_output + target_upper_output) / 2) / (int(duration) * scaling_factor), 2)
        except KeyError:
            print(f"Output Targets Not Defined")
        # Custom difficulty range/categories based on expected output
        difficulty_category = "Power Zone" if difficulty_rating == 0 \
            else "Very Easy" if difficulty_rating < 3.6 \
            else "Easy" if difficulty_rating < 4.6 \
            else "Medium" if difficulty_rating <= 5.6 \
            else "Hard" if difficulty_rating <= 6.5 \
            else "Very Hard"
        print(f"Instructor: {instructor}")
        print(f"Title: {title}")
        print(f"Difficulty: {difficulty_rating}")
        print(f"Peloton Difficulty: {peloton_difficulty_rating}")
        print(f"Difficulty Category: {difficulty_category}")
        print(f"Workout Category: {workout_category}")
        print(f"Duration: {int(duration)} Minutes")
        print(f"Air Date {air_date}")
        print(f"Current Date {current_date}")
        print(f"Image Link: {image_link}")
        workout_link = f'https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={workout_id}'
        print(workout_link)
        # Rebuild Artist/Song JSON because there was a lot metadata we didn't need that was slowing Database queries
        song_array = []
        artist_array = []
        for song in songs:
            song_title = song['title']
            song_artist = song['artists'][0]['artist_name']
            song_array.append(song_title)
            artist_array.append(song_artist)
        songs_json = json.dumps([{"Artist": a, "Song": s} for a, s in zip(artist_array, song_array)])

        query = "SELECT * FROM Cycling_Records WHERE Workout_ID=%s"
        sql_cursor.execute(query, (workout_id,))
        cycling_entry = sql_cursor.fetchone()
        if cycling_entry is None:
            print(f"New Entry Found:{workout_id} \nAdding to the database...")
            query = f"INSERT INTO Cycling_Records( Title, Workout_ID, Difficulty_Rating, Peloton_Difficulty_Rating, " \
                    f"Workout_Length, User_Rating, Instructor, Workout_Type, Workout_Link, Difficulty_Category," \
                    f" Expected_Min, Expected_Max, Release_Date, Last_Modified, Hide, Thumbnail, Songs) " \
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            sql_cursor.execute(query, (
                title, workout_id, difficulty_rating, peloton_difficulty_rating, duration, user_rating, instructor,
                workout_category, workout_link, difficulty_category, target_lower_output, target_upper_output,
                air_date, current_date, 0, image_link, songs_json))

            sql_cursor.execute("SELECT * FROM Cycling_Records WHERE Workout_ID=%s", (workout_id,))
            new_workout_entry = sql_cursor.fetchone()
            if new_workout_entry is None:
                print("Error adding tv entry to database")
            else:
                print(f"New Workout: {workout_id} successfully added\n")
        else:
            # Update Entries with the latest Difficulty and User Ratings
            query = "UPDATE Cycling_Records SET Peloton_Difficulty_Rating=%s, User_Rating=%s WHERE Workout_ID=%s"
            sql_cursor.execute(query, (peloton_difficulty_rating, user_rating, workout_id))
    db.commit()
    db.close()


if __name__ == "__main__":
    Cycling_Scrape_MySQL()
