"""
Created by Analitika at 03/09/2024
contact@analitika.fr
"""
# External imports
import os
from docx import Document

# Internal imports
from config import DATA_DIR


def extract_text_from_docx(docx_path):
    # Load the document
    doc = Document(docx_path)

    # Initialize an empty string for the full text
    full_text = []

    # Iterate over each paragraph in the document
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    # Join all the paragraphs with a newline character
    return "\n".join(full_text)


def main():
    # Example usage:
    docx_path = os.path.join(DATA_DIR, "A00388 - safety stock.docx")
    text = extract_text_from_docx(docx_path)

    output_path = docx_path.replace(".docx", ".json")
    # Print the extracted text
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)


if __name__ == "__main__":

    main()
