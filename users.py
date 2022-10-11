import os
import psycopg2
from flask import Blueprint, request
import bcrypt
import jwt
from dotenv import load_dotenv


load_dotenv()

users = Blueprint('users', __name__)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)

secret = os.environ.get("SECRET")

# CREATE ROUTE

@users.route("/", methods=["POST"])
def create_user():

    if request.method == 'POST':
        data = request.get_json()

        if len(data["password"]) < 8:
            return {"msg": "Password needs to have at least 8 characters"}, 401
        else:

            pw = data["password"]
            bytes = pw.encode('utf-8')
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(bytes, salt)
            decode_password = password.decode('utf8')
            data["password"] = decode_password
            data_list = list(data.values())
            email = data['email']
            name = data["name"]
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO user_details (name, date_of_birth, gender, email, password) VALUES (%s, %s, %s, %s, %s)", (
                        data_list))
                # check for user data
                    cursor.execute(
                        f"SELECT *, to_char(date_of_birth, 'DD-MM-YYYY') As new_birthdate FROM user_details WHERE email = '{email}'")
                    columns = list(cursor.description)
                    user_result = cursor.fetchone()

                    # Make a dict for user data
                    user_dict = {}
                    for i, col in enumerate(columns):
                        user_dict[col.name] = user_result[i]

                     # Set up payload
                    del user_dict['password']
                    del user_dict['date_of_birth']
                    del user_dict['created_at']
                    del user_dict['updated_at']
                    payload_data = user_dict

                    token = jwt.encode(
                        payload=payload_data,
                        key=secret
                    )
                    return {"token": f"{token}"}, 201


# GET ALL ROUTE
@users.route("/", methods=["GET"])
def get_all_users():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM user_details")
                columns = list(cursor.description)
                result = cursor.fetchall()

                results = []
                for row in result:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col.name] = row[i]
                    del row_dict['password']
                    results.append(row_dict)
            return results, 201


# GET ONE / UPDATE / DELETE ROUTE
@users.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_users(id):

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_details WHERE id= {id}")
                columns = list(cursor.description)
                result = cursor.fetchone()

                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = result[i]
                del row_dict['password']
            return row_dict, 201

    if request.method == 'PUT':
        data = request.get_json()
        with connection:
            with connection.cursor() as cursor:
                if len(data["password"]) >= 8:

                    pw = data["password"]
                    bytes = pw.encode('utf-8')
                    salt = bcrypt.gensalt()
                    password = bcrypt.hashpw(bytes, salt)
                    decode_password = password.decode('utf8')
                    data["password"] = decode_password
                    data_list = list(data.values())
                    data_list.append(id)
                    cursor.execute(
                        "UPDATE user_details SET name=%s, date_of_birth=%s, gender=%s, email=%s, password=%s, retirement_age=%s, retirement_lifestyle=%s, legacy_allocation=%s, life_expectancy=%s  WHERE id=%s",
                        data_list)
                    return {"msg": f"Account updated with id: {id}"}, 201
                else:
                    del data["password"]
                    data_list_old_pw = list(data.values())
                    data_list_old_pw.append(id)
                    cursor.execute(
                        "UPDATE user_details SET name=%s, date_of_birth=%s, gender=%s, email=%s, retirement_age=%s, retirement_lifestyle=%s, legacy_allocation=%s, life_expectancy=%s  WHERE id=%s",
                        data_list_old_pw)
                    return {"msg": f"Account updated with id: {id}"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_details WHERE id= '{id}'")
                result = cursor.fetchall()
                if len(result) == 0:
                    return {"msg": "User not found"}, 401
                else:
                    cursor.execute(
                        f"DELETE FROM user_details WHERE id= '{id}'")
                    return {"msg": f"Deleted Account with id: {id}"}, 201


# USER LOGIN # HOW TO COMPARE
@users.route("/login", methods=["POST"])
def user_login():

    if request.method == 'POST':
        data = request.get_json()
        email = data["email"]
        pw = data["password"]
        bytes = pw.encode('utf-8')

        with connection:
            with connection.cursor() as cursor:
                # check for user data
                cursor.execute(
                    f"SELECT * FROM user_details WHERE email = '{email}'")
                columns = list(cursor.description)
                user_result = cursor.fetchone()

                # Make a dict for user data
                user_dict = {}
                for i, col in enumerate(columns):
                    user_dict[col.name] = user_result[i]

                # Validate password
                decode_password = user_dict['password']
                encode_password = decode_password.encode('utf-8')
                result = bcrypt.checkpw(bytes, encode_password)
                print(str(user_dict['created_at']))
                if result:
                    # Set up payload
                    user_dict['date_of_birth'] = str(user_dict['date_of_birth'])
                    del user_dict['password']
                    del user_dict['created_at']
                    del user_dict['updated_at'] 
                    payload_data = user_dict

                    token = jwt.encode(
                        payload_data,
                        secret,
                        algorithm="HS256"
                    )

                    

                    return {"token": f"{token}"}, 201

                    # decode
                    # test = jwt.decode(token, secret, algorithms=["HS256"])
                    # {'some': 'payload'}
                    # return test, 201
                else:
                    return {"msg": "Password didn't match. Try again."}, 401