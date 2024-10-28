from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('clientes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rota para a página principal, exibindo empresas já cadastradas
@app.route('/')
def index():
    conn = get_db_connection()
    empresas = conn.execute('SELECT id, razao_social, cnpj FROM clientes').fetchall()
    conn.close()
    return render_template('index.html', empresas=empresas)

# Rota para o cadastro de clientes
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    return render_template('cadastro.html')

# Rota para processar o cadastro de clientes
@app.route('/processar', methods=['POST'])
def processar():
    cnpj = request.form['cnpj']
    razao_social = request.form['razao_social']
    nome_fantasia = request.form['nome_empresa']
    endereco = request.form['endereco']
    telefone = request.form['telefone']
    email = request.form['email']
    honorario = request.form['honorario']

    # Inserindo os dados no banco de dados
    conn = get_db_connection()
    conn.execute('INSERT INTO clientes (cnpj, razao_social, nome_fantasia, endereco, telefone, email, honorario) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (cnpj, razao_social, nome_fantasia, endereco, telefone, email, honorario))
    
    # Recupera o ID da empresa recém-criada
    cliente_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    # Cria uma entrada na planilha de cadastro associada à nova empresa
    conn.execute('INSERT INTO planilha_cadastro (cliente_id) VALUES (?)', (cliente_id,))
    
    conn.commit()
    conn.close()

    # Redireciona de volta para a página de cadastro
    return redirect(url_for('cadastro'))

# Rota para buscar dados do CNPJ via API da ReceitaWS
@app.route('/buscar_cnpj', methods=['POST'])
def buscar_cnpj():
    cnpj = request.form['cnpj'].strip()

    # Verifique se o CNPJ tem 14 dígitos
    if len(cnpj) != 14:
        return jsonify({'error': 'CNPJ inválido'}), 400

    url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        if dados.get('status') == 'OK':
            return jsonify({
                'nome': dados.get('nome'),
                'endereco': dados.get('logradouro'),
                'telefone': dados.get('telefone'),
                'email': dados.get('email'),
                'cep': dados.get('cep'),
                'cidade': dados.get('municipio'),
                'estado': dados.get('uf')
            })
        else:
            return jsonify({'error': 'Dados não encontrados'}), 404
    else:
        return jsonify({'error': 'Falha ao buscar dados'}), 500

# Rota para exibir e atualizar os honorários
@app.route('/honorarios', methods=['GET', 'POST'])
def honorarios():
    conn = get_db_connection()

    # Processar os pagamentos e ano selecionado
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        mes = request.form['mes']
        ano = request.form['ano']
        pago = request.form.get('pago') == 'on'

        # Verifica se já existe um registro para o mês, ano e cliente
        cursor = conn.execute('SELECT * FROM pagamentos_honorarios WHERE cliente_id = ? AND mes = ? AND ano = ?', (cliente_id, mes, ano))
        result = cursor.fetchone()

        if result:
            # Atualiza o status de pagamento
            conn.execute('UPDATE pagamentos_honorarios SET pago = ? WHERE cliente_id = ? AND mes = ? AND ano = ?',
                         (pago, cliente_id, mes, ano))
        else:
            # Insere novo registro de pagamento
            conn.execute('INSERT INTO pagamentos_honorarios (cliente_id, mes, ano, pago) VALUES (?, ?, ?, ?)',
                         (cliente_id, mes, ano, pago))

        conn.commit()

        return jsonify({'status': 'success'})

    # Recupera o ano selecionado (ou 2024 como padrão)
    ano_selecionado = request.args.get('ano', '2024')

    # Recupera todos os clientes
    clientes = conn.execute('SELECT id, nome_fantasia FROM clientes').fetchall()

    # Recupera pagamentos por cliente, mês e ano
    honorarios = []
    meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    for cliente in clientes:
        pagamentos = {mes: False for mes in meses}
        pagamentos_cliente = conn.execute('SELECT mes, pago FROM pagamentos_honorarios WHERE cliente_id = ? AND ano = ?', (cliente['id'], ano_selecionado)).fetchall()
        for pagamento in pagamentos_cliente:
            pagamentos[pagamento['mes']] = pagamento['pago']
        honorarios.append({
            'id': cliente['id'],
            'nome_fantasia': cliente['nome_fantasia'],
            **pagamentos
        })

    conn.close()

    anos = ['2022', '2023', '2024']  # Anos disponíveis
    return render_template('honorarios.html', honorarios=honorarios, meses=meses, anos=anos, ano_selecionado=ano_selecionado)

# Rota para autocomplete (pesquisa dinâmica)
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    termo = request.args.get('query', '')

    conn = get_db_connection()
    empresas = conn.execute('''
        SELECT id, nome_fantasia, cnpj FROM clientes
        WHERE nome_fantasia LIKE ? OR cnpj LIKE ?
    ''', ('%' + termo + '%', '%' + termo + '%')).fetchall()
    conn.close()

    resultados = [{'id': empresa['id'], 'nome_fantasia': empresa['nome_fantasia'], 'cnpj': empresa['cnpj']} for empresa in empresas]

    return jsonify(resultados)

# Rota para editar empresa
@app.route('/editar_empresa/<int:cliente_id>')
def editar_empresa(cliente_id):
    conn = get_db_connection()
    empresa = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    conn.close()
    if empresa:
        return render_template('editar_empresa.html', empresa=empresa)
    else:
        return "Empresa não encontrada."

# Rota para processar a atualização dos dados da empresa
@app.route('/atualizar_empresa/<int:cliente_id>', methods=['POST'])
def atualizar_empresa(cliente_id):
    cnpj = request.form['cnpj']
    razao_social = request.form['razao_social']
    nome_fantasia = request.form['nome_empresa']
    endereco = request.form['endereco']
    telefone = request.form['telefone']
    whatsapp = request.form['whatsapp']
    email = request.form['email']
    responsavel = request.form['responsavel']
    senha_gov_br = request.form['senha_gov_br']
    honorario = request.form['honorario']

    conn = get_db_connection()
    conn.execute('''
        UPDATE clientes
        SET cnpj = ?, razao_social = ?, nome_fantasia = ?, endereco = ?, telefone = ?, whatsapp = ?, email = ?, responsavel = ?, senha_gov_br = ?, honorario = ?
        WHERE id = ?
    ''', (cnpj, razao_social, nome_fantasia, endereco, telefone, whatsapp, email, responsavel, senha_gov_br, honorario, cliente_id))
    conn.commit()
    conn.close()

    return redirect(url_for('exibir_empresa', cliente_id=cliente_id))

# Rota para exibir os dados da empresa
@app.route('/empresa/<int:cliente_id>')
def exibir_empresa(cliente_id):
    conn = get_db_connection()
    empresa = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    planilha = conn.execute('SELECT * FROM planilha_cadastro WHERE cliente_id = ?', (cliente_id,)).fetchone()
    conn.close()

    if empresa and planilha:
        return render_template('exibir_empresa.html', empresa=empresa, planilha=planilha)
    else:
        return "Empresa ou planilha não encontrada."

# Rota para selecionar uma empresa para acessar a planilha
@app.route('/planilhas')
def selecionar_cliente_planilhas():
    conn = get_db_connection()
    empresas = conn.execute('SELECT id, razao_social, cnpj FROM clientes').fetchall()
    conn.close()
    return render_template('selecionar_empresa_planilha.html', empresas=empresas)

# Rota para exibir e salvar planilhas de uma empresa específica
@app.route('/planilhas/<int:cliente_id>', methods=['GET', 'POST'])
def planilhas(cliente_id):
    conn = get_db_connection()

    # Recuperar os dados da empresa
    empresa = conn.execute('SELECT razao_social, cnpj FROM clientes WHERE id = ?', (cliente_id,)).fetchone()

    # Lista dos meses do ano
    meses = [
        {'mes': 'Janeiro', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Fevereiro', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Março', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Abril', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Maio', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Junho', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Julho', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Agosto', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Setembro', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Outubro', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Novembro', 'vendas': 0, 'compras': 0, 'servicos': 0},
        {'mes': 'Dezembro', 'vendas': 0, 'compras': 0, 'servicos': 0}
    ]

    if request.method == 'POST':
        # Iterar sobre os meses e salvar os valores de vendas, compras e serviços
        for mes in meses:
            vendas = request.form.get(f'{mes["mes"]}_vendas', 0)
            compras = request.form.get(f'{mes["mes"]}_compras', 0)
            servicos = request.form.get(f'{mes["mes"]}_servicos', 0)

            # Inserir ou atualizar os dados da planilha no banco de dados
            conn.execute('''
                INSERT OR REPLACE INTO planilhas (cliente_id, mes, vendas, compras, servicos)
                VALUES (?, ?, ?, ?, ?)
            ''', (cliente_id, mes['mes'], vendas, compras, servicos))

        conn.commit()
        conn.close()

        return redirect(url_for('planilhas', cliente_id=cliente_id))

    # Recuperar os dados da planilha para exibir
    planilhas = conn.execute('SELECT * FROM planilhas WHERE cliente_id = ?', (cliente_id,)).fetchall()
    conn.close()

    # Atualizar os meses com os valores salvos
    for mes in meses:
        dados_mes = next((p for p in planilhas if p['mes'] == mes['mes']), {'vendas': 0, 'compras': 0, 'servicos': 0})
        mes.update({
            'vendas': dados_mes['vendas'],
            'compras': dados_mes['compras'],
            'servicos': dados_mes['servicos']
        })

    return render_template('planilhas.html', empresa=empresa, meses=meses)

# Rota para a página de planilha de cadastro de uma empresa específica
@app.route('/planilha_cadastro/<int:cliente_id>', methods=['GET', 'POST'])
def planilha_cadastro(cliente_id):
    conn = get_db_connection()

    # Recuperar os dados da empresa para exibição no topo
    empresa = conn.execute('SELECT razao_social, cnpj FROM clientes WHERE id = ?', (cliente_id,)).fetchone()

    if request.method == 'POST':
        # Lista de campos permitidos para atualização
        campos_permitidos = [
            'credenciamento_sefaz', 'sefaz_sep', 'sped_fiscal', 'dctf_web', 'sat', 'aplicativo',
            'procuracao_rfb', 'procuracao_fgts', 'certificado_digital', 'senha_post_fiscal',
            'senha_web', 'licenca_pms', 'cadastro_fgts', 'matricula_inss', 'perfil_ccm',
            'cadastro_lixo', 'incluir_contabilista', 'incluir_sindicatos', 'destda',
            'socios_irpf', 'pis_socios', 'ficha_darf', 'cadastrar_honorarios', 'cadastrar_planilha_darf',
            'pasta_suspensa_contrato', 'pasta_suspensa_contabilidade', 'pasta_suspensa_balanco',
            'pasta_suspensa_darf', 'livro_57', 'livro_modelo_6', 'avisar_dp', 'planilha_setorista',
            'rpa_gias', 'notas_fiscais', 'quadro_documentos'
        ]
        
        # Atualizar o status das tarefas na planilha de cadastro
        for campo in request.form:
            if campo in campos_permitidos:
                valor = request.form.get(campo) == 'on'
                conn.execute(f'''
                    UPDATE planilha_cadastro SET {campo} = ? WHERE cliente_id = ?
                ''', (valor, cliente_id))

        conn.commit()
        return jsonify({'status': 'success'})

    # Recuperar a planilha de cadastro para a empresa
    planilha = conn.execute('SELECT * FROM planilha_cadastro WHERE cliente_id = ?', (cliente_id,)).fetchone()
    conn.close()

    if planilha:
        return render_template('planilha_cadastro.html', planilha=planilha, empresa=empresa)
    else:
        return "Planilha de cadastro não encontrada."

if __name__ == '__main__':
    app.run(debug=True)
