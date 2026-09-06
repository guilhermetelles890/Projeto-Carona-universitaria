import sqlite3
import os
CAMINHO_BANCO = "database/banco.db"

# Criar o diretório se não existir
os.makedirs(os.path.dirname(CAMINHO_BANCO), exist_ok=True)


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

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
            tipo_usuario TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


def cadastrar_usuario(nome, email, senha, telefone, curso, campus, tipo_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO usuarios
        (nome, email, senha, telefone, curso, campus, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, senha, telefone, curso, campus, tipo_usuario))

    conexao.commit()
    conexao.close()

    def criar_tabela_caronas():
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caronas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origem TEXT NOT NULL,
                destino TEXT NOT NULL,
                data_hora DATETIME NOT NULL,
                vagas_disponiveis INTEGER NOT NULL,
                id_usuario INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        """)

        conexao.commit()
        conexao.close()
    criar_tabela_caronas()
criar_tabela_usuarios()