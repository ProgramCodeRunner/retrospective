from flask import Blueprint, render_template, request, redirect, url_for, session
from db import mysql
import hashlib

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def restrict_to_admin():
    if not session.get('loggedin') or session.get('role') != 1:
        return redirect(url_for('auth.login'))


@admin_bp.route('/')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id_user, u.name, t.name 
        FROM user u
        JOIN type_account t ON u.type_account_id_type_account = t.id_type_account
    """)
    users = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html', users=users)


@admin_bp.route('/create', methods=['GET', 'POST'])
def create_user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_type_account, name FROM type_account")
    types = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        type_id = request.form['type_account']
        cur.execute("INSERT INTO user (name, password, type_account_id_type_account) VALUES (%s, %s, %s)",
                    (name, password, type_id))
        mysql.connection.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_user.html', types=types)


@admin_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_type_account, name FROM type_account")
    types = cur.fetchall()

    cur.execute("SELECT id_user, name, type_account_id_type_account FROM user WHERE id_user = %s", (user_id,))
    user = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        type_id = request.form['type_account']

        if password:
            password = hashlib.sha256(password.encode()).hexdigest()
            cur.execute(
                "UPDATE user SET name = %s, password = %s, type_account_id_type_account = %s WHERE id_user = %s",
                (name, password, type_id, user_id))
        else:
            cur.execute("UPDATE user SET name = %s, type_account_id_type_account = %s WHERE id_user = %s",
                        (name, type_id, user_id))

        mysql.connection.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_user.html', user=user, types=types)


@admin_bp.route('/delete/<int:user_id>')
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user WHERE id_user = %s", (user_id,))
    mysql.connection.commit()
    return redirect(url_for('admin.dashboard'))
