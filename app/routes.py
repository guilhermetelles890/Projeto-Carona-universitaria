from flask import render_template, request, redirect, url_for, session, flash

from app import app
from app.database import (
    cadastrar_usuario,
    conectar_banco,
    cadastrar_trajeto,
    listar_trajetos,
    buscar_trajeto_por_id,
    buscar_solicitacao_existente,
    criar_solicitacao,
    buscar_solicitacao_por_id,
    listar_solicitacoes_recebidas,
    listar_minhas_solicitacoes,
    aceitar_solicitacao,
    recusar_solicitacao,
)
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
    trajetos = listar_trajetos()

    # Monta um dicionário {id_trajeto: status} com as solicitações que o
    # próprio usuário logado já fez, para exibir o status correto no botão
    minhas_solicitacoes = listar_minhas_solicitacoes(session["usuario_id"])
    status_por_trajeto = {
        s["id_trajeto"]: s["status"]
        for s in minhas_solicitacoes
        if s["status"] in ("pendente", "aceita")
    }

    return render_template(
        "buscar_caronas.html",
        trajetos=trajetos,
        status_por_trajeto=status_por_trajeto,
    )


@app.route("/solicitar_carona/<int:id_trajeto>", methods=["POST"])
@login_obrigatorio
def solicitar_carona(id_trajeto):
    trajeto = buscar_trajeto_por_id(id_trajeto)

    if trajeto is None:
        flash("Essa carona não existe mais.")
        return redirect(url_for("buscar_caronas"))

    if trajeto["id_usuario"] == session["usuario_id"]:
        flash("Você não pode solicitar uma vaga na sua própria carona.")
        return redirect(url_for("buscar_caronas"))

    if trajeto["vagas_disponiveis"] <= 0:
        flash("Essa carona não tem mais vagas disponíveis.")
        return redirect(url_for("buscar_caronas"))

    ja_existe = buscar_solicitacao_existente(id_trajeto, session["usuario_id"])
    if ja_existe:
        flash("Você já solicitou essa carona.")
        return redirect(url_for("buscar_caronas"))

    criar_solicitacao(id_trajeto, session["usuario_id"])
    flash("Solicitação enviada! Aguarde o motorista aceitar.")

    return redirect(url_for("buscar_caronas"))


@app.route("/minhas_solicitacoes")
@login_obrigatorio
def minhas_solicitacoes():
    solicitacoes = listar_minhas_solicitacoes(session["usuario_id"])
    return render_template("minhas_solicitacoes.html", solicitacoes=solicitacoes)


@app.route("/solicitacoes_recebidas")
@login_obrigatorio
def solicitacoes_recebidas():
    solicitacoes = listar_solicitacoes_recebidas(session["usuario_id"])
    return render_template("solicitacoes_recebidas.html", solicitacoes=solicitacoes)


@app.route("/solicitacao/<int:id_solicitacao>/aceitar", methods=["POST"])
@login_obrigatorio
def aceitar_solicitacao_route(id_solicitacao):
    solicitacao = buscar_solicitacao_por_id(id_solicitacao)

    if solicitacao is None or solicitacao["id_motorista"] != session["usuario_id"]:
        flash("Solicitação não encontrada.")
        return redirect(url_for("solicitacoes_recebidas"))

    if solicitacao["status"] != "pendente":
        flash("Essa solicitação já foi respondida.")
        return redirect(url_for("solicitacoes_recebidas"))

    if solicitacao["vagas_disponiveis"] <= 0:
        flash("Não há mais vagas disponíveis nessa carona.")
        return redirect(url_for("solicitacoes_recebidas"))

    aceitar_solicitacao(id_solicitacao)
    flash("Solicitação aceita!")

    return redirect(url_for("solicitacoes_recebidas"))


@app.route("/solicitacao/<int:id_solicitacao>/recusar", methods=["POST"])
@login_obrigatorio
def recusar_solicitacao_route(id_solicitacao):
    solicitacao = buscar_solicitacao_por_id(id_solicitacao)

    if solicitacao is None or solicitacao["id_motorista"] != session["usuario_id"]:
        flash("Solicitação não encontrada.")
        return redirect(url_for("solicitacoes_recebidas"))

    if solicitacao["status"] != "pendente":
        flash("Essa solicitação já foi respondida.")
        return redirect(url_for("solicitacoes_recebidas"))

    recusar_solicitacao(id_solicitacao)
    flash("Solicitação recusada.")

    return redirect(url_for("solicitacoes_recebidas"))

@app.route("/publicar_carona", methods=["GET", "POST"])
@login_obrigatorio
def publicar_carona():
    if request.method == "POST":
        origem = request.form["origem"]
        destino = request.form["destino"]
        data = request.form["data"]
        hora = request.form["hora"]
        vagas_disponiveis = request.form["vagas_disponiveis"]

        cadastrar_trajeto(
            session["usuario_id"],
            origem,
            destino,
            data,
            hora,
            vagas_disponiveis
        )

        return redirect(url_for("buscar_caronas"))

    return render_template("publicar_carona.html")