from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def extract_pdf_text(file_path: str):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text.strip()
        })

    return pages


def chunk_pages(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    chunk_index = 0

    for page in pages:
        page_text = page["text"]

        if not page_text:
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk_text in page_chunks:
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page["page_number"],
                "text": chunk_text
            })

            chunk_index += 1

    return chunks