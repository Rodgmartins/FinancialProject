import sqlite3

def init_db():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()

    # Criação da tabela "clientes"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT NOT NULL,
            razao_social TEXT NOT NULL,
            nome_fantasia TEXT NOT NULL,
            endereco TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT NOT NULL,
            honorario REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
