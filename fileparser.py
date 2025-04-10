import pymupdf
import io
from flask import jsonify, request

def pdf_processing(file):
    
    #store file in memory
    pdf_memory = io.BytesIO(file.read())
    
    doc = pymupdf.open(stream=pdf_memory, filetype="pdf")
    
    for page in doc:
        text = page.get_text()
        
    return text
    


