import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
import jwt


load_dotenv()

debt = Blueprint('debt', __name__)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)

secret = os.environ.get("SECRET")

# CREATE ROUTE


@debt.route("/", methods=["POST"])
def create_debt():

    if request.method == 'POST':
        data = request.get_json()
        data_values = list(data.values())
        debt_name = data["debt_name"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO user_debt (debt_name, debt_type, debt_status, loan_amount,interest_rate, commitment_period_months, start_date, monthly_commitment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data_values)
        return {"msg": f"{debt_name} created!"}, 201


# GET ALL ROUTE
@debt.route("/", methods=["GET"])
def get_all_debt():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *, to_char(start_date, 'DD-MM-YYYY') As NewDateFormat FROM user_debt")
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
@debt.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_debt(id):

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_debt WHERE id= {id}")
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
        debt_name = data["debt_name"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_debt SET debt_name=%s, debt_type=%s, debt_status=%s, purchase_value=%s, down_payment=%s, loan_amount=%s, interest_rate=%s, commitment_period_months=%s, start_date=%s, monthly_commitment=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"{debt_name} updated!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM user_debt WHERE id= '{id}'")

            return {"msg": f"Deleted debt with id: {id}"}, 201
