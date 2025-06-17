from flask import Blueprint, render_template, session, redirect, url_for, request, g
from db import mysql

participant_bp = Blueprint('participant', __name__, url_prefix='/participant')


@participant_bp.before_request
def restrict_to_participant():
    if not session.get('loggedin') or session.get('role') != 3:
        return redirect(url_for('auth.login'))


@participant_bp.route('/')
def dashboard():
    user_id = session.get('id')
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT is_active, voting_active, collecting_decisions, voting_decision_active FROM session_state WHERE id = 1")
    is_active, voting_active, collecting_decisions, voting_decision_active = cur.fetchone()
    cur.close()

    if is_active:
        return render_template('participant/dashboard.html')
    elif voting_active:
        has_voted = False
        # Загрузка идей из БД
        cur = mysql.connection.cursor()

        # Проверка: голосовал ли пользователь
        cur.execute("SELECT voted_stage1 FROM votes_cast WHERE user_id = %s", (user_id,))
        vote_status = cur.fetchone()

        if vote_status and vote_status[0]:
            has_voted = True

        cur.execute("""
                    SELECT id_idea, type_idea_id_type_idea, name, description, vote
                    FROM idea
                """)
        ideas = cur.fetchall()
        cur.close()
        return render_template('participant/voting.html', ideas=ideas, has_voted=has_voted)

    elif collecting_decisions:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_idea, name, description, vote
            FROM idea
            WHERE type_idea_id_type_idea = 1
            ORDER BY vote DESC
            LIMIT 3
        """)
        good_ideas = cur.fetchall()

        cur.execute("""
            SELECT id_idea, name, description, vote
            FROM idea
            WHERE type_idea_id_type_idea = 2
            ORDER BY vote DESC
            LIMIT 3
        """)
        bad_ideas = cur.fetchall()

        cur.execute("""
            SELECT id_idea, name FROM idea
            WHERE type_idea_id_type_idea = 1
            ORDER BY vote DESC
            LIMIT 3
        """)
        good_idea_choices = cur.fetchall()

        cur.execute("""
            SELECT id_idea, name FROM idea
            WHERE type_idea_id_type_idea = 2
            ORDER BY vote DESC
            LIMIT 3
        """)
        bad_idea_choices = cur.fetchall()

        cur.close()

        return render_template('participant/decision_submission.html',
                               good_ideas=good_ideas,
                               bad_ideas=bad_ideas,
                               good_idea_choices=good_idea_choices,
                               bad_idea_choices=bad_idea_choices)
    elif voting_decision_active:
        has_voted = False
        cur = mysql.connection.cursor()
        cur.execute("SELECT voted_stage2 FROM votes_cast WHERE user_id = %s", (user_id,))
        vote_status = cur.fetchone()

        if vote_status and vote_status[0]:
            has_voted = True

        # Получаем топ 3 идеи по типу 1 ("хорошо")
        cur.execute("""
            SELECT id_idea, type_idea_id_type_idea, name, description
            FROM idea
            WHERE type_idea_id_type_idea = 1
            ORDER BY vote DESC
            LIMIT 3
        """)
        good_ideas = cur.fetchall()

        # Получаем топ 3 идеи по типу 2 ("плохо")
        cur.execute("""
            SELECT id_idea, type_idea_id_type_idea, name, description
            FROM idea
            WHERE type_idea_id_type_idea = 2
            ORDER BY vote DESC
            LIMIT 3
        """)
        bad_ideas = cur.fetchall()

        # Получаем все решения
        idea_ids = [row[0] for row in good_ideas + bad_ideas]
        format_strings = ','.join(['%s'] * len(idea_ids)) if idea_ids else 'NULL'
        cur.execute(f"""
            SELECT id_idea_decision, idea_id_idea, name, description
            FROM idea_decision
            WHERE idea_id_idea IN ({format_strings})
        """, idea_ids if idea_ids else [])

        decisions = cur.fetchall()
        cur.close()

        # Группировка решений по идее
        decision_map = {}
        for decision in decisions:
            decision_map.setdefault(decision[1], []).append(decision)

        return render_template(
            'participant/decision_voting.html',
            has_voted=has_voted,
            good_ideas=good_ideas,
            bad_ideas=bad_ideas,
            decision_map=decision_map
        )

    else:
        return render_template('participant/waiting.html')


@participant_bp.before_request
def load_retrospective_topic():
    cur = mysql.connection.cursor()
    cur.execute("SELECT topic FROM retrospective_topic WHERE id = 1")
    row = cur.fetchone()
    g.retrospective_topic = row[0] if row else "не задана"
    cur.close()


@participant_bp.route('/submit/<int:idea_type>', methods=['POST'])
def submit_idea(idea_type):
    name = request.form['name']
    description = request.form['description']
    user_id = session.get('id')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO idea (type_idea_id_type_idea, user_id_user, name, description, vote)
        VALUES (%s, %s, %s, %s, %s)
    """, (idea_type, user_id, name, description, 0))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('participant.dashboard'))


