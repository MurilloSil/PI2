from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#*Configuração do Banco de dados

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'barbershop'

mysql = MySQL(app)

#*Rotas para Login, registrar e criar agendamentos

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('agendamentos'))
        else:
            flash('Nome de usuário ou senha incorretos!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            flash('Conta já existe!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Nome de usuário deve conter apenas caracteres e números!', 'danger')
        elif not username or not password:
            flash('Por favor, preencha o formulário!', 'danger')
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password,))
            mysql.connection.commit()
            flash('Você se registrou com sucesso!', 'success')
    return render_template('register.html')

'''@app.route('/logout') #Rota será utilizada somente se houver logout da conta
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))'''

@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    if request.method == 'POST':
        data = request.form['data']
        hora = request.form['hora']
        descricao = request.form['descricao']
        cliente = request.form['cliente']
        
        # Verificar se já existe um agendamento para a mesma data e hora
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM agendamentos WHERE data = %s AND hora = %s', (data, hora))
        agendamento_existente = cursor.fetchone()
        
        if agendamento_existente:
            flash('Já existe um agendamento para essa data e hora!', 'danger')
        else:
            cursor.execute('INSERT INTO agendamentos (data, hora, descricao, cliente) VALUES (%s, %s, %s, %s)', (data, hora, descricao, cliente))
            mysql.connection.commit()
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('login', redirect=True))
    
    # Gerar datas e horas disponíveis
    hoje = datetime.now().date()
    datas_disponiveis = [(hoje + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    horas_disponiveis = [f'{h:02}:00' for h in range(10, 23)]  # Horário das 10h às 22h
    
    return render_template('agendamentos.html', datas_disponiveis=datas_disponiveis, horas_disponiveis=horas_disponiveis, datetime=datetime)

if __name__ == '__main__':
    app.run(debug=True)