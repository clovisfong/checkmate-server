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
        data_list = list(data.values())
        debt_name = data["debt_name"]

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
                    cursor.execute("INSERT INTO user_debt (user_details_id, debt_name, debt_type, debt_status, loan_amount, interest_rate, commitment_period_months, start_date, monthly_commitment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", data_list)
                else:
                    cursor.execute(
                        "INSERT INTO user_debt (user_details_id, debt_name, debt_type, debt_status, loan_amount, interest_rate, commitment_period_months, monthly_commitment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data_list)
        return {"msg": f"Successfully created {debt_name}!"}, 201


# GET ALL ROUTE FOR A SPECIFIC USER
@debt.route("/", methods=["GET"])
def get_all_debt():

    if request.method == 'GET':
        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_debt WHERE user_details_id={user_id}")
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
                cursor.execute("UPDATE user_debt SET user_details_id=%s, debt_name=%s, debt_type=%s, debt_status=%s, loan_amount=%s, interest_rate=%s, commitment_period_months=%s, start_date=%s, monthly_commitment=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"Successfully updated {debt_name}!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM user_debt WHERE id= '{id}'")

            return {"msg": f"Successfully deleted"}, 201
