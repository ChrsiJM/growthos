from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import Blueprint
from datetime import datetime, date
from extensions import db
from models.lead import Lead

leads_bp = Blueprint('leads', __name__)


@leads_bp.route('/')
@login_required
def index():
    # Get filter parameters
    niche = request.args.get('niche')
    interest = request.args.get('interest')

    query = Lead.query.filter_by(user_id=current_user.id)

    if niche:
        query = query.filter_by(niche=niche)
    if interest:
        query = query.filter_by(interest_level=interest)

    leads = query.order_by(Lead.created_at.desc()).all()

    # Get unique niches for filter dropdown
    niches = db.session.query(Lead.niche).filter_by(user_id=current_user.id).distinct().all()
    niches = [n[0] for n in niches if n[0]]

    # Calculate metrics
    today = date.today()
    follow_ups_today = Lead.query.filter(
        Lead.user_id == current_user.id,
        Lead.follow_up_date == today
    ).count()

    overdue_follow_ups = Lead.query.filter(
        Lead.user_id == current_user.id,
        Lead.follow_up_date < today,
        Lead.status.in_(['Negotiating'])
    ).count()

    potential_revenue = sum(l.expected_value for l in leads if l.status == 'Negotiating')
    closed_revenue = sum(l.expected_value for l in leads if l.status == 'Closed')

    return render_template(
        'leads/index.html',
        leads=leads,
        niches=niches,
        follow_ups_today=follow_ups_today,
        overdue_follow_ups=overdue_follow_ups,
        potential_revenue=potential_revenue,
        closed_revenue=closed_revenue,
        today=today  # Add today to template context
    )


# ... rest of the routes remain the same
@leads_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        lead = Lead(
            user_id=current_user.id,
            name=request.form.get('name'),
            niche=request.form.get('niche'),
            source=request.form.get('source'),
            feedback=request.form.get('feedback'),
            interest_level=request.form.get('interest_level'),
            next_action=request.form.get('next_action'),
            expected_value=float(request.form.get('expected_value', 0)),
            status=request.form.get('status', 'Negotiating')
        )

        follow_up_date = request.form.get('follow_up_date')
        if follow_up_date:
            lead.follow_up_date = datetime.strptime(follow_up_date, '%Y-%m-%d').date()

        db.session.add(lead)
        db.session.commit()

        flash('Lead created successfully!', 'success')
        return redirect(url_for('leads.index'))

    return render_template('leads/create.html')


@leads_bp.route('/edit/<int:lead_id>', methods=['GET', 'POST'])
@login_required
def edit( lead_id ):
    lead = Lead.query.filter_by(id=lead_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        lead.name = request.form.get('name')
        lead.niche = request.form.get('niche')
        lead.source = request.form.get('source')
        lead.feedback = request.form.get('feedback')
        lead.interest_level = request.form.get('interest_level')
        lead.next_action = request.form.get('next_action')
        lead.expected_value = float(request.form.get('expected_value', 0))
        lead.status = request.form.get('status')

        follow_up_date = request.form.get('follow_up_date')
        if follow_up_date:
            lead.follow_up_date = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
        else:
            lead.follow_up_date = None

        db.session.commit()
        flash('Lead updated successfully!', 'success')
        return redirect(url_for('leads.index'))

    return render_template('leads/edit.html', lead=lead)


@leads_bp.route('/delete/<int:lead_id>')
@login_required
def delete( lead_id ):
    lead = Lead.query.filter_by(id=lead_id, user_id=current_user.id).first_or_404()
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted successfully!', 'success')
    return redirect(url_for('leads.index'))