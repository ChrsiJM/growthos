from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime, date, timedelta
from extensions import db
from models.daily_plan import DailyPlan

planner_bp = Blueprint('planner', __name__)


@planner_bp.route('/')
@login_required
def index():
    # Auto-carry missed tasks
    auto_carry_missed_tasks()

    today = date.today()
    selected_date = request.args.get('date', today.isoformat())

    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = today

    tasks = DailyPlan.query.filter_by(
        user_id=current_user.id,
        planned_date=selected_date
    ).order_by(DailyPlan.created_at).all()

    # Get week statistics
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_end = week_start + timedelta(days=6)
    week_tasks = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.planned_date >= week_start,
        DailyPlan.planned_date <= week_end
    ).all()

    week_stats = {
        'total': len(week_tasks),
        'achieved': sum(1 for t in week_tasks if t.status == 'Achieved'),
        'missed': sum(1 for t in week_tasks if t.status == 'Missed'),
        'carried': sum(1 for t in week_tasks if t.status == 'Carried')
    }

    return render_template(
        'planner/index.html',
        tasks=tasks,
        selected_date=selected_date,
        week_stats=week_stats,
        today=today,
        timedelta=timedelta  # Pass timedelta to template
    )


@planner_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        planned_date = request.form.get('planned_date')

        if not title or not planned_date:
            flash('Title and date are required.', 'danger')
            return render_template('planner/create.html')

        task = DailyPlan(
            user_id=current_user.id,
            title=title,
            description=description,
            planned_date=datetime.strptime(planned_date, '%Y-%m-%d').date()
        )

        db.session.add(task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('planner.index', date=planned_date))

    return render_template('planner/create.html', today=date.today())


@planner_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit( task_id ):
    task = DailyPlan.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status = request.form.get('status')
        task.feedback = request.form.get('feedback')

        # Validate feedback for missed tasks
        if task.status == 'Missed' and not task.feedback:
            flash('Please provide feedback for missed tasks.', 'danger')
            return render_template('planner/edit.html', task=task)

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('planner.index', date=task.planned_date.isoformat()))

    return render_template('planner/edit.html', task=task)


@planner_bp.route('/delete/<int:task_id>')
@login_required
def delete( task_id ):
    task = DailyPlan.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task_date = task.planned_date.isoformat()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('planner.index', date=task_date))


def auto_carry_missed_tasks():
    today = date.today()

    # Find tasks from previous dates that are still pending
    pending_tasks = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.planned_date < today,
        DailyPlan.status == 'Pending'
    ).all()

    for task in pending_tasks:
        # Mark original as carried
        task.status = 'Carried'

        # Create new task for today
        new_task = DailyPlan(
            user_id=current_user.id,
            title=task.title,
            description=task.description,
            planned_date=today,
            status='Pending'
        )
        db.session.add(new_task)

    if pending_tasks:
        db.session.commit()