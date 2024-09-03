"""
Created by Analitika at 03/09/2024
contact@analitika.fr
"""
# External imports
import requests
import docx
from io import BytesIO
from loguru import logger
import pandas as pd

# Internal imports
from tools import S3Manager
from config import DATA_DIR, RAW_DATA_FOLDER


class WordDownloader:
    bucket = S3Manager()

    def __init__(self, site: str):
        self.site = site  # FR | UK to store in AWS

    def download_and_read_docx(self, file_url: str):
        response = requests.get(file_url)
        response.raise_for_status()  # Ensure the request was successful

        # Load the content into a docx.Document object
        doc = docx.Document(BytesIO(response.content))

        try:
            # Extract the text from the document
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)

            return "\n".join(full_text)
        except Exception as e:
            logger.critical(f"An error occurred {self.site} URL: {file_url}{e}")
            return None

    def store(self, content, file_id: str):
        text_bytes = content.encode("utf-8")
        folder = RAW_DATA_FOLDER + f"/{self.site}"
        self.bucket.upload_to_s3(file_id + ".txt", text_bytes, folder, "text/plain")
        logger.info(f"File {file_id} uploaded to S3")
        return


def download_raw_data():
    files_csv = pd.read_csv(DATA_DIR / "raw/docx.csv", header=None, dtype=str)

    for idx, row in files_csv.iterrows():
        id_ = row[0]
        site_ = row[1]
        url = row[2]
        word_downloader = WordDownloader(site_)
        content = word_downloader.download_and_read_docx(url)
        word_downloader.store(content, id_)

    return


if __name__ == "__main__":
    download_raw_data()
