from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    jobs = db.relationship('Job', backref='recruiter', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rankings = db.relationship('Ranking', backref='job', lazy=True)

class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    candidate_name = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)