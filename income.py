import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv


load_dotenv()

income = Blueprint('income', __name__)
# CORS(income)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)


# CREATE ROUTE
@income.route("/", methods=["POST"])
def create_income():

    if request.method == 'POST':
        data = request.get_json()
        data_values = list(data.values())
        income_name = data["income_name"]

        with connection:
            with connection.cursor() as cursor:
                if data.get("start_date") is not None:
                    cursor.execute(
                        "INSERT INTO user_income (income_name, income_type, income_status, amount,frequency, duration_months, start_date, growth_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data_values)
                else:
                    cursor.execute(
                        "INSERT INTO user_income (income_name, income_type, income_status, amount,frequency, duration_months, growth_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)", data_values)
        return {"msg": f"{income_name} created!"}, 201


# GET ALL ROUTE
@income.route("/", methods=["GET"])
def get_all_income():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM user_income")
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
@income.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_income(id):

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_income WHERE id= {id}")
                columns = list(cursor.description)
                result = cursor.fetchone()
                print(result)
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = result[i]
            return row_dict, 201

    if request.method == 'PUT':
        data = request.get_json()
        data_list = list(data.values())
        data_list.append(id)
        income_name = data["income_name"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_income SET income_name= %s, income_type= %s, income_status=%s, amount= %s, frequency= %s, duration_months=%s, start_date=%s, growth_rate=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"{income_name} updated!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM user_income WHERE id= %s", (str(id)))

            return {"msg": f"Deleted income with id: {id}"}, 201
