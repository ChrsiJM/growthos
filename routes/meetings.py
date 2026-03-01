from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime
from extensions import db
from models.event import Event  # Changed from 'models import'
from models.lead import Lead  # Changed from 'models import'
from models.project import Project  # Changed from 'models import'

meetings_bp = Blueprint('meetings', __name__)


@meetings_bp.route('/')
@login_required
def index():
    now = datetime.now()

    upcoming = Event.query.filter(
        Event.user_id == current_user.id,
        Event.event_date >= now
    ).order_by(Event.event_date).all()

    past = Event.query.filter(
        Event.user_id == current_user.id,
        Event.event_date < now
    ).order_by(Event.event_date.desc()).all()

    return render_template('meetings/index.html', upcoming=upcoming, past=past)


@meetings_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        event = Event(
            user_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            reminder_note=request.form.get('reminder_note')
        )

        event_date = request.form.get('event_date')
        if event_date:
            event.event_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')

        linked_lead_id = request.form.get('linked_lead_id')
        if linked_lead_id and linked_lead_id != '':
            event.linked_lead_id = int(linked_lead_id)

        linked_project_id = request.form.get('linked_project_id')
        if linked_project_id and linked_project_id != '':
            event.linked_project_id = int(linked_project_id)

        db.session.add(event)
        db.session.commit()

        flash('Meeting/Event created successfully!', 'success')
        return redirect(url_for('meetings.index'))

    leads = Lead.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()

    return render_template('meetings/create.html', leads=leads, projects=projects)


@meetings_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit( event_id ):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.reminder_note = request.form.get('reminder_note')

        event_date = request.form.get('event_date')
        if event_date:
            event.event_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')

        linked_lead_id = request.form.get('linked_lead_id')
        event.linked_lead_id = int(linked_lead_id) if linked_lead_id and linked_lead_id != '' else None

        linked_project_id = request.form.get('linked_project_id')
        event.linked_project_id = int(linked_project_id) if linked_project_id and linked_project_id != '' else None

        db.session.commit()
        flash('Meeting/Event updated successfully!', 'success')
        return redirect(url_for('meetings.index'))

    leads = Lead.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()

    return render_template('meetings/edit.html', event=event, leads=leads, projects=projects)


@meetings_bp.route('/delete/<int:event_id>')
@login_required
def delete( event_id ):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    flash('Meeting/Event deleted successfully!', 'success')
    return redirect(url_for('meetings.index'))