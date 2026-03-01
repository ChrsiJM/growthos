from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime
from extensions import db
from models.reflection import Reflection  # Changed from 'models import'

reflections_bp = Blueprint('reflections', __name__)


@reflections_bp.route('/')
@login_required
def index():
    reflections = Reflection.query.filter_by(user_id=current_user.id).order_by(Reflection.created_at.desc()).all()
    return render_template('reflections/index.html', reflections=reflections)


@reflections_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        reflection = Reflection(
            user_id=current_user.id,
            type=request.form.get('type'),
            wins=request.form.get('wins'),
            failures=request.form.get('failures'),
            lessons=request.form.get('lessons'),
            next_focus=request.form.get('next_focus')
        )

        db.session.add(reflection)
        db.session.commit()

        flash('Reflection saved successfully!', 'success')
        return redirect(url_for('reflections.index'))

    return render_template('reflections/create.html')


@reflections_bp.route('/view/<int:reflection_id>')
@login_required
def view( reflection_id ):
    reflection = Reflection.query.filter_by(id=reflection_id, user_id=current_user.id).first_or_404()
    return render_template('reflections/view.html', reflection=reflection)


@reflections_bp.route('/edit/<int:reflection_id>', methods=['GET', 'POST'])
@login_required
def edit( reflection_id ):
    reflection = Reflection.query.filter_by(id=reflection_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        reflection.type = request.form.get('type')
        reflection.wins = request.form.get('wins')
        reflection.failures = request.form.get('failures')
        reflection.lessons = request.form.get('lessons')
        reflection.next_focus = request.form.get('next_focus')

        db.session.commit()
        flash('Reflection updated successfully!', 'success')
        return redirect(url_for('reflections.view', reflection_id=reflection.id))

    return render_template('reflections/edit.html', reflection=reflection)


@reflections_bp.route('/delete/<int:reflection_id>')
@login_required
def delete( reflection_id ):
    reflection = Reflection.query.filter_by(id=reflection_id, user_id=current_user.id).first_or_404()
    db.session.delete(reflection)
    db.session.commit()
    flash('Reflection deleted successfully!', 'success')
    return redirect(url_for('reflections.index'))