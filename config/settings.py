"""
Created by Analitika at 24/07/2024
contact@analitika.fr
"""

# External imports
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJ_ROOT / "data"
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

# Environment variables for AWS credentials and configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_REGION = os.getenv("AWS_REGION", None)
AWS_FOLDER = os.getenv("AWS_FOLDER", None)
S3_BUCKET_NAME = os.getenv("AWS_BUCKET", None)
RAW_DATA_FOLDER = "raw_content"
STRUCTURED_DATA_FOLDER = "structured_content"
BATCH_OUTPUT_FOLDER = "batch_output"

# OPENAI IDENTIFIERS AND PARAMETERS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
COMPLETIONS_MODEL = os.getenv("COMPLETIONS_MODEL", None)

if __name__ == "__main__":
    print(COMPLETIONS_MODEL)
