from flask import Flask

app = Flask(__name__)
app.secret_key = "senha ultrasecreta"

from app import routes