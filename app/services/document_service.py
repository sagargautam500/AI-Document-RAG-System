
import fitz


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""

    pdf_document = fitz.open(
        stream=file_content,
        filetype="pdf"
    )

    extracted_text = ""

    for page in pdf_document:
        extracted_text += page.get_text() + "\n"

    pdf_document.close()

    return extracted_text.strip()


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file."""

    return file_content.decode("utf-8").strip()
