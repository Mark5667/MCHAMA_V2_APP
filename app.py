from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import func

import os

app = Flask(__name__)
app.secret_key = 'secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'member'

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    id_number = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    age = db.Column(db.String(5))
    registration_date = db.Column(db.String(20))

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    amount = db.Column(db.Float)
    date = db.Column(db.String(20))

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))

# --- Create Tables & Admin ---
def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                mobile_number='0700000000',
                password=hashed_pw,
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

create_tables()

# --- Routes ---
@app.route('/')
def home():
    return redirect('/splash')  # ✅ New

@app.route('/splash')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        mobile = request.form['mobile_number']
        password = request.form['password']

        user = User.query.filter_by(mobile_number=mobile).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin/dashboard')
            elif user.role == 'member':
                return redirect('/member/dashboard')
            else:
                error = 'Unknown role. Contact support.'
        else:
            error = 'Invalid mobile number or password'

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    member_count = Member.query.count()
    total_contributions = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
    pending_loans = Loan.query.filter_by(status='pending').count()
    return render_template('dashboard.html', member_count=member_count, total_contributions=total_contributions, pending_loans=pending_loans)
@app.route('/register_member', methods=['GET', 'POST'])
def register_member():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    error = ''
    if request.method == 'POST':
        name = request.form['name']
        id_number = request.form['id_number']
        dob = request.form['dob']
        age = request.form['age']
        registration_date = request.form['registration_date']

        # ✅ Check if the member already exists
        existing = Member.query.filter_by(id_number=id_number).first()
        if existing:
            error = f"⚠️ Member with ID number {id_number} already exists."
        else:
            try:
                member = Member(
                    name=name,
                    id_number=id_number,
                    dob=dob,
                    age=age,
                    registration_date=registration_date
                )
                db.session.add(member)
                db.session.commit()
                return redirect('/members')
            except Exception as e:
                db.session.rollback()
                error = "⚠️ Failed to register member. Please try again."

    return render_template('register_member.html', error=error)



@app.route('/members')
def view_members():
    if 'user' not in session:
        return redirect('/login')

    members = Member.query.all()
    return render_template('members.html', members=members)
@app.route('/add_contribution', methods=['GET', 'POST'])
def add_contribution():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        member_name = request.form['member_name']
        amount = request.form['amount']
        date = request.form['date']

        member = Member.query.filter_by(name=member_name).first()

        if not member:
            return "⚠️ Member not found. Please check the name or register the member first."

        new_contribution = Contribution(member_id=member.id, amount=amount, date=date)
        db.session.add(new_contribution)
        db.session.commit()
        return redirect('/contributions')

    return render_template('add_contribution.html')

@app.route('/request_loan', methods=['GET', 'POST'])
def request_loan():
    if 'user' not in session:
        return redirect('/login')

    members = Member.query.all()

    if request.method == 'POST':
        member_id = request.form['member_id']
        amount = request.form['amount']

        loan = Loan(member_id=member_id, amount=amount, status='pending')
        db.session.add(loan)
        db.session.commit()
        return redirect('/loans')

    return render_template('request_loan.html', members=members)

    return render_template('add_contribution.html', members=members)
@app.route('/approve-loans')
def approve_loans():
    loans = Loan.query.filter_by(status='Pending').all()
    return render_template('approve_loans.html', loans=loans)

@app.route('/approve-loan/<int:loan_id>', methods=['POST'])
def approve_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.status = 'Approved'
        db.session.commit()
    return redirect('/approve-loans')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/goodbye')
@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')
@app.route('/contributions')
def contributions():
    all_contributions = Contribution.query.all()
    return render_template('contribute.html', contributions=all_contributions)
@app.route('/summary')
def summary():
    total_members = Member.query.count()
    total_contributions = db.session.query(func.sum(Contribution.amount)).scalar() or 0
    total_loans = db.session.query(func.sum(Loan.amount)).scalar() or 0
    return render_template("summary.html", total_members=total_members,
                           total_contributions=total_contributions, total_loans=total_loans)
@app.route('/loans')
def view_loans():
    if 'user' not in session:
        return redirect('/login')

    loans = Loan.query.join(Member).add_columns(Loan.amount, Loan.status, Member.name).all()
    return render_template('loans.html', loans=loans)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    member_count = Member.query.count()
    total_contributions = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
    pending_loans = Loan.query.filter_by(status='pending').count()

    return render_template('admin_dashboard.html',
                           member_count=member_count,
                           total_contributions=total_contributions,
                           pending_loans=pending_loans)

@app.route('/member/dashboard')
def member_dashboard():
    if 'user' not in session or session['role'] != 'member':
        return redirect('/login')

    # You can customize this more if you want member-specific data
    return render_template('member_dashboard.html', user=session['user'])


# Add your other routes (register_member, members list, contributions, etc.) here.

if __name__ == '__main__':
    app.run(debug=True)
