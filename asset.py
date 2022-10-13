import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
import jwt


load_dotenv()

asset = Blueprint('asset', __name__)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)

secret = os.environ.get("SECRET")

# CREATE ROUTE


@asset.route("/", methods=["POST"])
def create_asset():

    if request.method == 'POST':
        data = request.get_json()
        data_list = list(data.values())
        asset_name = data["asset_name"]

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
                cursor.execute("INSERT INTO user_asset (user_details_id, asset_name, asset_type, current_value) VALUES (%s, %s, %s, %s)", (
                    data_list))
        return {"msg": f"Successfully created {asset_name}!"}, 201


# GET ALL ROUTE
@asset.route("/", methods=["GET"])
def get_all_asset():

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM user_asset")
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
@asset.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_asset(id):

    if request.method == 'GET':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM user_asset WHERE id= {id}")
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
        asset_name = data["asset_name"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_asset SET asset_name=%s, asset_type=%s, current_value=%s WHERE id = %s", (
                    data_list))
        return {"msg": f"{asset_name} updated!"}, 201

    if request.method == 'DELETE':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM user_asset WHERE id= '{id}'")

            return {"msg": f"Deleted asset with id: {id}"}, 201
