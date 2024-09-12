from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

# Define your models here
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    course_of_study = db.Column(db.String(100))
    skills = db.Column(db.Text)
    bio = db.Column(db.Text)
    location_of_interest = db.Column(db.String(100))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    industry = db.Column(db.String(100))
    about = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    start_date = db.Column(db.Date)
    duration = db.Column(db.String(50))
    requirements = db.Column(db.Text)