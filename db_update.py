import sqlite3

def update_db():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()

    # Criação da tabela "pagamentos_honorarios" para associar meses e status de pagamento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos_honorarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            pago BOOLEAN NOT NULL DEFAULT 0,
            ano INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')

    # Criação da tabela para armazenar os valores dos honorários por ano
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS honorarios_ano (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            valor REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Criação da tabela "planilha_cadastro" para associar o status das tarefas por cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planilha_cadastro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            credenciamento_sefaz BOOLEAN DEFAULT 0,
            sefaz_sep BOOLEAN DEFAULT 0,
            sped_fiscal BOOLEAN DEFAULT 0,
            dctf_web BOOLEAN DEFAULT 0,
            sat BOOLEAN DEFAULT 0,
            aplicativo BOOLEAN DEFAULT 0,
            procuracao_rfb BOOLEAN DEFAULT 0,
            procuracao_fgts BOOLEAN DEFAULT 0,
            certificado_digital BOOLEAN DEFAULT 0,
            senha_post_fiscal BOOLEAN DEFAULT 0,
            senha_web BOOLEAN DEFAULT 0,
            licenca_pms BOOLEAN DEFAULT 0,
            cadastro_fgts BOOLEAN DEFAULT 0,
            matricula_inss BOOLEAN DEFAULT 0,
            perfil_ccm BOOLEAN DEFAULT 0,
            cadastro_lixo BOOLEAN DEFAULT 0,
            incluir_contabilista BOOLEAN DEFAULT 0,
            incluir_sindicatos BOOLEAN DEFAULT 0,
            destda BOOLEAN DEFAULT 0,
            socios_irpf BOOLEAN DEFAULT 0,
            pis_socios BOOLEAN DEFAULT 0,
            ficha_darf BOOLEAN DEFAULT 0,
            cadastrar_honorarios BOOLEAN DEFAULT 0,
            cadastrar_planilha_darf BOOLEAN DEFAULT 0,
            pasta_suspensa_contrato BOOLEAN DEFAULT 0,
            pasta_suspensa_contabilidade BOOLEAN DEFAULT 0,
            pasta_suspensa_balanco BOOLEAN DEFAULT 0,
            pasta_suspensa_darf BOOLEAN DEFAULT 0,
            livro_57 BOOLEAN DEFAULT 0,
            livro_modelo_6 BOOLEAN DEFAULT 0,
            avisar_dp BOOLEAN DEFAULT 0,
            planilha_setorista BOOLEAN DEFAULT 0,
            rpa_gias BOOLEAN DEFAULT 0,
            notas_fiscais BOOLEAN DEFAULT 0,
            quadro_documentos BOOLEAN DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')

    # Criação da tabela "planilhas" para associar os dados de faturamento por cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planilhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            vendas REAL DEFAULT 0,
            compras REAL DEFAULT 0,
            servicos REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Adiciona a coluna 'ano' na tabela 'pagamentos_honorarios', se ela não existir
    try:
        cursor.execute('''
            ALTER TABLE pagamentos_honorarios ADD COLUMN ano INTEGER
        ''')
    except sqlite3.OperationalError:
        print("A coluna 'ano' já existe na tabela pagamentos_honorarios.")

    # Adiciona a coluna 'whatsapp' na tabela 'clientes', se ela não existir
    try:
        cursor.execute('''
            ALTER TABLE clientes ADD COLUMN whatsapp TEXT
        ''')
    except sqlite3.OperationalError:
        print("A coluna 'whatsapp' já existe na tabela clientes.")

    # Adiciona a coluna 'senha_gov_br' na tabela 'clientes', se ela não existir
    try:
        cursor.execute('''
            ALTER TABLE clientes ADD COLUMN senha_gov_br TEXT
        ''')
    except sqlite3.OperationalError:
        print("A coluna 'senha_gov_br' já existe na tabela clientes.")

    # Adiciona a coluna 'responsavel' na tabela 'clientes', se ela não existir
    try:
        cursor.execute('''
            ALTER TABLE clientes ADD COLUMN responsavel TEXT
        ''')
    except sqlite3.OperationalError:
        print("A coluna 'responsavel' já existe na tabela clientes.")

    # Adicionar uma planilha de cadastro para todas as empresas que ainda não têm uma
    cursor.execute('''
        INSERT INTO planilha_cadastro (cliente_id)
        SELECT id FROM clientes
        WHERE id NOT IN (SELECT cliente_id FROM planilha_cadastro)
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()
