from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime
from extensions import db
from models.project import Project, ProjectTask  # Changed from 'models import'

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('projects/index.html', projects=projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project = Project(
            user_id=current_user.id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            status=request.form.get('status', 'Active'),
            notes=request.form.get('notes')
        )

        start_date = request.form.get('start_date')
        if start_date:
            project.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        deadline = request.form.get('deadline')
        if deadline:
            project.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

        db.session.add(project)
        db.session.commit()

        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.index'))

    return render_template('projects/create.html')


@projects_bp.route('/<int:project_id>')
@login_required
def view( project_id ):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    tasks = project.tasks.order_by(ProjectTask.due_date).all()
    return render_template('projects/view.html', project=project, tasks=tasks)


@projects_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit( project_id ):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.category = request.form.get('category')
        project.status = request.form.get('status')
        project.notes = request.form.get('notes')

        start_date = request.form.get('start_date')
        if start_date:
            project.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            project.start_date = None

        deadline = request.form.get('deadline')
        if deadline:
            project.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        else:
            project.deadline = None

        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view', project_id=project.id))

    return render_template('projects/edit.html', project=project)


@projects_bp.route('/delete/<int:project_id>')
@login_required
def delete( project_id ):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects.index'))


# Task routes
@projects_bp.route('/<int:project_id>/tasks/create', methods=['POST'])
@login_required
def create_task( project_id ):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    title = request.form.get('title')
    if not title:
        flash('Task title is required.', 'danger')
        return redirect(url_for('projects.view', project_id=project_id))

    task = ProjectTask(
        project_id=project_id,
        title=title,
        description=request.form.get('description'),
        status='Pending'
    )

    due_date = request.form.get('due_date')
    if due_date:
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

    db.session.add(task)
    db.session.commit()

    # Update project progress
    project.update_progress()

    flash('Task created successfully!', 'success')
    return redirect(url_for('projects.view', project_id=project_id))


@projects_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task( task_id ):
    task = ProjectTask.query.get_or_404(task_id)
    project = Project.query.filter_by(id=task.project_id, user_id=current_user.id).first_or_404()

    task.status = 'Done' if task.status == 'Pending' else 'Pending'
    db.session.commit()

    # Update project progress
    project.update_progress()

    return jsonify({'status': 'success', 'new_status': task.status})


@projects_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task( task_id ):
    task = ProjectTask.query.get_or_404(task_id)
    project = Project.query.filter_by(id=task.project_id, user_id=current_user.id).first_or_404()

    db.session.delete(task)
    db.session.commit()

    # Update project progress
    project.update_progress()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('projects.view', project_id=project.id))