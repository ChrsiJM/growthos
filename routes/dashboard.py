from flask import render_template
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime, date, timedelta
from sqlalchemy import func
from models.daily_plan import DailyPlan
from models.lead import Lead
from models.project import Project
from models.event import Event
from models.finance import WeeklyFinance

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()

    # Today's tasks
    todays_tasks = DailyPlan.query.filter_by(
        user_id=current_user.id,
        planned_date=today
    ).all()

    # Execution rate this week
    week_start = today - timedelta(days=today.weekday())
    week_plans = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.planned_date >= week_start,
        DailyPlan.planned_date <= today
    ).all()

    if week_plans:
        achieved_count = sum(1 for p in week_plans if p.status == 'Achieved')
        execution_rate = int((achieved_count / len(week_plans)) * 100)
    else:
        execution_rate = 0

    # Active projects count
    active_projects = Project.query.filter_by(
        user_id=current_user.id,
        status='Active'
    ).count()

    # Follow-ups due today
    follow_ups_today = Lead.query.filter(
        Lead.user_id == current_user.id,
        Lead.follow_up_date == today,
        Lead.status.in_(['Negotiating'])
    ).count()

    # Revenue metrics
    leads = Lead.query.filter_by(user_id=current_user.id).all()
    potential_revenue = sum(l.expected_value for l in leads if l.status == 'Negotiating')
    closed_revenue = sum(l.expected_value for l in leads if l.status == 'Closed')

    # Weekly balance
    current_week_finance = WeeklyFinance.query.filter(
        WeeklyFinance.user_id == current_user.id,
        WeeklyFinance.week_start_date <= today,
        WeeklyFinance.week_end_date >= today
    ).first()

    weekly_balance = current_week_finance.remaining_balance if current_week_finance else 0

    # Upcoming meetings
    upcoming_meetings = Event.query.filter(
        Event.user_id == current_user.id,
        Event.event_date >= datetime.now()
    ).order_by(Event.event_date).limit(5).all()

    # Streak counter (consecutive days with achieved tasks)
    streak = calculate_streak()

    # Revenue goal progress (example: monthly goal of $10,000)
    monthly_goal = 10000
    monthly_revenue = sum(
        l.expected_value for l in leads
        if l.status == 'Closed' and
        l.created_at.month == today.month
    )
    revenue_progress = int((monthly_revenue / monthly_goal) * 100) if monthly_goal > 0 else 0

    return render_template(
        'dashboard/index.html',
        todays_tasks=todays_tasks,
        execution_rate=execution_rate,
        active_projects=active_projects,
        follow_ups_today=follow_ups_today,
        potential_revenue=potential_revenue,
        closed_revenue=closed_revenue,
        weekly_balance=weekly_balance,
        upcoming_meetings=upcoming_meetings,
        streak=streak,
        revenue_progress=revenue_progress,
        monthly_revenue=monthly_revenue,
        monthly_goal=monthly_goal
    )


def calculate_streak():
    from datetime import date, timedelta

    today = date.today()
    streak = 0
    check_date = today

    while True:
        day_plans = DailyPlan.query.filter_by(
            user_id=current_user.id,
            planned_date=check_date
        ).all()

        if not day_plans:
            break

        # Check if all tasks for that day are achieved
        all_achieved = all(plan.status == 'Achieved' for plan in day_plans)

        if all_achieved:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak