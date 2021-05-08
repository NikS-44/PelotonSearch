from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import os

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
        item_sql = f"AND {sql_category} IN ("
        first = True
        for item in item_list:
            if first:
                item_sql += '"' + item + '"'
                first = False
            else:
                item_sql += ', "' + item + '"'
        item_sql += ")"
    return item_sql


def json_search_sql_format(json_search_item_list, sql_category, exclude):
    json_search_item_sql = ""
    if not json_search_item_list:
        return json_search_item_sql
    else:
        if exclude:
            first = True
            for json_search_item in json_search_item_list:
                # Remove case sensitivity
                json_search_item_lower = json_search_item.lower()
                if first:
                    # Double %% to escape the python % parameter syntax
                    json_search_item_sql += f"AND (JSON_SEARCH(LOWER({sql_category}),'one', '%%{json_search_item_lower}%%') IS NULL "
                    first = False
                else:
                    json_search_item_sql += f"AND JSON_SEARCH(LOWER({sql_category}),'one', '%%{json_search_item_lower}%%') IS NULL "
            json_search_item_sql += ")"
        else:
            first = True
            for json_search_item in json_search_item_list:
                # Remove case sensitivity
                json_search_item_lower = json_search_item.lower()
                if first:
                    # Double %% to escape the python % parameter syntax
                    json_search_item_sql += f"AND (JSON_SEARCH(LOWER({sql_category}),'one', '%%{json_search_item_lower}%%') IS NOT NULL "
                    first = False
                else:
                    json_search_item_sql += f"OR JSON_SEARCH(LOWER({sql_category}),'one', '%%{json_search_item_lower}%%') IS NOT NULL "
            json_search_item_sql += ")"
    return json_search_item_sql


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
    difficulty_list = request.form.getlist("difficulty_cat_chosen[]")
    instructor_list = request.form.getlist("instructor_chosen[]")
    duration_list = request.form.getlist("duration_chosen[]")
    category_list = request.form.getlist("type_cat_chosen[]")
    artist_box = request.form.get("artist")
    exclude_artist_box = request.form.get("exclude_artist")
    search_index = request.form.get("search_index")

    # Future Feature- Multi-input custom song/artist filters
    # Comma seperated input parsing could work for getting multi custom inputs from the website
    artist_list = []
    if artist_box:
        artist_list.append(artist_box)

    result_limit = 10

    # Check the state of the Exclude Artist Checkbox
    if exclude_artist_box == "exclude":
        exclude_artist = True
    else:
        exclude_artist = False

    difficulty_sql = multi_sql_format(difficulty_list, "Difficulty_Category")
    category_sql = multi_sql_format(category_list, "Workout_Type")
    instructor_sql = multi_sql_format(instructor_list, "Instructor")
    duration_sql = multi_sql_format(duration_list, "Workout_Length")
    song_artist_sql = json_search_sql_format(artist_list, "Songs", exclude_artist)

    # Separate Title Box into param variable to protect against an SQL Injection from the text entry box
    # Need to add further SQL Injection prevention for all parameters that could be injected
    query = (
        f"""select * from Cycling_Records where Title LIKE %s {instructor_sql} {song_artist_sql} {difficulty_sql} """
        f"""{duration_sql} {category_sql}  order by Release_Date DESC LIMIT {result_limit} OFFSET {search_index}"""
    )

    param = '%{}%'.format(title_box)
    cursor.execute(query, (param,))
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results)


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
