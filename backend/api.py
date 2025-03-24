from flask import Flask
from flask import jsonify, request
import google.generativeai as genai
import pdfplumber
import os

app = Flask(__name__)

# resume file location
UPLOAD_FOLDER = "upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.route("/")
def test():
    return "<h1>Test</h1>"

# upload endpoint
@app.route("/upload", methods=["POST"])
def upload_resume():
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file and file.filename.endswith(".pdf"):
        
        file_path = os.path.join (UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        text = extract_pdf(file)
        return jsonify({"filename": file.filename,
                        "content": text}), 200
    
    return jsonify({"error": "Upload failed"}), 400
        

# parse pdf to text       
def extract_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            
            if page_text:
                text += page_text + "\n"
    return text.strip()
                    
    
    
 
 
if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     