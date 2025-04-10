 # ResumeXpert-dev
 
 - A tool to quickly improve or tailor job seekers resume from a job description

## Features

### REST API Architecture
- Independent backend architecture designed to use with a REST frontend client
- API endpoint documentation soon

### PDF Parsing
- Resume file parsing with PyMuPDF

### AI Powered Analyzing
- Gemini API

### Matching Job Listings
- Try to find matching jobs from resume with Google jobs API (SerpAPI)



## Techologies
- Flask
- PyMuPDF
- SerpAPI

## Usage
- Make a python enivorment with file name `.venv`
```python
python -m venv .venv
```
- activate it
- then install all packages dependency with `pip`
```python
pip install -r requirements.txt
```
## Run
- to run the flask app
```python
python api.py
```