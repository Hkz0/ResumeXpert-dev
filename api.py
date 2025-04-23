from flask import Flask
from flask import jsonify, request
from flasgger import Swagger
from flask_cors import CORS

from ai import analyze
from fileparser import pdf_processing
from jobs import job_listings


app = Flask(__name__)
CORS(app)

#init swagger
swagger = Swagger(app, template_file='swagger.yml')

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
    
    # pdf only
    if file and file.filename.endswith(".pdf"):
        
        text = pdf_processing(file)
        
        return jsonify({"job_desc_text" : job_desc,
                        "resume_text"   : text}), 200
        # return jsonify(text), 200

        
    
    return jsonify({"status" : "error",
                    "message" : "Upload failed"}), 400
          
    
# analyze endpoint
@app.route("/analyze", methods=["POST"])
def geminiTest():
    
    data = request.get_json()
    resume_text = data.get('resume_text')
    job_desc_text = data.get('job_desc_text')
    
    if not resume_text or not job_desc_text:
        return jsonify({'status': 'error',
                        'message': 'missing data'}), 400

    
    result = analyze(resume_text,job_desc_text)
    return result
    

# job matching endpoint
@app.route("/job-matching", methods=["GET"])
def job_matching():
    job_result = job_listings("Cybersecurity", "Shah Alam")
    return jsonify(job_result)
 
 
if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     