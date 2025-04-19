import pymupdf
import io
from flask import jsonify, request
from unidecode import unidecode


def pdf_processing(file):
    
    #store file in memory
    pdf_memory = io.BytesIO(file.read())
    
    doc = pymupdf.open(stream=pdf_memory, filetype="pdf")
    text = ""
    
    
    for page in doc:
        
        output = page.get_text("blocks")
        prevBlockId = 0 # mark prev b id
    
        for block in output:
            
           if block[6] == 0: # text only 
                if prevBlockId != block[5]:
                    text += "\n"   
                text += unidecode(block[4])
    
    #parserTest(all_pages,doc)              
        
    return text

def parserTest(all_pages,doc):
    
    for page_num, page in enumerate(doc, start=1):
        page_dict = page.get_text("dict")
        blocks = page_dict.get("blocks", [])
        page_data = []

        for b in blocks:
            if "lines" not in b:
                continue

            for line in b["lines"]:
                for span in line["spans"]:
                    text = unidecode(span["text"]).strip()
                    if not text:
                        continue

                    font = span["font"]
                    size = span["size"]
                    is_bold = "Bold" in font or "bold" in font.lower()
                    is_italic = "Italic" in font or "Oblique" in font or "italic" in font.lower()

                    span_data = {
                        "text": text,
                        "font": font,
                        "size": size,
                        "bold": is_bold,
                        "italic": is_italic
                    }
                    page_data.append(span_data)

        all_pages.append({
            "page": page_num,
            "spans": page_data
        })

    return all_pages
    

