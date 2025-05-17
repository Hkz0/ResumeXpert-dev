from flask import Flask
from flask import jsonify, request, session
from flask_cors import CORS

from ai import analyze
from fileparser import pdf_processing
from jobs import JSearch

#db
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# sqli
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
CORS(app)

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
 
 # ranking upload
@app.route("/upload-ranking", methods=["POST"])
def uploadRanking():
    if "files" not in request.files:
        return jsonify({
            "status": "error",
            "message": "no files"
        }), 400

    if not request.form.get("job_desc"):
        return jsonify({
            "status": "error",
            "message": "no job_desc"
        }), 400

    files = request.files.getlist("files")
    job_desc = request.form.get("job_desc")

    resume_texts = []

    for file in files:
        if file and file.filename.endswith(".pdf"):
            text = pdf_processing(file)
            resume_texts.append({
                "filename": file.filename,
                "text": text
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"{file.filename} is not a PDF"
            }), 400

    return jsonify({
        "job_desc_text": job_desc,
        "resumes": resume_texts
    }), 200

 
if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     