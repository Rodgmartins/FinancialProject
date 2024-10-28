import sqlite3

def verificar_colunas():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()

    # Verificar as colunas da tabela 'clientes'
    cursor.execute("PRAGMA table_info(clientes)")
    colunas = cursor.fetchall()

    print("Colunas da tabela 'clientes':")
    for coluna in colunas:
        print(f"{coluna[1]}")

    conn.close()

def adicionar_coluna_responsavel():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()

    # Verificar se a coluna 'responsavel' já existe
    cursor.execute("PRAGMA table_info(clientes)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    
    if 'responsavel' not in colunas:
        try:
            # Adicionar a coluna 'responsavel' se não existir
            cursor.execute('''
                ALTER TABLE clientes ADD COLUMN responsavel TEXT
            ''')
            print("Coluna 'responsavel' adicionada com sucesso.")
        except sqlite3.OperationalError as e:
            print(f"Erro ao adicionar a coluna 'responsavel': {e}")
    else:
        print("A coluna 'responsavel' já existe.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Verificar as colunas da tabela 'clientes'
    verificar_colunas()
    
    # Adicionar a coluna 'responsavel' se necessário
    adicionar_coluna_responsavel()
