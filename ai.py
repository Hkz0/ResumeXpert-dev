from dotenv import load_dotenv
import google.generativeai as genai
from flask import jsonify, request
import os
import json
import re
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze(resume_text,job_desc_text):
    try:
        #prompt = data.get("prompt", "")
        
        #if not prompt:
        #    return jsonify({"error": "prompt is required"}), 400
        
        prompt = f"""
        Analyze the provided resume against the job description and provide comprehensive feedback in JSON format.
        
        # Resume:
        {resume_text}
        
        # Job Description:
        {job_desc_text}
        
        Based on your analysis, provide a detailed JSON response with the following structure:
        {{
            "match_score": 0-100,
            "key_matches": [
                {{
                    "skill": "string",
                    "description": "string",
                    "relevance": "high/medium/low"
                }}
            ],
            "missing_qualifications": [
                {{
                    "qualification": "string",
                    "importance": "critical/important/nice-to-have",
                    "suggestion": "string"
                }}
            ],
            "suggested_improvements": [
                {{
                    "section": "string",
                    "issue": "string",
                    "suggestion": "string",
                    "priority": "high/medium/low"
                }}
            ],
            "ats_feedback": {{
                "score": 0-100,
                "issues": [
                    {{
                        "issue": "string",
                        "solution": "string"
                    }}
                ],
                "keyword_optimization": "string"
            }},
            "formatting_issues": [
                {{
                    "issue": "string",
                    "solution": "string"
                }}
            ],
            "keyword_analysis": {{
                "keywords": [
                    {{
                        "keyword": "string", 
                        "present": true/false,
                        "context": "string",
                        "recommendation": "string"
                    }}
                ]
            }}
        }}
        
        Respond ONLY with valid JSON - do not include any explanatory text before or after the JSON.
        """


        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        #return  jsonify({"response": response.text})
        return gemini_response_parse(response.text)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def gemini_response_parse(text):
        
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if match:
            json_data = match.group(0)
            return json.loads(json_data)
        else:
            raise ValueError("No valid JSON found in response.")
        #print("Raw response:", text)
        #return json.loads(text)
    except json.JSONDecodeError:
        print("Error parsing response. Please check the response format.")
        return None
    except Exception as e:
       print(f"Unexpected error: {str(e)}")
       return None