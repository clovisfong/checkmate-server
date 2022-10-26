import os
import psycopg2
from flask import Blueprint, request
from flask_cors import CORS
import bcrypt
import jwt
from dotenv import load_dotenv


load_dotenv()

users = Blueprint('users', __name__)
CORS(users)
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
                    try:
                        cursor.execute("INSERT INTO user_details (name, date_of_birth, gender, email, password) VALUES (%s, %s, %s, %s, %s)", (
                            data_list))
                    # check for user data
                        cursor.execute(
                            f"SELECT * FROM user_details WHERE email = '{email}'")
                        columns = list(cursor.description)
                        user_result = cursor.fetchone()

                        # Make a dict for user data
                        user_dict = {}
                        for i, col in enumerate(columns):
                            user_dict[col.name] = user_result[i]

                        # Set up payload
                        user_dict['date_of_birth'] = str(
                            user_dict['date_of_birth'])
                        del user_dict['password']
                        del user_dict['created_at']
                        del user_dict['updated_at']
                        payload_data = user_dict

                        token = jwt.encode(
                            payload=payload_data,
                            key=secret
                        )
                        return {"token": f"{token}"}, 201
                    except Exception as error:
                        return {"error": "Email is already in used!"}, 401


# GET ALL ROUTE
@users.route("/", methods=["GET"])
def get_all_users():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                try:
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
                except Exception as error:
                    return {"error": f"{error}"}, 401


# GET ONE / UPDATE / DELETE ROUTE
@users.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_users(id):

    if request.method == 'GET':

     # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_details WHERE id= {user_id}")
                columns = list(cursor.description)
                result = cursor.fetchone()

                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = result[i]
                del row_dict['password']
            return row_dict, 201

    if request.method == 'PUT':
        # get user's input password
        data = request.get_json()
        pw = data["password"]
        bytes = pw.encode('utf-8')

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        with connection:
            with connection.cursor() as cursor:

                # Get user original data
                cursor.execute(
                    f"SELECT * FROM user_details WHERE id= {user_id}")
                columns = list(cursor.description)
                user_result = cursor.fetchone()

                # Make a dict for user data
                user_dict = {}
                for i, col in enumerate(columns):
                    user_dict[col.name] = user_result[i]

                # Validate password to get true or false
                decode_password = user_dict['password']
                encode_password = decode_password.encode('utf-8')
                result = bcrypt.checkpw(bytes, encode_password)

                if result:
                    # add old password and id into data
                    data["password"] = decode_password
                    data_list = list(data.values())
                    email = data['email']
                    data_list.append(id)
                    try:
                        cursor.execute(
                            "UPDATE user_details SET name=%s, date_of_birth=%s, gender=%s, email=%s, password=%s, retirement_age=%s, retirement_lifestyle=%s, legacy_allocation=%s, life_expectancy=%s  WHERE id=%s",
                            data_list)

                        # check for user data
                        cursor.execute(
                            f"SELECT * FROM user_details WHERE email = '{email}'")
                        columns = list(cursor.description)
                        user_result = cursor.fetchone()

                        # Make a dict for user data
                        user_dict = {}
                        for i, col in enumerate(columns):
                            user_dict[col.name] = user_result[i]

                        # Set up payload
                        user_dict['date_of_birth'] = str(
                            user_dict['date_of_birth'])
                        del user_dict['password']
                        del user_dict['created_at']
                        del user_dict['updated_at']
                        payload_data = user_dict

                        token = jwt.encode(
                            payload=payload_data,
                            key=secret
                        )

                        return {"token": f"{token}"}, 201

                    except Exception as error:
                        return {"msg": "Email is already in used!"}, 401

                else:
                    return {"msg": "Password didn't match. Try again."}, 401

    if request.method == 'DELETE':

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        if user_id == id:

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

        else:
            return {"msg": "Not authorized to delete"}, 401


# USER LOGIN
@users.route("/login", methods=["POST"])
def user_login():

    if request.method == 'POST':
        data = request.get_json()
        email = data["email"]
        pw = data["password"]
        bytes = pw.encode('utf-8')
        print(data)
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
                    user_dict['date_of_birth'] = str(
                        user_dict['date_of_birth'])
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


# UPDATE PASSWORD

@users.route("/changepassword/<int:id>", methods=["PUT"])
def change_pw(id):

    if request.method == 'PUT':

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        # get user password
        data = request.get_json()
        old_pw = data["old_password"]
        bytes = old_pw.encode('utf-8')

        new_pw = data["new_password"]
        confirm_pw = data["confirm_password"]

        with connection:
            with connection.cursor() as cursor:

                # Get user original data
                cursor.execute(
                    f"SELECT * FROM user_details WHERE id= {user_id}")
                columns = list(cursor.description)
                user_result = cursor.fetchone()

                # Make a dict for user data
                user_dict = {}
                for i, col in enumerate(columns):
                    user_dict[col.name] = user_result[i]

                # Validate password to get true or false
                decode_password = user_dict['password']
                encode_password = decode_password.encode('utf-8')
                result = bcrypt.checkpw(bytes, encode_password)

                if result:
                    if new_pw == confirm_pw:

                        # hash new password
                        bytes = new_pw.encode('utf-8')
                        salt = bcrypt.gensalt()
                        password = bcrypt.hashpw(bytes, salt)
                        decode_password = password.decode('utf8')

                        user_dict["password"] = decode_password
                        del user_dict['created_at']
                        del user_dict['updated_at']

                        data_list = list(user_dict.values())
                        data_list.pop(0)
                        data_list.append(id)

                        cursor.execute(
                            "UPDATE user_details SET name=%s, date_of_birth=%s, gender=%s, email=%s, password=%s, retirement_age=%s, retirement_lifestyle=%s, legacy_allocation=%s, life_expectancy=%s  WHERE id=%s",
                            data_list)

                        # retrive user new data
                        cursor.execute(
                            f"SELECT * FROM user_details WHERE id= {user_id}")
                        columns = list(cursor.description)
                        user_result = cursor.fetchone()

                        # Make a dict for user new data
                        user_dict = {}
                        for i, col in enumerate(columns):
                            user_dict[col.name] = user_result[i]

                        # Set up payload
                        user_dict['date_of_birth'] = str(
                            user_dict['date_of_birth'])
                        del user_dict['password']
                        del user_dict['created_at']
                        del user_dict['updated_at']
                        payload_data = user_dict

                        token = jwt.encode(
                            payload=payload_data,
                            key=secret
                        )

                        return {"token": f"{token}"}, 201

                    else:
                        return {"msg": "New password didn't match."}, 401

                else:
                    return {"msg": "Old password is wrong. Try again."}, 401
