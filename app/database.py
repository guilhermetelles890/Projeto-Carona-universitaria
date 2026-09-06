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
            id_veiculo INTEGER NOT NULL,
            origem TEXT NOT NULL,
            destino TEXT NOT NULL,
            data_hora_saida DATETIME DEFAULT CURRENT_TIMESTAMP,
            vagas_disponiveis INTEGER NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo)
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


def inicializar_banco():
    criar_tabela_usuarios()
    criar_tabela_trajetos()
    criar_tabela_solicitacoes()


if __name__ == "__main__":
    inicializar_banco()