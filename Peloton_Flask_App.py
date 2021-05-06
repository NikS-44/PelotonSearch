from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import re
import os
from re import search
import json
from unidecode import unidecode

app = Flask(__name__)

def initialize_settings(filename):
    with open(filename, 'w') as settings_writer:
        settings_writer.writelines('##Settings##\n'
                                   'MYSQL_HOST: "localhost"\n'
                                   'MYSQL_USER: "root"\n'
                                   'MYSQL_PASSWORD: "password"\n'
                                   'MYSQL_DB: "Peloton"\n'
                                   'MYSQL_CURSORCLASS: "DictCursor"\n'
                                   'MYSQL_AUTH_PLUGIN: ""MYSQL_NATIVE_PASSWORD"\n'
                                   '##END##')
def settings_reader(filename):
    input_category_types = {}
    categories_read = False
    with open(filename, 'r') as f:
        while True:
            line_read = f.readline().strip()
            if not line_read:
                print("Done")
                break
            if line_read == "##Settings##":
                categories_read = True
                continue
            if "##END##" in line_read and categories_read:
                break
            category_type = line_read.split(':')[0]
            # Start from 2nd argument ('1') to the end of the file (blank), read every other argument to get the quoted match cases ('2')
            category_match_case = line_read.split('"')[1]
            input_category_types[category_type] = category_match_case
    return input_category_types

def multi_sql_format(item_list, sql_category):
    if not item_list:
        item_sql = ""
    else:
        item_sql = f"and {sql_category} IN ("
        first = 1
        for item in item_list:
            if first:
                item_sql += '"' + item + '"'
                first = 0
            else:
                item_sql += ', "' + item + '"'
        item_sql += ")"
    return item_sql


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pelotonstyle.css')
def pelotoncss():
    return render_template('pelotonstyle.css', )


@app.route("/PelotonSearch", methods=["POST", "GET"])
def PelotonSearch():
    cursor = db.connection.cursor()

    # Get User Inputs from Page Forms
    title_box = request.form.get("title")
    difficulty_list = request.form.getlist("difficultycatchosen[]")
    instructor_list = request.form.getlist("instructorchosen[]")
    duration_list = request.form.getlist("durationchosen[]")
    category_list = request.form.getlist("typecatchosen[]")
    artist_box = request.form.get("artist")
    exclude_artist_box = request.form.get("excludeartist")
    duration = request.form.get("duration")
    search_index = request.form.get("searchindex")
    # In this crappy implementation, I am not filtering artists in SQL because it seemed complicated to filter the
    # artists somehow using a JSON search inside of an SQL query. For now, if you do a artist search, I am not
    # limiting the results
    result_limit = 10
    if artist_box:
        result_limit = 100000
    # Check the state of the Exclude Artist Checkbox
    if exclude_artist_box == "exclude":
        exclude_artist = True
    else:
        exclude_artist = False

    difficulty_sql = multi_sql_format(difficulty_list, "Difficulty_Category")
    category_sql = multi_sql_format(category_list, "Workout_Type")
    instructor_sql = multi_sql_format(instructor_list, "Instructor")
    duration_sql = multi_sql_format(duration_list, "Workout_Length")

    # Separate Title Box into param variable to protect against an SQL Injection from the text entry box
    # Double %% to escape the python % syntax
    query = (
        f"""select * from Cycling_Records where Title LIKE %s {instructor_sql} {difficulty_sql} """
        f"""{duration_sql} {category_sql} order by Release_Date DESC LIMIT {result_limit} OFFSET {search_index}"""
    )
    param = '%{}%'.format(title_box)
    cursor.execute(query, (param,))
    results = cursor.fetchall()
    filtered_results = []
    if artist_box:
        for result in results:
            artist_results = json.loads(result['Songs'])
            if exclude_artist:
                add_entry = True
            else:
                add_entry = False
            for artist_entry in artist_results:
                if exclude_artist:
                    # Added unidecode argument to match Artists with non-standard ascii characters such as Tiësto and Beyoncé
                    if search(artist_box, artist_entry['Artist'], re.IGNORECASE) or search(artist_box, unidecode(
                            artist_entry['Artist']), re.IGNORECASE):
                        add_entry = False
                        break
                else:
                    if search(artist_box, artist_entry['Artist'], re.IGNORECASE) or search(artist_box, unidecode(
                            artist_entry['Artist']), re.IGNORECASE):
                        add_entry = True
                        break
            if add_entry:
                filtered_results.append(result)
    else:
        filtered_results = results
    cursor.close()
    return jsonify(filtered_results)


if __name__ == "__main__":
    if not os.path.exists("Settings.txt"):
        initialize_settings("Settings.txt")
    # Read the User Settings (including SQL credentials) from Settings.txt (will always have a default category of Uncategorized)
    # User will need to set up the SQL server config variables in the Settings.txt file that is created
    settings = settings_reader("Settings.txt")
    app.config['MYSQL_HOST'] = settings['MYSQL_HOST']
    app.config['MYSQL_USER'] = settings['MYSQL_USER']
    app.config['MYSQL_PASSWORD'] = settings['MYSQL_PASSWORD']
    app.config['MYSQL_DB'] = settings['MYSQL_DB']
    app.config['MYSQL_CURSORCLASS'] = settings['MYSQL_CURSORCLASS']
    app.config['MYSQL_AUTH_PLUGIN'] = settings['MYSQL_AUTH_PLUGIN']
    db = MySQL(app)

    # Access at http://127.0.0.1:5000/ - Will not available on local network
    # app.run()
    # Access at localhost:5000 or http://127.0.0.1:5000/ - Will also be available on local network
    app.run(host='0.0.0.0')
