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



def criar_tabela_avaliacoes():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_trajeto INTEGER NOT NULL,
            id_avaliador INTEGER NOT NULL,
            id_avaliado INTEGER NOT NULL,
            nota INTEGER NOT NULL,
            comentario TEXT,
            data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (id_trajeto) REFERENCES trajetos (id_trajeto),
            FOREIGN KEY (id_avaliador) REFERENCES usuarios (id),
            FOREIGN KEY (id_avaliado) REFERENCES usuarios (id),
            UNIQUE (id_trajeto, id_avaliador, id_avaliado)
        )
    """)

    conexao.commit()
    conexao.close()



def inicializar_banco():
    criar_tabela_usuarios()
    criar_tabela_trajetos()
    criar_tabela_solicitacoes()
    criar_tabela_avaliacoes()



def cadastrar_usuario(nome, email, senha, telefone, curso, campus, cnh, tipo_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # CNH vazia vira NULL: strings vazias colidem entre si na constraint
    # UNIQUE, mas vários NULLs podem coexistir sem problema.
    cnh = cnh.strip() if cnh else None
    if cnh == "":
        cnh = None

    try:
        cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha, telefone, curso, campus, cnh, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, email, senha, telefone, curso, campus, cnh, tipo_usuario))
        conexao.commit()
    finally:
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
        SELECT trajetos.*, usuarios.nome AS motorista_nome,
               (SELECT AVG(nota) FROM avaliacoes WHERE id_avaliado = trajetos.id_usuario) AS motorista_nota_media,
               (SELECT COUNT(*) FROM avaliacoes WHERE id_avaliado = trajetos.id_usuario) AS motorista_total_avaliacoes
        FROM trajetos
        JOIN usuarios ON trajetos.id_usuario = usuarios.id
        WHERE trajetos.vagas_disponiveis > 0 AND trajetos.status = 'ativo'
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
               usuarios.nome AS passageiro_nome, usuarios.telefone AS passageiro_telefone,
               (SELECT AVG(nota) FROM avaliacoes WHERE id_avaliado = usuarios.id) AS passageiro_nota_media,
               (SELECT COUNT(*) FROM avaliacoes WHERE id_avaliado = usuarios.id) AS passageiro_total_avaliacoes
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


def listar_meus_trajetos(id_usuario):
    conexao = conectar_banco()

    trajetos = conexao.execute("""
        SELECT * FROM trajetos
        WHERE id_usuario = ?
        ORDER BY data_hora_saida DESC
    """, (id_usuario,)).fetchall()

    conexao.close()
    return trajetos


def finalizar_trajeto(id_trajeto):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE trajetos SET status = 'finalizado' WHERE id_trajeto = ?
    """, (id_trajeto,))

    # Quem estava com a vaga confirmada agora pode avaliar e ser avaliado
    cursor.execute("""
        UPDATE solicitacoes SET status = 'concluida'
        WHERE id_trajeto = ? AND status = 'aceita'
    """, (id_trajeto,))

    # Pedidos que nunca foram respondidos perdem o sentido depois que a viagem acabou
    cursor.execute("""
        UPDATE solicitacoes SET status = 'recusada'
        WHERE id_trajeto = ? AND status = 'pendente'
    """, (id_trajeto,))

    conexao.commit()
    conexao.close()


def verificar_participacao_concluida(id_trajeto, id_usuario):
    conexao = conectar_banco()

    participacao = conexao.execute("""
        SELECT 1 FROM solicitacoes
        WHERE id_trajeto = ? AND id_usuario = ? AND status = 'concluida'
    """, (id_trajeto, id_usuario)).fetchone()

    conexao.close()
    return participacao is not None


def verificar_avaliacao_existente(id_trajeto, id_avaliador, id_avaliado):
    conexao = conectar_banco()

    avaliacao = conexao.execute("""
        SELECT 1 FROM avaliacoes
        WHERE id_trajeto = ? AND id_avaliador = ? AND id_avaliado = ?
    """, (id_trajeto, id_avaliador, id_avaliado)).fetchone()

    conexao.close()
    return avaliacao is not None


def criar_avaliacao(id_trajeto, id_avaliador, id_avaliado, nota, comentario):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO avaliacoes (id_trajeto, id_avaliador, id_avaliado, nota, comentario)
            VALUES (?, ?, ?, ?, ?)
        """, (id_trajeto, id_avaliador, id_avaliado, nota, comentario))
        conexao.commit()
    finally:
        conexao.close()


def listar_avaliacoes_pendentes_como_passageiro(id_usuario):
    conexao = conectar_banco()

    pendentes = conexao.execute("""
        SELECT solicitacoes.id_trajeto,
               trajetos.id_usuario AS id_avaliado,
               usuarios.nome AS nome_avaliado,
               trajetos.origem, trajetos.destino, trajetos.data_hora_saida,
               'motorista' AS papel_avaliado
        FROM solicitacoes
        JOIN trajetos ON solicitacoes.id_trajeto = trajetos.id_trajeto
        JOIN usuarios ON trajetos.id_usuario = usuarios.id
        LEFT JOIN avaliacoes
            ON avaliacoes.id_trajeto = solicitacoes.id_trajeto
            AND avaliacoes.id_avaliador = ?
            AND avaliacoes.id_avaliado = trajetos.id_usuario
        WHERE solicitacoes.id_usuario = ?
            AND solicitacoes.status = 'concluida'
            AND avaliacoes.id_avaliacao IS NULL
    """, (id_usuario, id_usuario)).fetchall()

    conexao.close()
    return pendentes


def listar_avaliacoes_pendentes_como_motorista(id_usuario):
    conexao = conectar_banco()

    pendentes = conexao.execute("""
        SELECT solicitacoes.id_trajeto,
               solicitacoes.id_usuario AS id_avaliado,
               usuarios.nome AS nome_avaliado,
               trajetos.origem, trajetos.destino, trajetos.data_hora_saida,
               'passageiro' AS papel_avaliado
        FROM solicitacoes
        JOIN trajetos ON solicitacoes.id_trajeto = trajetos.id_trajeto
        JOIN usuarios ON solicitacoes.id_usuario = usuarios.id
        LEFT JOIN avaliacoes
            ON avaliacoes.id_trajeto = solicitacoes.id_trajeto
            AND avaliacoes.id_avaliador = ?
            AND avaliacoes.id_avaliado = solicitacoes.id_usuario
        WHERE trajetos.id_usuario = ?
            AND solicitacoes.status = 'concluida'
            AND avaliacoes.id_avaliacao IS NULL
    """, (id_usuario, id_usuario)).fetchall()

    conexao.close()
    return pendentes


inicializar_banco()