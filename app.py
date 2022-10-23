from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from users import users
from income import income
from expense import expense
from debt import debt
from asset import asset
# from all import all
import os
import psycopg2

load_dotenv()


app = Flask(__name__)
CORS(app)

app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(income, url_prefix='/income')
app.register_blueprint(expense, url_prefix='/expense')
app.register_blueprint(debt, url_prefix='/debt')
app.register_blueprint(asset, url_prefix='/asset')
# app.register_blueprint(all, url_prefix='/all')

url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)


@app.route('/')
def home():
    return {"home": "This is the homepage"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")
