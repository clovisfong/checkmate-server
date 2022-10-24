import os
import psycopg2
from flask import Blueprint, request
from flask_cors import CORS
from dotenv import load_dotenv
import jwt


load_dotenv()

all = Blueprint('all', __name__)
CORS(all)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)

secret = os.environ.get("SECRET")

# CREATE ROUTE


@all.route("/", methods=["POST"])
def create_all():

    if request.method == 'POST':
        data = request.get_json()
        print(data[2])
        data[0]["duration_months"] = data[0]["duration_months"]*12
        data[1]["duration_months"] = data[1]["duration_months"]*12
        data[2]["commitment_period_months"] = data[2]["commitment_period_months"]*12
        income_list = list(data[0].values())
        expense_list = list(data[1].values())
        debt_list = list(data[2].values())
        asset_list = list(data[3].values())
        # print(income_list)

        # Decode Token and get User ID
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split()[1]
        user_details = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = user_details['id']

        # Put user id to the front of list
        income_list.insert(0, user_id)
        expense_list.insert(0, user_id)
        debt_list.insert(0, user_id)
        asset_list.insert(0, user_id)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_income (user_details_id, income_name, income_type, income_status, amount,frequency, duration_months, start_date, growth_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", income_list)
                cursor.execute(
                    "INSERT INTO user_expense (user_details_id, expense_name, expense_type, expense_status, amount, frequency, duration_months, start_date, inflation_rate) VALUES (%s, %s, %s,%s,  %s, %s, %s, %s, %s)", (expense_list))
                cursor.execute(
                    "INSERT INTO user_debt (user_details_id, debt_name, debt_type, debt_status, loan_amount, interest_rate, commitment_period_months, start_date, monthly_commitment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", debt_list)
                cursor.execute(
                    "INSERT INTO user_asset (user_details_id, asset_name, asset_type, current_value) VALUES (%s, %s, %s, %s)", (asset_list))
        return {"msg": f"Successfully created!"}, 201
