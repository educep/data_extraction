""""
Created by Analitika at 27/03/2024
contact@analitika.fr
"""
# External imports
import gzip
import json
from io import BytesIO
from typing import Union, List
import pickle
import boto3  # AWS SDK for Python
from botocore.exceptions import ClientError
from loguru import logger

# Internal imports
from config import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME


class S3Manager:
    def __init__(self):
        """
        Initialize the S3Manager with AWS credentials.
        """
        self.s3_client = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        ).client("s3")

    def get_available_files(self, folder: str) -> List[str]:
        """
        List all files in a specific folder within an AWS S3 bucket.
        :param folder: The folder within the S3 bucket
        :return: List of file names
        """
        files = []
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME, Prefix=folder
            )
            if "Contents" in response:
                for file in response["Contents"]:
                    filename = file["Key"][len(folder) + 1 :]
                    if filename:
                        files.append(filename)

        except ClientError as e:
            logger.error(str(e))
        return files

    def upload_to_s3(
        self,
        file_name: str,
        data: bytes,
        folder: str,
        content_type: str = "application/octet-stream",
    ) -> int:
        """
        Upload a file to an AWS S3 bucket.
        :param file_name: The name of the file to be saved in S3 (without extension)
        :param data: The data to be uploaded
        :param folder: The folder within the S3 bucket where the file will be stored
        :param content_type: The content type of the file
        :return: int status code (0 for success, 1 for failure)
        """
        try:
            s3_file_key = f"{folder}/{file_name}"
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_file_key,
                Body=data,
                ContentType=content_type,
            )
            return 0
        except ClientError as e:
            logger.error(str(e))
            return 1

    def delete_object_from_s3(self, file_name: str, folder: str) -> int:
        """
        Delete an object from an AWS S3 bucket.
        :param file_name: The name of the file to be deleted from S3
        :param folder: The folder within the S3 bucket where the file is stored
        :return: int status code (0 for success, 1 for failure)
        """
        try:
            s3_file_key = f"{folder}/{file_name}"
            self.s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_file_key)
            logger.info(f"Object {s3_file_key} deleted from S3.")
            return 0
        except ClientError as e:
            logger.error(str(e))
            return 1

    def check_file_exists(self, key: str) -> bool:
        """
        Check if a file exists in an S3 bucket.
        :param key: The full key of the file in the S3 bucket
        :return: True if the file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise

    def download_from_s3(self, file_name: str, folder: str) -> Union[bytes, str, None]:
        """
        Download a file from an AWS S3 bucket, with optional decompression for gzip files.
        :param file_name: The name of the file to be downloaded from S3 (with extension)
        :param folder: The folder within the S3 bucket where the file is stored (can be composed folder/subfolder)
        :return: The file content, decompressed if it's a gzip file, or None on failure
        """
        s3_file_key = f"{folder}/{file_name}"
        if not self.check_file_exists(s3_file_key):
            logger.error(
                f"File '{s3_file_key}' does not exist in bucket '{S3_BUCKET_NAME}'."
            )
            return None

        file_stream = BytesIO()
        try:
            self.s3_client.download_fileobj(
                Bucket=S3_BUCKET_NAME, Key=s3_file_key, Fileobj=file_stream
            )
            file_stream.seek(0)
            # Handle gzip files
            if file_name.endswith(".gz"):
                with gzip.open(file_stream, "rb") as f_in:
                    return f_in.read().decode("utf-8")

            # Handle pickle files
            if file_name.endswith(".pkl"):
                return pickle.load(file_stream)

            # Default: return content as a string
            return file_stream.read().decode("utf-8")
        except ClientError as e:
            logger.critical(str(e))
            return None

    def rename_s3_folder(self, old_folder: str, new_folder: str) -> None:
        """
        Rename a folder in S3 by copying all objects from the old folder to the new folder
        and then deleting the old objects.
        :param old_folder: The name of the existing folder in S3
        :param new_folder: The new folder name to move the objects to
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME, Prefix=old_folder
            )
            if "Contents" not in response:
                logger.info(f"No objects found in the folder: {old_folder}")
                return

            for obj in response["Contents"]:
                old_key = obj["Key"]
                new_key = old_key.replace(old_folder, new_folder, 1)
                self.s3_client.copy_object(
                    Bucket=S3_BUCKET_NAME,
                    CopySource={"Bucket": S3_BUCKET_NAME, "Key": old_key},
                    Key=new_key,
                )
                self.s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=old_key)
                logger.info(f"Moved {old_key} to {new_key}")
            logger.info(f"Folder renamed from {old_folder} to {new_folder}")
        except ClientError as e:
            logger.info(f"Error renaming folder: {str(e)}")


def test():
    from dotenv import load_dotenv
    import os

    load_dotenv()
    aws_folder = os.getenv("AWS_FOLDER", None)
    folder_date = "20240903"
    filename = "test.json"
    path_ = f"{aws_folder}/{folder_date}"
    full_path_to_file = f"{path_}/{filename}"
    s3_bucket = S3Manager()
    test_dict = {"test": "test"}
    exit_code_1 = s3_bucket.upload_json_file(filename, test_dict, path_)
    content_1 = s3_bucket.download_from_s3(filename, path_)
    files = s3_bucket.get_available_files(aws_folder)
    assert f"{folder_date}/{filename}" in files
    exit_code_2 = s3_bucket.delete_object_from_s3("test.json", path_)
    content_2 = s3_bucket.download_from_s3("test.json", path_)
    assert content_2 is None


if __name__ == "__main__":
    test()
