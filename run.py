from app import app
import sqlite3

conexao = sqlite3.connect('banco.db')
cursor = conexao.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL
                )''')

cursor.execute('''INSERT INTO usuarios (nome) VALUES ('Matheus')''')

conexao.commit()
conexao.close()

if __name__ == "__main__":
    app.run(debug=True)