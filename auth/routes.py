from flask import Blueprint, render_template, request, redirect, url_for, session
from db import mysql
import hashlib

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id_user, name, type_account_id_type_account FROM user WHERE name = %s AND password = %s",
                    (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]

            # РЕДИРЕКТ в зависимости от роли
            if session['role'] == 1:
                return redirect(url_for('admin.dashboard'))
            elif session['role'] == 2:
                return redirect(url_for('facilitator.dashboard'))
            elif session['role'] == 3:
                return redirect(url_for('participant.dashboard'))
            else:
                error = 'Неизвестная роль пользователя.'

        else:
            error = 'Неверные данные для входа'

    return render_template('login.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
