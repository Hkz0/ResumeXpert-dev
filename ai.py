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
        
        prompt1 = f"""
        Analyze the provided resume against the job description and provide comprehensive feedback in JSON format.

        Note: The resume is provided as plain text only. It does not include any formatting (e.g., bold, italics, font sizes, layout styles). Do not make any assumptions about formatting, design, or visual layout.

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
                "keyword_optimization": "string"
            }},
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
        
        prompt2 = f"""
        Analyze the provided resume against the job description and provide concise feedback in JSON format.

        Note: The resume is plain text only. Do not make any assumptions about formatting or layout.

        If a section has no relevant feedback, return a default placeholder string (e.g., "None" or "No issues found") instead of null or empty lists.

        # Resume:
        {resume_text}

        # Job Description:
        {job_desc_text}

        Provide a JSON response with the following structure:
        {{
            "match_score": 0-100,
            "missing_keywords": ["keyword1", "keyword2", ...] or ["None"],
            "extra_keywords_to_add": ["keyword1", "keyword2", ...] or ["None"],
            "suggested_improvements": [
                {{
                    "issue": "string",
                    "suggestion": "string"
                }}
            ] or ["No issues found"],
            "career_recommendations": {{
                "best_match": {{
                    "title": "Best Job Title",
                    "reason": "Brief explanation why this is the top recommendation based on skills/experience"
                }},
                "other_careers": [
                    {{
                        "title": "Alternative Job Title",
                        "reason": "Brief explanation why this role is also suitable"
                    }},
                    ...
                ]
            }}
        }}

        Guidelines for career_recommendations:
        - Select one "best_match" that fits the candidate most strongly.
        - Then suggest 2-4 "other_careers" that are also good matches.
        - **Prefer broadly recognized, high-demand job titles** (e.g., "Software Developer", "Marketing Specialist") over highly specific/niche titles unless the resume is extremely specialized.
        - Keep explanations brief but meaningful.
        
        Respond ONLY with valid JSON - no extra text.
        """




        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt2)
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