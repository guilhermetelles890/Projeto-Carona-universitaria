from flask import render_template

from app import app


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/login")
def login():
    return render_template("login.html")