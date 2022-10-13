import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
import jwt

load_dotenv()

expense = Blueprint('expense', __name__)

url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)

secret = os.environ.get("SECRET")

# CREATE ROUTE


@expense.route("/", methods=["POST"])
def create_expense():

    if request.method == 'POST':
        data = request.get_json()
        data["duration_months"] = data["duration_months"]*12
        data_list = list(data.values())
        expense_name = data["expense_name"]

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        # Put user id to the front of list
        data_list.insert(0, user_id)
        print(data_list)

        with connection:
            with connection.cursor() as cursor:
                if data.get("start_date") is not None:
                    cursor.execute(
                        "INSERT INTO user_expense (user_details_id, expense_name, expense_type, expense_status, amount, frequency, duration_months, start_date, inflation_rate) VALUES (%s, %s, %s,%s,  %s, %s, %s, %s, %s)", (
                            data_list))
                else:
                    cursor.execute(
                        "INSERT INTO user_expense (user_details_id, expense_name, expense_type, expense_status, amount, frequency, duration_months, inflation_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
                            data_list))
        return {"msg": f"Successfully created {expense_name}!"}, 201


# GET ALL ROUTE FOR A SPECIFIC USER
@expense.route("/", methods=["GET"])
def get_all_expense():

    if request.method == 'GET':
        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_expense WHERE user_details_id={user_id}")
                columns = list(cursor.description)
                result = cursor.fetchall()

                results = []
                for row in result:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col.name] = row[i]
                    results.append(row_dict)
            return results, 201


# # GET ONE / UPDATE / DELETE ROUTE
@expense.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_expense(id):

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_expense WHERE id= {id}")
                columns = list(cursor.description)
                result = cursor.fetchone()

                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = result[i]

            return row_dict, 201

    if request.method == 'PUT':
        data = request.get_json()
        data["duration_months"] = data["duration_months"]*12
        data_list = list(data.values())
        data_list.append(id)
        print(data)
        expense_name = data["expense_name"]

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        # Put user id to the front of list
        data_list.insert(0, user_id)
        print(data_list)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_expense SET user_details_id=%s, expense_name= %s, expense_type= %s, expense_status=%s, amount= %s, frequency= %s, duration_months=%s, start_date=%s, inflation_rate=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"Successfully updated{expense_name}!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM user_expense WHERE id= '{id}'")

            return {"msg": f"Successfully deleted"}, 201
