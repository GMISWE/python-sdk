import os
import requests

from .._exceptions import UploadFileError


class FileUploadClient:
    CHUNK_SIZE = 10 * 1024 * 1024  # 10MB Default Chunk Size

    """
    A file upload client supporting small files and resumable uploads (chunked uploads).
    """

    @staticmethod
    def upload_small_file(upload_url: str, file_path: str,
                          content_type: str = "application/zip"):
        """
        Uploads a small file directly to a signed Google Storage upload URL.

        :param upload_url: Signed upload URL for small files.
        :param file_path: The local path to the file to upload.
        :param content_type: MIME type of the file.
        """
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()

            headers = {"Content-Type": content_type}
            response = requests.put(upload_url, headers=headers, data=file_data)

            if response.status_code not in [200, 201]:
                raise UploadFileError(f"Failed to upload file, code:{response.status_code} ,message: {response.text}")

        except requests.exceptions.RequestException as e:
            raise UploadFileError(f"Failed to upload file: {str(e)}")

    @staticmethod
    def upload_large_file(upload_url: str, file_path: str, chunk_size: int = CHUNK_SIZE):
        """
        Performs resumable (chunked) file uploads to a signed Google Storage URL.

        :param upload_url: Signed resumable upload URL.
        :param file_path: The local path to the file to upload.
        :param chunk_size: Chunk size in bytes (default: 10MB).
        """
        try:
            file_size = os.path.getsize(file_path)
            print(f"File Size: {file_size} bytes")

            start_byte = 0
            uploaded_range = FileUploadClient._check_file_status(upload_url, file_size)
            if uploaded_range:
                start_byte = int(uploaded_range.split("-")[1]) + 1
                print(f"Resuming upload from {start_byte} bytes")

            with open(file_path, "rb") as file:
                while start_byte < file_size:
                    # Calculate end byte and adjust chunk to not exceed file size
                    end_byte = min(start_byte + chunk_size - 1, file_size - 1)

                    # Seek to the current position in the file and read the chunk
                    file.seek(start_byte)
                    chunk_data = file.read(chunk_size)

                    # Set the Content-Range and headers
                    content_range = f"bytes {start_byte}-{end_byte}/{file_size}"
                    headers = {
                        "Content-Length": str(len(chunk_data)),
                        "Content-Range": content_range
                    }

                    # Upload the chunk
                    resp = requests.put(upload_url, headers=headers, data=chunk_data)
                    # Ensure upload is successful for this chunk
                    if resp.status_code not in (200, 201, 308):
                        raise UploadFileError(
                            f"Failed to upload file, code:{resp.status_code} ,message: {resp.text}")

                    start_byte = end_byte + 1
                    print(f"Uploaded {end_byte + 1}/{file_size} bytes")

                print("Upload completed successfully.")
        except Exception as e:
            raise UploadFileError(f"Failed to upload file: {str(e)}")

    @staticmethod
    def _check_file_status(upload_url: str, file_size: int) -> str:
        """
        Check the status of a resumable upload.

        :param upload_url: The resumable upload URL.
        :param file_size: Total file size in bytes.
        :return: The status of the upload (e.g., 'bytes=0-10485759') or None if no partial upload.
        """
        headers = {
            "Content-Length": "0",  # No payload for status check
            "Content-Range": f"bytes */{file_size}"  # Asking server where the upload left off
        }

        try:
            resp = requests.put(upload_url, headers=headers)

            # If upload is incomplete (HTTP 308: Resume Incomplete), retrieve the "Range" header
            if resp.status_code == 308:
                range_header = resp.headers.get("Range")
                if range_header:
                    print(f"Server reports partial upload range: {range_header}")
                return range_header

            if resp.status_code in (200, 201):
                return None

            resp.raise_for_status()
        except requests.RequestException as e:
            raise UploadFileError(f"Failed to check file status: {str(e)}") from e
