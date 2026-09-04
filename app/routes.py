from flask import render_template, request, redirect, url_for

from app import app
from app.database import cadastrar_usuario
from werkzeug.security import generate_password_hash


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        telefone = request.form["telefone"]
        curso = request.form["curso"]
        campus = request.form["campus"]
        tipo_usuario = request.form["tipo_usuario"]

        senha_hash = generate_password_hash(senha)

        cadastrar_usuario(
            nome,
            email,
            senha_hash,
            telefone,
            curso,
            campus,
            tipo_usuario
        )

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login")
def login():
    return render_template("login.html")