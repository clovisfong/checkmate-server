import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv


load_dotenv()

expense = Blueprint('expense', __name__)

url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)


# CREATE ROUTE
@expense.route("/", methods=["POST"])
def create_expense():

    if request.method == 'POST':
        data = request.get_json()
        data_list = list(data.values())
        expense_name = data["expense_name"]

        with connection:
            with connection.cursor() as cursor:
                if data.get("start_date") is not None:
                    cursor.execute(
                        "INSERT INTO user_expense (expense_name, expense_type, expense_status, amount, frequency, duration_months, start_date, inflation_rate) VALUES (%s, %s,%s,  %s, %s, %s, %s, %s)", (
                            data_list))
                else:
                    cursor.execute(
                        "INSERT INTO user_expense (expense_name, expense_type, expense_status, amount, frequency, duration_months, inflation_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)", (
                            data_list))
        return {"msg": f"{expense_name} created!"}, 201


# GET ALL ROUTE
@expense.route("/", methods=["GET"])
def get_all_expense():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM user_expense")
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
        data_list = list(data.values())
        data_list.append(id)
        print(data)
        expense_name = data["expense_name"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_expense SET expense_name= %s, expense_type= %s, expense_status=%s, amount= %s, frequency= %s, duration_months=%s, start_date=%s, inflation_rate=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"{expense_name} updated!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM user_expense WHERE id= %s", (str(id)))

            return {"msg": f"Deleted expense with id: {id}"}, 201
