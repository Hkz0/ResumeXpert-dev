from flask import Flask
from flask import jsonify, request, session
from flask_cors import CORS

from ai import analyze, rank_resumes
from fileparser import pdf_processing
from jobs import JSearch

#db
from models import db, User, Job, Ranking
from werkzeug.security import generate_password_hash, check_password_hash

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'http://localhost:5500',
    'http://localhost:5000',
    'https://resumexpert.onrender.com',
    'http://localhost:5173',
    'https://resumexpert-ai.vercel.app'
    ])
db.init_app(app)

with app.app_context():
    db.create_all()
    
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        # Store user info in session after successful login
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 400
    
@app.route('/api/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/check-session')
def check_session():
    if 'user_id' in session:
        return jsonify({'loggedIn': True, 'username': session['username']}), 200
    return jsonify({'loggedIn': False}), 200


@app.route("/")
def test():
    return jsonify({"status" : "OK",
                    "message" : "API Online"}), 200

# upload endpoint
@app.route("/upload", methods=["POST"])
def upload():
    
    if "file" not in request.files:
        return jsonify({"status" : "error",
                        "message" : "no file"}), 400
    
    if not request.form.get("job_desc"):
        return jsonify({"status" : "error",
                        "message" : "no job_desc"}), 400
    
    file = request.files['file']
    job_desc = request.form.get('job_desc')
    
    if file and file.filename.endswith(".pdf"):
        
        text = pdf_processing(file)
        
        return jsonify({"job_desc_text" : job_desc,
                        "resume_text"   : text}), 200

    return jsonify({"status" : "error",
                    "message" : "Upload failed"}), 400
          
    
# analyze endpoint
@app.route("/analyze", methods=["POST"])
def geminiAnalyze():
    
    data = request.get_json()
    resume_text = data.get('resume_text')
    job_desc_text = data.get('job_desc_text')
    
    if not resume_text or not job_desc_text:
        return jsonify({'status': 'error',
                        'message': 'missing data'}), 400

    
    result = analyze(resume_text,job_desc_text)
    return result, 200
    

# job matching endpoint
@app.route("/job-matching", methods=["POST"])
def job_matching():
    
    data = request.get_json()
    job_title = data.get('job_title')
    job_location = data.get('job_location')
    
    if not job_title:
        return jsonify({'status': 'error',
                        'message': 'missing job_title'}), 400
        
    job_result = JSearch(job_title, job_location)
    return jsonify(job_result), 200
 
 # # # Ranking Endpoints # # #

# Create new job position
@app.route("/api/jobs", methods=["POST"])
def create_job():
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    data = request.get_json()
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({
            "status": "error",
            "message": "Missing job title or description"
        }), 400

    new_job = Job(
        title=data['title'],
        description=data['description'],
        recruiter_id=session['user_id']
    )
    
    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Job created successfully",
        "job_id": new_job.id
    }), 201

# Get all jobs for logged-in recruiter
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    jobs = Job.query.filter_by(recruiter_id=session['user_id']).all()
    return jsonify({
        "jobs": [{
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "created_at": job.created_at.isoformat(),
            "rankings_count": len(job.rankings)
        } for job in jobs]
    }), 200

# Modified rank-resumes endpoint to get job_id from URL
@app.route("/rank-resumes/<int:job_id>", methods=["POST"])
def rank_resumes_endpoint(job_id):
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if "files" not in request.files:
        return jsonify({
            "status": "error",
            "message": "no files"
        }), 400

    # Verify job belongs to user
    job = Job.query.filter_by(id=job_id, recruiter_id=session['user_id']).first()
    if not job:
        return jsonify({
            "status": "error",
            "message": "Job not found or unauthorized"
        }), 404

    files = request.files.getlist("files")
    job_desc_text = job.description
    
    resume_texts = []
    filenames = []

    for file in files:
        if file and file.filename.endswith(".pdf"):
            text = pdf_processing(file)
            resume_texts.append(text)
            filenames.append(file.filename)
        else:
            return jsonify({
                "status": "error",
                "message": f"{file.filename} is not a PDF"
            }), 400
    
    # Get rankings from AI
    rankings = rank_resumes(resume_texts, job_desc_text)
    
    # Save rankings to database
    if rankings and 'rankings' in rankings:
        for i, ranking in enumerate(rankings['rankings']):
            new_ranking = Ranking(
                job_id=job_id,
                candidate_name=ranking.get('candidate_name'),
                score=ranking.get('score'),
                summary=ranking.get('summary'),
                filename=filenames[i]
            )
            db.session.add(new_ranking)
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Resumes uploaded and ranked successfully",
            "job_id": job_id,
            "files_processed": len(filenames)
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to process rankings"
        }), 500

# Get rankings for a specific job
@app.route("/api/jobs/<int:job_id>/rankings", methods=["GET"])
def get_job_rankings(job_id):
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    # Verify job belongs to user
    job = Job.query.filter_by(id=job_id, recruiter_id=session['user_id']).first()
    if not job:
        return jsonify({
            "status": "error",
            "message": "Job not found or unauthorized"
        }), 404

    rankings = Ranking.query.filter_by(job_id=job_id).order_by(Ranking.score.desc()).all()
    return jsonify({
        "job_title": job.title,
        "rankings": [{
            "id": r.id,
            "candidate_name": r.candidate_name,
            "score": r.score,
            "summary": r.summary,
            "filename": r.filename,
            "created_at": r.created_at.isoformat()
        } for r in rankings]
    }), 200

# Delete a specific ranking
@app.route("/api/jobs/<int:job_id>/rankings/<int:ranking_id>", methods=["DELETE"])
def delete_ranking(job_id, ranking_id):
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    # Verify job belongs to user
    job = Job.query.filter_by(id=job_id, recruiter_id=session['user_id']).first()
    if not job:
        return jsonify({
            "status": "error",
            "message": "Job not found or unauthorized"
        }), 404

    # Find and delete the ranking
    ranking = Ranking.query.filter_by(id=ranking_id, job_id=job_id).first()
    if not ranking:
        return jsonify({
            "status": "error",
            "message": "Ranking not found"
        }), 404

    db.session.delete(ranking)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Candidate ranking deleted successfully"
    }), 200

# Delete a specific job
@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    if 'user_id' not in session:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    # Verify job belongs to user
    job = Job.query.filter_by(id=job_id, recruiter_id=session['user_id']).first()
    if not job:
        return jsonify({
            "status": "error",
            "message": "Job not found or unauthorized"
        }), 404

    # Optionally delete associated rankings
    rankings = Ranking.query.filter_by(job_id=job_id).all()
    for ranking in rankings:
        db.session.delete(ranking)

    db.session.delete(job)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Job and associated rankings deleted successfully"
    }), 200

if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     