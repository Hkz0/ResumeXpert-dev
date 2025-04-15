from flask import Flask
from flask import jsonify, request
from flasgger import Swagger
from flask_cors import CORS
from ai import analyze
from fileparser import pdf_processing



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
        
        return jsonify({"status" : "OK",
                        "message" : "upload successfull",
                        "filename": file.filename,
                        "job description" : job_desc,
                        "content": text}), 200
        
    
    return jsonify({"status" : "error",
                    "message" : "Upload failed"}), 400
        


                    
    
# gemini test
@app.route("/ai", methods=["POST"])
def geminiTest():
    return analyze()
    
 
 
if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     