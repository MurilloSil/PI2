from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'barbershop'

mysql = MySQL(app)

#*Home page

@app.route('/')
def home():
    return render_template('home.html')

#*Sistema de Agendamentos

#**Rotas para busca e deletar agendamentos

@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        search_data = request.form.get('data')
        search_month = request.form.get('mes')
        query = "SELECT id, data, hora, cliente, descricao FROM agendamentos WHERE "
        query_conditions = []
        query_values = []

        if search_data:
            query_conditions.append("data = %s")
            query_values.append(search_data)
        if search_month:
            query_conditions.append("data LIKE %s")
            query_values.append(search_month + '%')

        if query_conditions:
            query += " OR ".join(query_conditions)
        else:
            query += "1=0"  # Não retorna resultados se nenhum filtro for aplicado

        cur.execute(query, query_values)
    else:
        cur.execute("SELECT id, data, hora, cliente, descricao FROM agendamentos WHERE 1=0")  # Não retorna resultados na inicialização
    data = cur.fetchall()
    cur.close()
    return render_template('agendamentos.html', agendamentos=data)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM agendamentos WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('agendamentos'))

#*Gestão de Estoque

#**Rotas para busca, adcionar ou deletar itens no estoque

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        produto = request.form['produto']
        quantidade = request.form['quantidade']
        descricao = request.form['descricao']
        cur.execute("INSERT INTO gestao_estoques (produto, quantidade, descricao) VALUES (%s, %s, %s)", (produto, quantidade, descricao))
        mysql.connection.commit()
    cur.execute("SELECT * FROM gestao_estoques")
    data = cur.fetchall()
    cur.close()
    return render_template('estoque.html', estoques=data)

@app.route('/delete_estoque/<int:id>', methods=['POST'])
def delete_estoque(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM gestao_estoques WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)
