from flask import render_template, request, redirect, url_for, session, flash
import sqlite3

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
    listar_meus_trajetos,
    finalizar_trajeto,
    verificar_participacao_concluida,
    verificar_avaliacao_existente,
    criar_avaliacao,
    listar_avaliacoes_pendentes_como_passageiro,
    listar_avaliacoes_pendentes_como_motorista,
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

        try:
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
        except sqlite3.IntegrityError as erro:
            if "usuarios.email" in str(erro):
                flash("Já existe uma conta com esse e-mail.")
            elif "usuarios.cnh" in str(erro):
                flash("Essa CNH já está cadastrada em outra conta.")
            else:
                flash("Não foi possível concluir o cadastro. Verifique os dados.")
            return render_template("cadastro.html")

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/meus_trajetos")
@login_obrigatorio
def meus_trajetos():
    trajetos = listar_meus_trajetos(session["usuario_id"])
    return render_template("meus_trajetos.html", trajetos=trajetos)


@app.route("/trajeto/<int:id_trajeto>/encerrar", methods=["POST"])
@login_obrigatorio
def encerrar_trajeto_route(id_trajeto):
    trajeto = buscar_trajeto_por_id(id_trajeto)

    if trajeto is None or trajeto["id_usuario"] != session["usuario_id"]:
        flash("Trajeto não encontrado.")
        return redirect(url_for("meus_trajetos"))

    if trajeto["status"] == "finalizado":
        flash("Essa viagem já foi encerrada.")
        return redirect(url_for("meus_trajetos"))

    finalizar_trajeto(id_trajeto)
    flash("Viagem encerrada! Agora você já pode avaliar os passageiros.")

    return redirect(url_for("meus_trajetos"))


@app.route("/avaliacoes_pendentes")
@login_obrigatorio
def avaliacoes_pendentes():
    pendentes = list(listar_avaliacoes_pendentes_como_passageiro(session["usuario_id"]))
    pendentes += list(listar_avaliacoes_pendentes_como_motorista(session["usuario_id"]))

    return render_template("avaliacoes_pendentes.html", pendentes=pendentes)


@app.route("/avaliar/<int:id_trajeto>/<int:id_avaliado>", methods=["POST"])
@login_obrigatorio
def avaliar_route(id_trajeto, id_avaliado):
    nota = request.form.get("nota")
    comentario = request.form.get("comentario", "").strip()

    if not nota or not nota.isdigit() or not (1 <= int(nota) <= 5):
        flash("Escolha uma nota de 1 a 5 estrelas.")
        return redirect(url_for("avaliacoes_pendentes"))

    nota = int(nota)

    if session["usuario_id"] == id_avaliado:
        flash("Você não pode avaliar a si mesmo.")
        return redirect(url_for("avaliacoes_pendentes"))

    trajeto = buscar_trajeto_por_id(id_trajeto)
    if trajeto is None:
        flash("Trajeto não encontrado.")
        return redirect(url_for("avaliacoes_pendentes"))

    sou_motorista = trajeto["id_usuario"] == session["usuario_id"]

    if sou_motorista:
        if trajeto["status"] != "finalizado":
            flash("Encerre a viagem antes de avaliar os passageiros.")
            return redirect(url_for("meus_trajetos"))
    else:
        participei = verificar_participacao_concluida(id_trajeto, session["usuario_id"])
        if not participei:
            flash("Você não participou dessa viagem.")
            return redirect(url_for("avaliacoes_pendentes"))

    if verificar_avaliacao_existente(id_trajeto, session["usuario_id"], id_avaliado):
        flash("Você já avaliou essa pessoa nessa viagem.")
        return redirect(url_for("avaliacoes_pendentes"))

    criar_avaliacao(id_trajeto, session["usuario_id"], id_avaliado, nota, comentario)
    flash("Avaliação enviada. Obrigado!")

    return redirect(url_for("avaliacoes_pendentes"))


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