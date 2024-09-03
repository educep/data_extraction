"""
Created by Analitika at 03/09/2024
contact@analitika.fr
"""
import json
import os
from openai import OpenAI

# Internal imports
from config import DATA_DIR, COMPLETIONS_MODEL

files = [
    os.path.join(DATA_DIR, "A00388 - safety stock.json"),
    os.path.join(DATA_DIR, "A00388 - safety stock.json"),
]

json_data = []
for idx, file_ in enumerate(files):
    with open(file_, "r", encoding="utf-8") as file:
        content = file.read()

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

    # 6. When a formula or quote is encountered, label it as such in the JSON structure.

    custom_idx = idx  # use something easy to track back to the DB

    # Create the JSON object for this entry
    json_entry = {
        "custom_id": f"request-{custom_idx}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": f"{COMPLETIONS_MODEL}",  # "gpt-3.5-turbo-0125",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt.strip()},
            ],
            "max_tokens": 1000,
        },
    }

    # Add the JSON object to the list
    json_data.append(json_entry)

prompts_file = os.path.join(DATA_DIR, "20240903_batch_prompts-1.jsonl")
# Write the list of JSON objects to a JSONL file
with open(prompts_file, "w", encoding="utf-8") as jsonl_file:
    for entry in json_data:
        jsonl_file.write(json.dumps(entry) + "\n")

print("JSONL file has been created successfully.")

# 2. Uploading Your Batch Input File
client = OpenAI()
batch_input_file = client.files.create(file=open(prompts_file, "rb"), purpose="batch")
# 3. Creating the Batch task
batch_input_file_id = batch_input_file.id
batch_task = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={"description": "ANK Batch"},
)

# 4. Checking the Status of a Batch
batch_task_id = batch_task.id
batch_status = client.batches.retrieve(batch_task_id)

# 5. Retrieving the Results
output_file_id = batch_status.output_file_id
file_response = client.files.content(output_file_id)
output_data = file_response.text

# Specify the file path where you want to save the JSON
file_path = os.path.join(DATA_DIR, "20240903_batch_outputs-1.jsonl")

# Write the string directly to the file
with open(file_path, "w", encoding="utf-8") as json_file:
    json_file.write(output_data)

print(f"Output saved to {file_path}")
