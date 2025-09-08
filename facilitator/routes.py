import io
import pandas as pd
from flask import Blueprint, redirect, url_for, session, send_file

from db import mysql

facilitator_bp = Blueprint('facilitator', __name__, url_prefix='/facilitator')


@facilitator_bp.before_request
def restrict_to_facilitator():
    if not session.get('loggedin') or session.get('role') != 2:
        return redirect(url_for('auth.login'))


@facilitator_bp.route('/')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT is_active, voting_active, collecting_decisions, voting_decision_active FROM session_state WHERE id = 1")
    is_active, voting_active, collecting_decisions, voting_decision_active = cur.fetchone()

    # Все идеи + имя автора
    cur.execute("""
         SELECT i.id_idea, i.name, i.description, i.vote, i.type_idea_id_type_idea, u.name 
         FROM idea i 
         JOIN user u ON i.user_id_user = u.id_user
         ORDER BY i.type_idea_id_type_idea, i.vote DESC
     """)
    ideas = cur.fetchall()

    cur.execute("""
        SELECT 
            d.id_idea_decision,
            d.idea_id_idea,
            i.name AS idea_name,
            u.name AS user_name,
            d.name,
            d.description,
            d.vote
        FROM idea_decision d
        JOIN idea i ON d.idea_id_idea = i.id_idea
        JOIN user u ON d.user_id_user = u.id_user
    """)
    decisions = cur.fetchall()

    cur.execute("SELECT topic FROM retrospective_topic WHERE id = 1")
    row = cur.fetchone()
    topic = row[0] if row else None

    cur.close()
    return render_template('facilitator/dashboard.html',
                           topic=topic,
                           is_active=is_active,
                           voting_active=voting_active,
                           voting_decision_active=voting_decision_active,
                           ideas=ideas,
                           decisions=decisions,
                           collecting_decisions=collecting_decisions)


