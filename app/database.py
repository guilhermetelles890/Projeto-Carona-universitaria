import sqlite3
import os

CAMINHO_BANCO = "database/banco.db"

# Criar o diretório se não existir
os.makedirs(os.path.dirname(CAMINHO_BANCO), exist_ok=True)


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_tabela_usuarios():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            telefone TEXT NOT NULL,
            curso TEXT NOT NULL,
            campus TEXT NOT NULL,
            cnh TEXT UNIQUE,
            tipo_usuario TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


def criar_tabela_trajetos():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trajetos (
            id_trajeto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            origem TEXT NOT NULL,
            destino TEXT NOT NULL,
            data_hora_saida DATETIME DEFAULT CURRENT_TIMESTAMP,
            vagas_disponiveis INTEGER NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    """)

    conexao.commit()
    conexao.close()


def criar_tabela_solicitacoes():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes (
            id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_trajeto INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            status TEXT NOT NULL,
            data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (id_trajeto) REFERENCES trajetos (id_trajeto),
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    """)

    conexao.commit()
    conexao.close()



def inicializar_banco():
    criar_tabela_usuarios()
    criar_tabela_trajetos()
    criar_tabela_solicitacoes()



def cadastrar_usuario(nome, email, senha, telefone, curso, campus, cnh, tipo_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO usuarios
        (nome, email, senha, telefone, curso, campus, cnh, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, senha, telefone, curso, campus, cnh, tipo_usuario))

    conexao.commit()
    conexao.close()
def cadastrar_trajeto(id_usuario, origem, destino, data, hora, vagas_disponiveis):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    data_hora_saida = data + " " + hora

    cursor.execute("""
        INSERT INTO trajetos
        (id_usuario, origem, destino, data_hora_saida, vagas_disponiveis, status)
        VALUES (?, ?, ?, ?, ?, 'ativo')
    """, (id_usuario, origem, destino, data_hora_saida, vagas_disponiveis))

    conexao.commit()
    conexao.close()

def listar_trajetos():
    conexao = conectar_banco()

    trajetos = conexao.execute("""
        SELECT trajetos.*, usuarios.nome AS motorista_nome
        FROM trajetos
        JOIN usuarios ON trajetos.id_usuario = usuarios.id
        WHERE trajetos.vagas_disponiveis > 0
        ORDER BY trajetos.data_hora_saida
    """).fetchall()

    conexao.close()
    return trajetos


def buscar_trajeto_por_id(id_trajeto):
    conexao = conectar_banco()

    trajeto = conexao.execute("""
        SELECT * FROM trajetos WHERE id_trajeto = ?
    """, (id_trajeto,)).fetchone()

    conexao.close()
    return trajeto


def buscar_solicitacao_existente(id_trajeto, id_usuario):
    conexao = conectar_banco()

    solicitacao = conexao.execute("""
        SELECT * FROM solicitacoes
        WHERE id_trajeto = ? AND id_usuario = ? AND status IN ('pendente', 'aceita')
    """, (id_trajeto, id_usuario)).fetchone()

    conexao.close()
    return solicitacao


def criar_solicitacao(id_trajeto, id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO solicitacoes (id_trajeto, id_usuario, status)
        VALUES (?, ?, 'pendente')
    """, (id_trajeto, id_usuario))

    conexao.commit()
    conexao.close()


def buscar_solicitacao_por_id(id_solicitacao):
    conexao = conectar_banco()

    solicitacao = conexao.execute("""
        SELECT solicitacoes.*, trajetos.id_usuario AS id_motorista,
               trajetos.vagas_disponiveis, trajetos.origem, trajetos.destino
        FROM solicitacoes
        JOIN trajetos ON solicitacoes.id_trajeto = trajetos.id_trajeto
        WHERE solicitacoes.id_solicitacao = ?
    """, (id_solicitacao,)).fetchone()

    conexao.close()
    return solicitacao


def listar_solicitacoes_recebidas(id_usuario_motorista):
    conexao = conectar_banco()

    solicitacoes = conexao.execute("""
        SELECT solicitacoes.*, trajetos.origem, trajetos.destino,
               trajetos.data_hora_saida, trajetos.vagas_disponiveis,
               usuarios.nome AS passageiro_nome, usuarios.telefone AS passageiro_telefone
        FROM solicitacoes
        JOIN trajetos ON solicitacoes.id_trajeto = trajetos.id_trajeto
        JOIN usuarios ON solicitacoes.id_usuario = usuarios.id
        WHERE trajetos.id_usuario = ?
        ORDER BY (solicitacoes.status = 'pendente') DESC, solicitacoes.data_solicitacao DESC
    """, (id_usuario_motorista,)).fetchall()

    conexao.close()
    return solicitacoes


def listar_minhas_solicitacoes(id_usuario):
    conexao = conectar_banco()

    solicitacoes = conexao.execute("""
        SELECT solicitacoes.*, trajetos.origem, trajetos.destino,
               trajetos.data_hora_saida, usuarios.nome AS motorista_nome,
               usuarios.telefone AS motorista_telefone
        FROM solicitacoes
        JOIN trajetos ON solicitacoes.id_trajeto = trajetos.id_trajeto
        JOIN usuarios ON trajetos.id_usuario = usuarios.id
        WHERE solicitacoes.id_usuario = ?
        ORDER BY solicitacoes.data_solicitacao DESC
    """, (id_usuario,)).fetchall()

    conexao.close()
    return solicitacoes


def aceitar_solicitacao(id_solicitacao):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE solicitacoes SET status = 'aceita' WHERE id_solicitacao = ?
    """, (id_solicitacao,))

    cursor.execute("""
        SELECT id_trajeto FROM solicitacoes WHERE id_solicitacao = ?
    """, (id_solicitacao,))
    id_trajeto = cursor.fetchone()["id_trajeto"]

    cursor.execute("""
        UPDATE trajetos
        SET vagas_disponiveis = vagas_disponiveis - 1
        WHERE id_trajeto = ? AND vagas_disponiveis > 0
    """, (id_trajeto,))

    cursor.execute("""
        SELECT vagas_disponiveis FROM trajetos WHERE id_trajeto = ?
    """, (id_trajeto,))
    vagas_restantes = cursor.fetchone()["vagas_disponiveis"]

    if vagas_restantes <= 0:
        cursor.execute("""
            UPDATE trajetos SET status = 'lotado' WHERE id_trajeto = ?
        """, (id_trajeto,))

        cursor.execute("""
            UPDATE solicitacoes SET status = 'recusada'
            WHERE id_trajeto = ? AND status = 'pendente'
        """, (id_trajeto,))

    conexao.commit()
    conexao.close()


def recusar_solicitacao(id_solicitacao):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE solicitacoes SET status = 'recusada' WHERE id_solicitacao = ?
    """, (id_solicitacao,))

    conexao.commit()
    conexao.close()


inicializar_banco()