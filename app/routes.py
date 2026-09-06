from flask import render_template, request, redirect, url_for, session

from app import app
from app.database import cadastrar_usuario, conectar_banco
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

def login_obrigatorio(funcao):
    @wraps(funcao)
    def loginObrigtorio(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)
    return loginObrigtorio

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
        cnh = request.form["cnh"]
        tipo_usuario = request.form["tipo_usuario"]

        senha_hash = generate_password_hash(senha)

        cadastrar_usuario(
            nome,
            email,
            senha_hash,
            telefone,
            curso,
            campus,
            cnh,
            tipo_usuario
        )

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar_banco()

        usuario = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        conexao.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("inicio"))

        return render_template("login_error.html")
    
    return render_template("login.html")

@app.route("/buscar_caronas")
@login_obrigatorio
def buscar_caronas():
    return render_template("buscar_caronas.html")

@app.route("/publicar_carona", methods=["GET", "POST"])
@login_obrigatorio
def publicar_carona():
    return render_template("publicar_carona.html")