import sqlite3

conexao = sqlite3.connect('banco.db')

conexao.execute("PRAGMA foreign_keys = ON")

cursor = conexao.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS motoristas (
                    id_motorista INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    cnh TEXT NOT NULL UNIQUE,
                    data_cadastro TEXT NOT NULL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS passageiros (
                    id_passageiro INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    telefone TEXT NOT NULL UNIQUE,
                    curso TEXT NOT NULL,
                    campos TEXT NOT NULL,
                    data_cadastro TEXT NOT NULL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_motorista INTEGER NOT NULL,
                    placa TEXT NOT NULL UNIQUE,
                    modelo TEXT NOT NULL,
                    cor TEXT NOT NULL UNIQUE,
                    capacidade INTEGER NOT NULL,

                    FOREIGN KEY (id_motorista) REFERENCES motoristas(id_motorista)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trajetos (
                    id_trajeto INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_motorista INTEGER NOT NULL,
                    id_veiculo INTEGER NOT NULL,
                    origem TEXT NOT NULL ,
                    destino TEXT NOT NULL,
                    data_hora_saida TEXT NOT NULL,
                    vagas_disponiveis INTEGER NOT NULL,
                    status TEXT NOT NULL,

                    FOREIGN KEY (id_motorista) REFERENCES motoristas(id_motorista),
                    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS solicitacoes (
                    id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_trajeto INTEGER NOT NULL,
                    id_passageiro INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    data_solicitacao INTEGER NOT NULL,

                    FOREIGN KEY (id_trajeto) REFERENCES trajetos(id_trajeto),
                    FOREIGN KEY (id_passageiro) REFERENCES passageiros(id_passageiro)
                )''')

conexao.commit()
conexao.close()