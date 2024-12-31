import os
import requests

from GMICloud.http_client.exceptions import UploadFileError


class FileUploadClient:
    """
    A file upload client supporting small files and resumable uploads (chunked uploads).
    """

    @staticmethod
    def upload_small_file(upload_url: str, file_path: str,
                          content_type: str = "application/octet-stream"):
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
    def upload_large_file(upload_url: str, file_path: str, chunk_size: int = 10 * 1024 * 1024):
        """
        Performs resumable (chunked) file uploads to a signed Google Storage URL.

        :param upload_url: Signed resumable upload URL.
        :param file_path: The local path to the file to upload.
        :param chunk_size: Chunk size in bytes (default: 10MB).
        """
        file_size = os.path.getsize(file_path)
        print(f"File Size: {file_size} bytes")
        try:
            with open(file_path, "rb") as file:
                start_byte = 0

                while start_byte < file_size:
                    end_byte = min(start_byte + chunk_size - 1, file_size - 1)
                    file.seek(start_byte)
                    chunk_data = file.read(chunk_size)

                    content_range = f"bytes {start_byte}-{end_byte}/{file_size}"
                    headers = {"Content-Range": content_range}

                    response = requests.put(upload_url, headers=headers, data=chunk_data)

                    if response.status_code not in (200, 201, 308):
                        raise UploadFileError(
                            f"Failed to upload file, code:{response.status_code} ,message: {response.text}")

                    start_byte = end_byte + 1
                    print(f"Uploaded {end_byte + 1}/{file_size} bytes")
        except Exception as e:
            raise UploadFileError(f"Failed to upload file: {str(e)}")


if __name__ == '__main__':
    # Small file upload
    # upload_url = "https://storage.googleapis.com/gmi-artifact-build-files/testing/593072db-18e4-46eb-b572-a8fafbdc2902/build_files_20241227004336.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=artifact-service%40devv-404803.iam.gserviceaccount.com%2F20241227%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20241227T004336Z&X-Goog-Expires=899&X-Goog-Signature=09f8f2fb3cf0ac0a2e975fefe9cdffce462a4d213453c716bf6520a833f6343ea7ca44b6fe46a515938c63bfbf8a9053ab119844a41064547bda26c244fd526708a71fdb1e94899f47a7543cf5e51be601863c6a9050e007ed58efbe4384b7969e425532eb59b2fdad74e357f0193cae4bc014da134518b2dfafb3014b3bd25b20640d63a1bc24af4f032597a50106055495dbf8b0a5f91a3e6b447aca13c6e4794524c0da71ab9b2b38176e4c1f972ce44cbbbc13d4025474dccd99bcc069e96a7611d6241c89c0b1144d7c24abbcba6726a2172ac48e50b544be97e84f404a91479716a2826e7465214a6f3fc08900eaea51e67734783a24bed259c6d382f3&X-Goog-SignedHeaders=content-type%3Bhost"
    # file_path = "/Users/57block/Downloads/gmi-apis/Llama-3.1-8B-Instruct.zip"
    # FileUploadClient.upload_small_file(upload_url, file_path)

    # Large file upload
    upload_url = "https://storage.googleapis.com/gmi-artifact-big-files/testing/ad035d95-202c-4a2e-b1be-7722b3dd9fb8/test.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=artifact-service%40devv-404803.iam.gserviceaccount.com%2F20241229%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20241229T145714Z&X-Goog-Expires=2699&X-Goog-Signature=7c882a35ada313054ea6684bb1145dc78f6b61d718a8c29640addbceaa164a20db37d83ca9d7dbd776ef886f6aa53504b3cb56260e15da1e74789c78052917beaf98e43808af61a966d71d8d609085c98286162b01db04b665b38cdb83299dc05b852fe71814cf857fb9b915034082664a454438025a16f73a384734ac459a8358e1b2cb01aad090326c54fab301626b8d6fbc9fb91c6d7be435e5145ac9c1f89ac28b1068ead3e2209ea896e809f536cbe00768f6864fc5ea8e9210fa787295e849714f5f763f15c3ea6d4faf8ae7e27d84d284309db039dbf35c8023adca411a9e0b2930b8a10877f8db7b012c1cde6ff3c38c5821768542afbbf7fc16241b&X-Goog-SignedHeaders=content-type%3Bhost%3Bx-goog-resumable&upload_id=AFiumC5vSW-MoH4yKo0CMNubxVxOCd0xCZewh13FXCcZMbHgaRySqp78UK3lYzPdFjZi-_edlhlfUrBcVU36XVwswuD4N-CaSXd1FlXLVgBInw"
    file_path = "/Users/57block/Downloads/test.zip"
    FileUploadClient.upload_large_file(upload_url, file_path)