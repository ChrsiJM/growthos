from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime
from app import db
from models.idea import Idea  # Changed from 'models import'
from models.project import Project  # Changed from 'models import'

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/')
@login_required
def index():
    category = request.args.get('category')

    query = Idea.query.filter_by(user_id=current_user.id)

    if category:
        query = query.filter_by(category=category)

    ideas = query.order_by(Idea.date_created.desc()).all()

    # Get unique categories for filter
    categories = db.session.query(Idea.category).filter_by(user_id=current_user.id).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return render_template('ideas/index.html', ideas=ideas, categories=categories)


@ideas_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        idea = Idea(
            user_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category')
        )

        db.session.add(idea)
        db.session.commit()

        flash('Idea saved successfully!', 'success')
        return redirect(url_for('ideas.index'))

    return render_template('ideas/create.html')


@ideas_bp.route('/edit/<int:idea_id>', methods=['GET', 'POST'])
@login_required
def edit( idea_id ):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        idea.title = request.form.get('title')
        idea.description = request.form.get('description')
        idea.category = request.form.get('category')

        db.session.commit()
        flash('Idea updated successfully!', 'success')
        return redirect(url_for('ideas.index'))

    return render_template('ideas/edit.html', idea=idea)


@ideas_bp.route('/delete/<int:idea_id>')
@login_required
def delete( idea_id ):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    db.session.delete(idea)
    db.session.commit()
    flash('Idea deleted successfully!', 'success')
    return redirect(url_for('ideas.index'))


@ideas_bp.route('/convert/<int:idea_id>', methods=['POST'])
@login_required
def convert_to_project( idea_id ):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()

    # Create project from idea
    project = Project(
        user_id=current_user.id,
        name=idea.title,
        description=idea.description,
        category=idea.category,
        status='Active'
    )

    db.session.add(project)
    db.session.flush()  # Get project ID

    # Link idea to project
    idea.linked_project_id = project.id

    db.session.commit()

    flash(f'Idea converted to project "{project.name}" successfully!', 'success')
    return redirect(url_for('projects.view', project_id=project.id))