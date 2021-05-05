from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import re
import os
from re import search
import json
from unidecode import unidecode

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_Password')
app.config['MYSQL_DB'] = 'peloton'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["MYSQL_AUTH_PLUGIN"] = "MYSQL_NATIVE_PASSWORD"
db = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pelotonstyle.css')
def pelotoncss():
    return render_template('pelotonstyle.css',)

@app.route("/PelotonSearch", methods=["POST", "GET"])
def PelotonSearch():

    # Get User Inputs from Page Forms
    title_box = request.form.get("title")
    difficulty_category_box = request.form.get("difficultycat")
    instructor_list = request.form.getlist("instructorchosen[]")
    type_box = request.form.get("typecat")
    artist_box = request.form.get("artist")
    exclude_artist_box = request.form.get("excludeartist")
    duration = request.form.get("duration")
    search_index = request.form.get("searchindex")
    # Check the state of the Exclude Artist Checkbox
    if exclude_artist_box == "exclude":
        exclude_artist = True
    else:
        exclude_artist = False
    # Build an SQL command for searching on multiple input Instructor field
    if not instructor_list:
        instructor_sql = ""
    else:
        instructor_sql = "and Instructor IN ("
        first = 1
        for instructor in instructor_list:
            if first:
                instructor_sql += '"' + instructor + '"'
                first = 0
            else:
                instructor_sql += ', "' + instructor + '"'
        instructor_sql += ")"

    cursor = db.connection.cursor()
    # Separate Title Box into param variable to protect against an SQL Injection from the text entry box
    # Double %% to escape the python % syntax
    query = (
                f"""select * from cycling_records where Title LIKE %s {instructor_sql} and Difficulty_Category LIKE "{difficulty_category_box}%%" """
                f"""and Workout_Length LIKE "{duration}%%" and Workout_Type LIKE "{type_box}%%" order by Release_Date DESC LIMIT 10 OFFSET {search_index}"""
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
                    if search(artist_box, artist_entry['Artist'], re.IGNORECASE) or search(artist_box, unidecode(artist_entry['Artist']), re.IGNORECASE):
                        add_entry = False
                        break
                else:
                    if search(artist_box, artist_entry['Artist'], re.IGNORECASE) or search(artist_box, unidecode(artist_entry['Artist']), re.IGNORECASE):
                        add_entry = True
                        break
            if add_entry:
                filtered_results.append(result)
    else:
        filtered_results = results
    cursor.close()
    return jsonify(filtered_results)


if __name__ == "__main__":
    # Access at http://127.0.0.1:5000/ - Will not available on local network
    # app.run()

    # Access at localhost:5000 or http://127.0.0.1:5000/ - Will also be available on local network
    app.run(host='0.0.0.0')