# тема ретроспективы
@facilitator_bp.route('/set_topic', methods=['POST'])
def set_topic():
    topic = request.form.get('topic')
    cur = mysql.connection.cursor()
    cur.execute("REPLACE INTO retrospective_topic (id, topic) VALUES (1, %s)", (topic,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/delete_topic', methods=['POST'])
def delete_topic():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM retrospective_topic WHERE id = 1")
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/get_topic')
def get_topic():
    cur = mysql.connection.cursor()
    cur.execute("SELECT topic FROM retrospective_topic WHERE id = 1")
    row = cur.fetchone()
    cur.close()
    topic = row[0] if row else "не задана"
    return topic


@facilitator_bp.route('/toggle', methods=['POST'])
def toggle_session():
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_active FROM session_state WHERE id = 1")
    current = cur.fetchone()[0]

    new_state = not current
    cur.execute("UPDATE session_state SET is_active = %s WHERE id = 1", (new_state,))

    if new_state:
        cur.execute(
            "UPDATE session_state SET voting_active = FALSE, collecting_decisions = FALSE, voting_decision_active = "
            "FALSE WHERE id = 1")

    mysql.connection.commit()
    cur.close()
    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/toggle_voting', methods=['POST'])
def toggle_voting():
    cur = mysql.connection.cursor()
    cur.execute("SELECT voting_active FROM session_state WHERE id = 1")
    current = cur.fetchone()[0]

    new_state = not current
    cur.execute("UPDATE session_state SET voting_active = %s WHERE id = 1", (new_state,))

    # Отключить сбор, если началось голосование
    if new_state:
        cur.execute(
            "UPDATE session_state SET is_active = FALSE, collecting_decisions = FALSE, voting_decision_active = FALSE WHERE id = 1")

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/edit_idea/<int:idea_id>', methods=['GET', 'POST'])
def edit_idea(idea_id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cur.execute("UPDATE idea SET name = %s, description = %s WHERE id_idea = %s", (name, description, idea_id))
        mysql.connection.commit()
        cur.close()
        flash('Идея обновлена.')
        return redirect(url_for('facilitator.dashboard'))

    cur.execute("SELECT id_idea, name, description FROM idea WHERE id_idea = %s", (idea_id,))
    idea = cur.fetchone()
    cur.close()
    return render_template('facilitator/edit_idea.html', idea=idea)


@facilitator_bp.route('/delete_idea/<int:idea_id>', methods=['POST'])
def delete_idea(idea_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM idea WHERE id_idea = %s", (idea_id,))
    mysql.connection.commit()
    cur.close()
    flash('Идея удалена.')
    return redirect(url_for('facilitator.dashboard'))


from flask import request, flash, render_template


# Показать форму редактирования решения
@facilitator_bp.route('/decision/edit/<int:decision_id>', methods=['GET', 'POST'])
def edit_decision(decision_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cur.execute("UPDATE idea_decision SET name = %s, description = %s WHERE id_idea_decision = %s",
                    (name, description, decision_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('facilitator.dashboard'))

    cur.execute("SELECT name, description FROM idea_decision WHERE id_idea_decision = %s", (decision_id,))
    decision = cur.fetchone()
    cur.close()
    return render_template('facilitator/edit_decision.html', decision=decision, decision_id=decision_id)


# Удаление решения
@facilitator_bp.route('/decision/delete/<int:decision_id>')
def delete_decision(decision_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM idea_decision WHERE id_idea_decision = %s", (decision_id,))
    mysql.connection.commit()
    cur.close()
    flash('Решение удалено.', 'warning')
    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/toggle_decision_collection', methods=['POST'])
def toggle_decision_collection():
    cur = mysql.connection.cursor()
    cur.execute("SELECT collecting_decisions FROM session_state WHERE id = 1")
    current = cur.fetchone()[0]
    new_state = not current
    cur.execute("UPDATE session_state SET collecting_decisions = %s WHERE id = 1", (new_state,))
    if new_state:
        cur.execute(
            "UPDATE session_state SET is_active = FALSE, voting_active = FALSE, voting_decision_active = FALSE WHERE id = 1")
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('facilitator.dashboard'))


@facilitator_bp.route('/toggle_voting_decision', methods=['POST'])
def toggle_voting_decision():
    cur = mysql.connection.cursor()
    cur.execute("SELECT voting_decision_active FROM session_state WHERE id = 1")
    current = cur.fetchone()[0]
    new_state = not current
    cur.execute("UPDATE session_state SET voting_decision_active = %s WHERE id = 1", (new_state,))
    if new_state:
        cur.execute(
            "UPDATE session_state SET is_active = FALSE, voting_active = FALSE, collecting_decisions = FALSE WHERE id = 1")
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('facilitator.dashboard'))


# отчет
@facilitator_bp.route('/report')
def report():
    """
    Рендерит страницу отчёта:
    1) Тема ретроспективы
    2) Топ-3 «Что было хорошо»: идея + её топ-решение + информация по исполнителям и срокам
    3) Топ-3 «Что было плохо»: аналогично
    """
    cur = mysql.connection.cursor()

    # 1. Тема ретроспективы
    cur.execute("SELECT topic FROM retrospective_topic WHERE id = 1")
    row = cur.fetchone()
    topic = row[0] if row else "— не задана —"

    # Вспомогательная функция: получить топ-3 идей по типу (1 = «хорошо», 2 = «плохо»)
    def get_top_ideas_with_decisions(idea_type):
        # Сначала выбираем ТОП-3 идеи по общему числу голосов
        cur.execute("""
            SELECT id_idea, name, description, vote 
            FROM idea 
            WHERE type_idea_id_type_idea = %s 
            ORDER BY vote DESC 
            LIMIT 3
        """, (idea_type,))
        ideas = cur.fetchall()  # [(id_idea, name, description, vote), ...]

        result = []
        for (idea_id, idea_name, idea_desc, idea_votes) in ideas:
            # Для каждой идеи найти её ТОП-решение (единственное с наивысшим vote)
            cur.execute("""
                SELECT d.id_idea_decision, d.name, d.description, d.vote, d.user_id_user
                FROM idea_decision d
                WHERE d.idea_id_idea = %s
                ORDER BY d.vote DESC
                LIMIT 1
            """, (idea_id,))
            dec_row = cur.fetchone()  # может быть None, если решений нет
            if dec_row:
                dec_id, dec_name, dec_desc, dec_votes, dec_author_id = dec_row
            else:
                dec_id = dec_name = dec_desc = dec_votes = dec_author_id = None

            # Попробовать получить существующее задание (decision_assignments), если есть
            if dec_id:
                cur.execute("""
                    SELECT da.executor_id, da.start_date, da.end_date, u.name
                    FROM decision_assignments da
                    LEFT JOIN user u ON da.executor_id = u.id_user
                    WHERE da.decision_id = %s
                """, (dec_id,))
                assign_row = cur.fetchone()
                if assign_row:
                    executor_id, start_date, end_date, executor_name = assign_row
                else:
                    executor_id = start_date = end_date = executor_name = None
            else:
                executor_id = start_date = end_date = executor_name = None

            result.append({
                'idea_id': idea_id,
                'idea_name': idea_name,
                'idea_desc': idea_desc,
                'idea_votes': idea_votes,
                'decision_id': dec_id,
                'decision_name': dec_name,
                'decision_desc': dec_desc,
                'decision_votes': dec_votes,
                'decision_author': dec_author_id,
                'executor_id': executor_id,
                'executor_name': executor_name,
                'start_date': start_date,
                'end_date': end_date,
            })
        return result

    # 2. Топ-3 «Что было хорошо» (type = 1)
    top_good = get_top_ideas_with_decisions(1)

    # 3. Топ-3 «Что было плохо» (type = 2)
    top_bad = get_top_ideas_with_decisions(2)

    # Список всех пользователей для раскрывающегося списка исполнителей
    cur.execute("SELECT id_user, name FROM user")
    users = cur.fetchall()  # [(id_user, name), ...]

    cur.close()
    return render_template('facilitator/report.html',
                           topic=topic,
                           top_good=top_good,
                           top_bad=top_bad,
                           users=users)


@facilitator_bp.route('/report/export')
def report_export():
    """
    Генерирует отчет в виде Excel-файла, включая тему ретроспективы.
    """
    cur = mysql.connection.cursor()

    # Получаем тему ретроспективы
    cur.execute("SELECT topic FROM retrospective_topic WHERE id = 1")
    row = cur.fetchone()
    topic = row[0] if row else "— не задана —"

    def get_top_ideas_for_excel(idea_type):
        cur.execute("""
            SELECT id_idea, name, description, vote 
            FROM idea 
            WHERE type_idea_id_type_idea = %s 
            ORDER BY vote DESC 
            LIMIT 3
        """, (idea_type,))
        return cur.fetchall()

    top_good_ideas = get_top_ideas_for_excel(1)
    top_bad_ideas = get_top_ideas_for_excel(2)

    rows = []

    def append_rows(idea_rows, label_type):
        for idea in idea_rows:
            idea_id, idea_name, idea_desc, idea_votes = idea
            cur.execute("""
                SELECT d.id_idea_decision, d.name, d.description, d.vote, d.user_id_user
                FROM idea_decision d
                WHERE d.idea_id_idea = %s
                ORDER BY d.vote DESC
                LIMIT 1
            """, (idea_id,))
            dec_row = cur.fetchone()
            if dec_row:
                dec_id, dec_name, dec_desc, dec_votes, dec_author_id = dec_row
                cur.execute("""
                    SELECT da.executor_id, da.start_date, da.end_date, u.name
                    FROM decision_assignments da
                    LEFT JOIN user u ON da.executor_id = u.id_user
                    WHERE da.decision_id = %s
                """, (dec_id,))
                assign_row = cur.fetchone()
                if assign_row:
                    executor_id, start_date, end_date, executor_name = assign_row
                else:
                    executor_name = start_date = end_date = None
            else:
                dec_name = dec_desc = dec_votes = executor_name = start_date = end_date = None

            rows.append({
                'Тип идеи': label_type,
                'Название идеи': idea_name,
                'Описание идеи': idea_desc,
                'Голоса идеи': idea_votes,
                'Название решения': dec_name,
                'Описание решения': dec_desc,
                'Голоса решения': dec_votes,
                'Исполнитель': executor_name,
                'Дата начала': start_date,
                'Дата окончания': end_date,
            })

    append_rows(top_good_ideas, 'Что было хорошо')
    append_rows(top_bad_ideas, 'Что было плохо')

    cur.close()

    df = pd.DataFrame(rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        sheet_name = 'Отчет ретроспективы'
        df.to_excel(writer, index=False, startrow=2, sheet_name=sheet_name)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Формат: выравнивание по центру, жирный шрифт
        merge_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_size': 14
        })

        # Объединяем ячейки A1:J1 и вставляем тему
        worksheet.merge_range('A1:J1', f'Тема ретроспективы: {topic}', merge_format)

        # Автоширина столбцов
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet.set_column(i, i, max_len + 2)

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='retrospective_report.xlsx'
    )



@facilitator_bp.route('/assign_executor', methods=['POST'])
def assign_executor():
    """
    Обрабатывает POST-форму из report.html,
    чтобы назначить исполнителя (или изменить) для выбранного решения.
    """
    decision_id = request.form.get('decision_id')
    executor_id = request.form.get('executor_id')  # может быть пустой строкой
    start_date = request.form.get('start_date')  # YYYY-MM-DD или пусто
    end_date = request.form.get('end_date')

    cur = mysql.connection.cursor()

    # Если передан пустой executor_id, сохраним NULL
    if executor_id:
        # Но сначала проверим, что такой пользователь вообще существует в БД
        cur.execute("SELECT id_user FROM user WHERE id_user = %s", (executor_id,))
        if not cur.fetchone():
            flash("Выбранный пользователь не найден.", "danger")
            cur.close()
            return redirect(url_for('facilitator.report'))
    else:
        executor_id = None

    # Проверяем, есть ли уже запись assignment для этого decision_id
    cur.execute("SELECT id FROM decision_assignments WHERE decision_id = %s", (decision_id,))
    existing = cur.fetchone()

    if existing:
        # Обновляем существующую запись
        cur.execute("""
            UPDATE decision_assignments 
            SET executor_id = %s, start_date = %s, end_date = %s 
            WHERE decision_id = %s
        """, (executor_id, start_date if start_date else None, end_date if end_date else None, decision_id))
    else:
        # Создаём новую, если executor_id указан (или даже если пустой — чтобы была запись)
        cur.execute("""
            INSERT INTO decision_assignments (decision_id, executor_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
        """, (decision_id, executor_id if executor_id else None,
              start_date if start_date else None, end_date if end_date else None))
    mysql.connection.commit()
    cur.close()
    flash("Данные сохранены.", "success")
    return redirect(url_for('facilitator.report'))
