from flask import Flask
from flask import jsonify, request

#from ai import analyze
from fileparser import pdf_processing

app = Flask(__name__)

@app.route("/")
def test():
    return "<h1>Test</h1>"

# upload endpoint
@app.route("/upload", methods=["POST"])
def upload_resume():
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # pdf only
    if file and file.filename.endswith(".pdf"):
        
        text = pdf_processing(file)
        
        return jsonify({"filename": file.filename,
                        "content": text}), 200
    
    return jsonify({"error": "Upload failed"}), 400
        


                    
    
# gemini test
#@app.route("/ai", methods=["POST"])
#def geminiTest():
#    return analyze()
    
 
 
if __name__ == "__main__":
     app.run(host="0.0.0.0", debug=True)
     