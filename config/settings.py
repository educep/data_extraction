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

# FILENAMES
SITEMAP_FILENAME = "sitemap.xml"  # site's sitemaps
SITEMAP_URL_FILENAME = "sitemap_urls.json"  # list of urls in site's sitemaps
FILE_SUFFIX = "XXSLUGXX"
ONPAGE_FILENAME = f"onpage_{FILE_SUFFIX}"  # generic name, no extension
CONTENT_FILENAME = f"content_{FILE_SUFFIX}"  # generic name, no extension

# OPENAI IDENTIFIERS AND PARAMETERS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID", None)
COMPLETIONS_MODEL = os.getenv("COMPLETIONS_MODEL", None)
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", None)

# Time format for filenames
TIME_FORMAT = "%Y-%m-%d_%Hpp%M"

# DATABASE
main_database_user = os.getenv("DATABASE_USER", None)
main_database_password = os.getenv("DATABASE_PASSWORD", None)
main_database_name = os.getenv("DATABASE_NAME", None)
main_database_host = os.getenv("DATABASE_HOST", None)
main_database_port = os.getenv("DATABASE_PORT", None)
main_database_ssl = os.getenv("DATABASE_SSL", None)

if __name__ == "__main__":
    logger.info("Done")
