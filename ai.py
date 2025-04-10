from dotenv import load_dotenv
import google.generativeai as genai
from flask import jsonify, request
import os
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

def analyze():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return  jsonify({"response": response.text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500