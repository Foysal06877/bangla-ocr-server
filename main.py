from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

app = FastAPI()

# Blogger থেকে call করার জন্য CORS খুলে দিতে হবে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # চাইলে পরে নিজের ডোমেইন বসাতে পারেন
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Bangla OCR server running"}

@app.post("/ocr")
async def ocr_pdf(file: UploadFile = File(...), lang: str = "ben+eng"):
    try:
        data = await file.read()
        pdf = fitz.open(stream=data, filetype="pdf")
        result = []
        for i, page in enumerate(pdf):
            # পেজকে ছবিতে রূপান্তর (৩০০ DPI — ভালো মান)
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            # OCR চালাও
            text = pytesseract.image_to_string(img, lang=lang)
            result.append({"page": i + 1, "text": text.strip()})
        return JSONResponse({"pages": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
