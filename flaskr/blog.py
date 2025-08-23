from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from datetime import date, datetime

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT id, title, description, term, author_id '
        'FROM tasks WHERE author_id = ?',
        (g.user['id'],)
    ).fetchall()
    
    # TAREFA: dia para entregar: amarelo    depois do dia da entrega: vermelho
    # Tarefa feita: verde
    return render_template('blog/index.html', tasks=tasks)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        term = request.form['term']
        error = None

        if not title:
            error = 'Title is required.'
        elif not description:
            error = 'Description is required.'
        elif not term:
            error = 'Term is required.'

        if len(title) > 25:
            error = 'Title should have less than 25 characters'
        elif len(description) > 1000: 
            error = 'Description should have less than 1000 characters'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (title, description, term, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, term, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')

    
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT t.id, title, description, term, author_id'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()
    task = post  # Alias for clarity

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and task['author_id'] != g.user['id']:
        abort(403)

    return task

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    task = get_post(id)

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        term = request.form['term']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasks SET title = ?, description = ?, term = ?'
                ' WHERE id = ?',
                (title, description, term, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', task=task)


@bp.route('/<int:id>/delete', methods=('POST', 'GET'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))