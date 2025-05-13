# API Documentation
> API Documentation for the ResumeXpert endpoints
## **POST** `/upload`

### **Description:**
Uploads a PDF file and extracts the text from it. The API requires a job description to be included in the request.

### **Request:**
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: The PDF file to be uploaded. (Required)
  - `job_desc`: A description of the job to associate with the resume. (Required)

### **Responses:**
- **200 OK**: Returns the extracted text from the resume and the provided job description.
  - **Response Body Example**:
    ```json
    {
      "job_desc_text": "Software Developer",
      "resume_text": "Extracted text from the resume PDF."
    }
    ```

- **400 Bad Request**: Missing `file` or `job_desc`, or unsupported file type.
  - **Response Body Example** (when no file is provided):
    ```json
    {
      "status": "error",
      "message": "no file"
    }
    ```

  - **Response Body Example** (when no job description is provided):
    ```json
    {
      "status": "error",
      "message": "no job_desc"
    }
    ```

  - **Response Body Example** (when an unsupported file type is uploaded):
    ```json
    {
      "status": "error",
      "message": "Upload failed"
    }
    ```

### **Notes:**
- Only PDF files are supported for upload.
- The `job_desc` field must be provided as part of the form data.


## **POST** `/analyze`
### **Description**
- Analyzes **parsed resume and job description text** from `/upload` endpoint

### **Request:**
- **Content-Type**: `application/json`
- **Body**:
  - `resume_text`: The text extracted from the resume. (Required)
  - `job_desc_text`: The job description text. (Required)
  - preferably from `/upload endpoint`

### **Request Example:**
```json
{
  "resume_text": "Extracted text from the resume PDF.",
  "job_desc_text": "Job description text for the position."
}
```

### **Responses:**
- **200 OK:** Returns an analysis of the resume and job description, including match score, missing/extra keywords, suggested improvements, and career recommendations.
	- **Response Body Example:**

```json
{
  "match_score": 85,
  "missing_keywords": ["communication", "leadership"],
  "extra_keywords_to_add": ["project management"],
  "suggested_improvements": [
    {
      "issue": "Lack of specific examples of leadership experience",
      "suggestion": "Include specific leadership projects or roles you've undertaken."
    }
  ],
  "career_recommendations": {
    "best_match": {
      "title": "Project Manager",
      "reason": "Your experience with leading teams and managing projects makes this role a great fit."
    },
    "other_careers": [
      {
        "title": "Product Manager",
        "reason": "Your skills in project coordination and team management align with the responsibilities of a product manager."
      }
    ]
  }
}

```      

- **400 Bad Request:** Missing `resume_text` or `job_desc_text`
	- **Response Body Example:**
```json
{
  "status": "error",
  "message": "missing data"
}
```

### **Notes:**
-  Both `resume_text` and `job_desc_text` are required for a successful analysis.
- The output includes a match score from 0 to 100, along with recommendations for improving the resume and possible career paths.

## **POST** `/job-matching`
- Returns a list of job postings
### **Request:**
- **Content-Type**: `application/json`
- **Body**:
	- `job_title`: title from `best_match` in `/analyze` **endpoint** . (Required)
	- `job_location`: The job location (city). (optional)
	- preferably from `/analyze` **endpoint** inside 
```json
"career_recommendations": {
    "best_match": {
      "title": "Project Manager",
```

### **Request Example:**
```json
{
	"job_title": "It Internship",
	"location" : "Shah Alam"
}
```

### **Response**
- **200 OK** - Returns a list of job matches retrieved and filtered from the JSearch API.
```json
[
  {
    "title": "Software Engineer",
    "location": "Kuala Lumpur, MY",
    "company": "ABC Tech",
    "description": "We are looking for a Software Engineer...",
    "apply_options": [
      "https://company.com/careers/job123"
    ]
  },
  ...
]

```

- **400 Error** - Returned when `job_title` is missing in the request.
```json
{
  "status": "error",
  "message": "missing job_title"
}
```

