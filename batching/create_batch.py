"""
Created by Analitika at 03/09/2024
contact@analitika.fr
"""
import json
import os
from time import sleep
from openai import OpenAI
from loguru import logger
from datetime import datetime

# Internal imports
from config import (
    DATA_DIR,
    COMPLETIONS_MODEL,
    RAW_DATA_FOLDER,
    BATCH_OUTPUT_FOLDER,
    OPENAI_API_KEY,
)
from tools import S3Manager


class BatchManager:
    json_file = None
    batch_id = None
    client = OpenAI(api_key=OPENAI_API_KEY)

    def __init__(self, batch_name: str):
        self.bucket = S3Manager()
        self.files = self.bucket.get_available_files(RAW_DATA_FOLDER)
        self.batch_name = batch_name

    def generate_json_batch(self):
        json_data = []

        for idx, file_ in enumerate(self.files):
            content = self.bucket.download_from_s3(file_, RAW_DATA_FOLDER)
            if content is None:
                continue

            # Construct the prompt
            prompt = f"""
                ### Instructions:
                1. Identify and structure the content according to the sections defined by headings (H1, H2, H3, H4).
                2. For each section, create an object with the following fields:
                   - **h_title**: The heading of the section.
                   - **main_title**: The highest-level title for the article (typically H1).
                   - **level**: The heading level (1 for H1, 2 for H2, etc.).
                   - **content**: An array of content objects, where each object has:
                     - **text**: The text content following the heading.
                     - **url**: Set to null unless there is a URL associated with the text.
                     - **urls**: Set to null unless there are multiple URLs associated with the text.
                3. Group all related content under the appropriate heading levels.
                4. Do not convert bullet points into JSON arrays; show them as text.
                5. Ensure that all text following the headings is included in the correct "content" field.
                6. Maintain the structure even when the text contains nested subsections.

                ### Text to convert:

                {content}
                """

            custom_idx = file_  # use something easy to track back to the DB

            # Create the JSON object for this entry
            json_entry = {
                "custom_id": f"{custom_idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": f"{COMPLETIONS_MODEL}",  # "gpt-3.5-turbo-0125",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt.strip()},
                    ],
                    # "max_tokens": 1000,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
            }

            # Add the JSON object to the list
            json_data.append(json_entry)

        self.json_file = os.path.join(DATA_DIR, "raw", "batch_prompts.jsonl")
        # Write the list of JSON objects to a JSONL file
        with open(self.json_file, "w", encoding="utf-8") as jsonl_file:
            for entry in json_data:
                jsonl_file.write(json.dumps(entry) + "\n")

        print("JSONL Data as has been created successfully.")
        return

    def send_batch_request(self):
        # 1. Check if data is present
        if self.json_file is None:
            logger.error("JSON data is empty")
            return
        # 2. Uploading Your Batch Input File
        # Serialize the content to a JSON string and encode it into bytes
        batch_input_file = self.client.files.create(
            file=open(self.json_file, "rb"), purpose="batch"
        )

        # 3. Creating the Batch task
        batch_input_file_id = batch_input_file.id
        batch_task = self.client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": self.batch_name},
        )
        self.batch_id = batch_task.id
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_id_filename = os.path.join(
            DATA_DIR, "batch_ids", f"{current_time}-batch_id.txt"
        )
        with open(batch_id_filename, "w") as file:
            file.write(self.batch_id)

        logger.info(f"Batch task ID: {self.batch_id}")

        return

    def retrieve_results(self, sleep_time: int = 60, batch_task_id: str = None):
        # 4. Checking the Status of a Batch
        if batch_task_id is not None:
            self.batch_id = batch_task_id

        batch_ = self.client.batches.retrieve(self.batch_id)

        while batch_manager.check_batch_status():
            sleep(sleep_time)

        if batch_.status != "completed":
            logger.info(f"Batch is not completed yet, status {batch_.status}")
            return

        # 5. Retrieving the Results
        output_file_id = batch_.output_file_id
        if output_file_id is None:
            logger.error("No output available")
            output_file_id = batch_.error_file_id
            if output_file_id is None:
                logger.error("No error file available, error Unknown")
                return

        # Specify the file path where you want to save the JSON
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{current_time}_{self.batch_id}.jsonl"

        file_response = self.client.files.content(output_file_id)
        json_bytes = file_response.text.encode("utf-8")
        # Upload the JSONL file to S3 with "text/plain" content type for better browser display
        c_type = "text/plain"  # for better browser display, not "application/x-ndjson"
        self.bucket.upload_to_s3(
            filename, json_bytes, BATCH_OUTPUT_FOLDER, content_type=c_type
        )
        logger.info(f"Task {self.batch_id} finished")

        # # Write the string directly to the file
        # with open(file_path, "w", encoding="utf-8") as json_file:
        #     json_file.write(output_data)
        #
        # print(f"Output saved to {file_path}")

        return

    def check_batch_status(self):
        batch_ = self.client.batches.retrieve(self.batch_id)
        # todo: add additional checks
        return batch_.status != "completed"


if __name__ == "__main__":
    batch_manager = BatchManager("20240903_ANK-TEST-1")
    # batch_manager.generate_json_batch()
    # batch_manager.send_batch_request()
    batch_manager.retrieve_results(batch_task_id="batch_m2nkzwZjq0vKfxxJ6BEiqWnD")