@participant_bp.route('/submit_votes', methods=['POST'])
def submit_votes():
    user_id = session.get('id')
    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO votes_cast (user_id) VALUES (%s)", (user_id,))

    form = request.form

    plus_total = 0
    minus_total = 0

    updates = []

    for key, value in form.items():
        if not value:
            continue
        try:
            votes = int(value)
            if votes <= 0:
                continue
        except ValueError:
            continue

        if key.startswith('plus_votes_'):
            plus_total += votes
        elif key.startswith('minus_votes_'):
            minus_total += votes

        idea_id = int(key.split('_')[-1])
        updates.append((votes, idea_id))

    if plus_total > 5 or minus_total > 5:
        cur.close()
        return "Превышен лимит голосов", 400

    # Обновляем идеи
    for votes, idea_id in updates:
        cur.execute("UPDATE idea SET vote = vote + %s WHERE id_idea = %s", (votes, idea_id))

    # Добавляем запись о голосовании
    cur.execute("UPDATE votes_cast SET voted_stage1 = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('participant.dashboard'))


@participant_bp.route('/submit_decision', methods=['POST'])
def submit_decision():
    idea_id = request.form['idea_id']
    name = request.form['name']
    description = request.form['description']
    user_id = session.get('id')
    vote = 0

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO idea_decision (idea_id_idea, user_id_user, name, description, vote)
        VALUES (%s, %s, %s, %s, %s)
    """, (idea_id, user_id, name, description, vote))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('participant.dashboard'))


@participant_bp.route('/decision_voting')
def decision_voting():
    user_id = session.get('id')
    cur = mysql.connection.cursor()

    # Топ-3 идеи каждого типа
    cur.execute("""
        SELECT id_idea, type_idea_id_type_idea, name, description 
        FROM idea 
        WHERE type_idea_id_type_idea = 1 
        ORDER BY vote DESC 
        LIMIT 3
    """)
    good_ideas = cur.fetchall()

    cur.execute("""
        SELECT id_idea, type_idea_id_type_idea, name, description 
        FROM idea 
        WHERE type_idea_id_type_idea = 2 
        ORDER BY vote DESC 
        LIMIT 3
    """)
    bad_ideas = cur.fetchall()

    # Все решения по этим идеям
    idea_ids = [idea[0] for idea in good_ideas + bad_ideas]
    format_strings = ','.join(['%s'] * len(idea_ids))
    cur.execute(f"""
        SELECT id_idea_decision, idea_id_idea, name, description 
        FROM idea_decision 
        WHERE idea_id_idea IN ({format_strings})
    """, tuple(idea_ids))
    decisions = cur.fetchall()
    cur.close()

    # Сгруппировать решения по idea_id
    decision_map = {}
    for d in decisions:
        decision_map.setdefault(d[1], []).append(d)

    return render_template(
        'participant/decision_voting.html',
        good_ideas=good_ideas,
        bad_ideas=bad_ideas,
        decision_map=decision_map
    )


@participant_bp.route('/submit_decision_votes', methods=['POST'])
def submit_decision_votes():
    user_id = session.get('id')
    form = request.form
    cur = mysql.connection.cursor()

    # Проверка на существование записи
    cur.execute("SELECT * FROM votes_cast WHERE user_id = %s", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO votes_cast (user_id) VALUES (%s)", (user_id,))

    idea_votes = {}

    for key, value in form.items():
        if not value:
            continue
        try:
            val = int(value)
            if val < 0:
                continue
        except ValueError:
            continue

        # expected key format: decision_<decision_id>_idea_<idea_id>
        if key.startswith('decision_'):
            parts = key.split('_')
            decision_id = int(parts[1])
            idea_id = int(parts[3])

            idea_votes.setdefault(idea_id, []).append((decision_id, val))

    # Проверка лимитов
    for idea_id, votes in idea_votes.items():
        total = sum(v[1] for v in votes)
        if total > 5:
            cur.close()
            return "Нельзя на одну идею потратить более 5 голосов", 400

    # Обновление голосов
    for idea_id, votes in idea_votes.items():
        for decision_id, value in votes:
            cur.execute("""
                UPDATE idea_decision SET vote = vote + %s 
                WHERE id_idea_decision = %s
            """, (value, decision_id))

    cur.execute("UPDATE votes_cast SET voted_stage2 = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('participant.dashboard'))
