from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime, date, timedelta
from extensions import db
from models.finance import WeeklyFinance

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/')
@login_required
def index():
    today = date.today()

    # Get current week finance
    current_week = WeeklyFinance.query.filter(
        WeeklyFinance.user_id == current_user.id,
        WeeklyFinance.week_start_date <= today,
        WeeklyFinance.week_end_date >= today
    ).first()

    # Get all weekly finances
    weekly_records = WeeklyFinance.query.filter_by(
        user_id=current_user.id
    ).order_by(WeeklyFinance.week_start_date.desc()).all()

    # Calculate monthly totals
    month_start = date(today.year, today.month, 1)
    monthly_records = WeeklyFinance.query.filter(
        WeeklyFinance.user_id == current_user.id,
        WeeklyFinance.week_start_date >= month_start,
        WeeklyFinance.week_end_date <= today
    ).all()

    total_income = sum(r.total_income for r in monthly_records)
    total_expenses = sum(r.total_expenses for r in monthly_records)
    net_profit = total_income - total_expenses

    return render_template(
        'finance/index.html',
        current_week=current_week,
        weekly_records=weekly_records,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        today=today
    )


@finance_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        week_start = datetime.strptime(request.form.get('week_start'), '%Y-%m-%d').date()
        week_end = week_start + timedelta(days=6)

        finance = WeeklyFinance(
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            income_source=request.form.get('income_source'),
            total_income=float(request.form.get('total_income', 0)),
            total_expenses=float(request.form.get('total_expenses', 0)),
            expense_description=request.form.get('expense_description'),
            review_completed=request.form.get('review_completed') == 'on'
        )

        db.session.add(finance)
        db.session.commit()

        flash('Weekly finance record created successfully!', 'success')
        return redirect(url_for('finance.index'))

    return render_template('finance/create.html', today=date.today())


@finance_bp.route('/edit/<int:finance_id>', methods=['GET', 'POST'])
@login_required
def edit( finance_id ):
    finance = WeeklyFinance.query.filter_by(id=finance_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        finance.income_source = request.form.get('income_source')
        finance.total_income = float(request.form.get('total_income', 0))
        finance.total_expenses = float(request.form.get('total_expenses', 0))
        finance.expense_description = request.form.get('expense_description')
        finance.review_completed = request.form.get('review_completed') == 'on'

        db.session.commit()
        flash('Weekly finance updated successfully!', 'success')
        return redirect(url_for('finance.index'))

    return render_template('finance/edit.html', finance=finance)


@finance_bp.route('/delete/<int:finance_id>')
@login_required
def delete( finance_id ):
    finance = WeeklyFinance.query.filter_by(id=finance_id, user_id=current_user.id).first_or_404()
    db.session.delete(finance)
    db.session.commit()
    flash('Weekly finance deleted successfully!', 'success')
    return redirect(url_for('finance.index'))