from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.app.services.pdf_service import extract_text_from_pdf


app = FastAPI(
    title="RAG Document Chatbot API",
    description="Backend API for uploading and chatting with documents.",
    version="1.0.0"
)


# Main project uploads folder
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "RAG Document Chatbot API is running"
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    # Check that a filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    # Validate extension
    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Check PDF header
    header = await file.read(5)
    await file.seek(0)

    if not header.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    stored_filename = f"{document_id}.pdf"

    file_path = UPLOAD_DIR / stored_filename

    # Save PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Extract text
        pages = extract_text_from_pdf(file_path)

    except Exception as error:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"Could not process PDF: {str(error)}"
        )

    return {
        "document_id": document_id,
        "filename": file.filename,
        "total_pages": len(pages),
        "pages": pages
    }

