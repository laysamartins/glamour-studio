import sqlite3

CAMINHO_BANCO = "glamour.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            duracao INTEGER NOT NULL
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,

            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (servico_id) REFERENCES servicos(id),

            UNIQUE(data, horario)
        )
    """)

    conexao.commit()
    conexao.close()