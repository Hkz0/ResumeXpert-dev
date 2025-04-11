import pymupdf
import io
from flask import jsonify, request
from unidecode import unidecode


def pdf_processing(file):
    
    #store file in memory
    pdf_memory = io.BytesIO(file.read())
    
    doc = pymupdf.open(stream=pdf_memory, filetype="pdf")
    text = ""
    #for page in doc:
    #    text = page.get_text()
    
    for page in doc:
        
        output = page.get_text("blocks")
        prevBlockId = 0 # mark prev b id
        
        for block in output:
            
           if block[6] == 0: # text only
               
                if prevBlockId != block[5]:
                    text += "\n"
                    
                text += block[4]
                      
        
    return text
    


