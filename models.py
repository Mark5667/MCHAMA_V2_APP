from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'member'
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    id_number = db.Column(db.String(20), unique=True)
    dob = db.Column(db.String(20))
    age = db.Column(db.Integer)
    registration_date = db.Column(db.String(20))

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    date = db.Column(db.String(20))

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))  # 'pending', 'approved', 'rejected'
