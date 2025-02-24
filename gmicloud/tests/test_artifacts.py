import unittest
from unittest.mock import patch
from gmicloud._internal._manager._artifact_manager import ArtifactManager
from gmicloud._internal._client._iam_client import IAMClient
from gmicloud._internal._models import *
from gmicloud._internal._enums import BuildStatus


class TestArtifactManager(unittest.TestCase):

    def setUp(self):
        self.mock_user_id = "test_user_id"
        self.mock_token = "test_token"

        self.iam_client = IAMClient(client_id="test_client_id", email="test_email", password="test_password")
        self.iam_client._user_id = self.mock_user_id
        self.iam_client._access_token = self.mock_token

        self.artifact_manager = ArtifactManager(self.iam_client)

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_artifact')
    def test_get_artifact_returns_artifact(self, mock_get_artifact):
        mock_get_artifact.return_value = Artifact(artifact_id="1")
        artifact = self.artifact_manager.get_artifact("1")
        self.assertEqual(artifact.artifact_id, "1")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_artifact')
    def test_get_artifact_raises_error_for_invalid_artifact_id(self, mock_get_artifact):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.get_artifact("")
        self.assertTrue("Artifact ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_artifact')
    def test_get_artifact_raises_error_for_nonexistent_artifact(self, mock_get_artifact):
        mock_get_artifact.side_effect = Exception("Artifact not found")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.get_artifact("nonexistent_id")
        self.assertTrue("Artifact not found" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_all_artifacts')
    def test_get_all_artifacts(self, mock_get_all_artifacts):
        mock_dict = {
            'artifact_id': 'test',
            'artifact_data': {
                'artifact_type': 'DockerImage',
                'artifact_link': 'link',
                'build_status': 'SUCCESS',
                'build_error': '',
                'build_id': 'test',
                'build_file_name': '',
                'create_at': '2024-12-25T03:20:39.820623326Z',
                'update_at': '2024-12-25T03:36:25.483679194Z',
                'status': ''
            },
            'artifact_metadata': {
                'user_id': 'test',
                'artifact_name': 'name',
                'artifact_description': 'description',
                'artifact_tags': ['tags', 'test']
            },
            'big_files_metadata': None
        }
        mock_get_all_artifacts.return_value = [Artifact(**mock_dict)]

        artifacts = self.artifact_manager.get_all_artifacts()
        self.assertEqual(len(artifacts), 1)

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact')
    def test_create_artifact(self, mock_create_artifact):
        mock_response = CreateArtifactResponse(artifact_id="test_artifact_id", upload_link="mock_link")
        mock_create_artifact.return_value = mock_response

        response = self.artifact_manager.create_artifact("artifact_name")
        self.assertEqual(response.artifact_id, "test_artifact_id")

    @patch("gmicloud._internal._client._file_upload_client.FileUploadClient.upload_small_file")
    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact')
    def test_create_artifact_with_file(self, mock_create_artifact, mock_upload_small_file):
        upload_link = "http://upload-link"
        artifact_file_path = "./testdata/test.zip"

        mock_response = CreateArtifactResponse(artifact_id="test_artifact_id", upload_link=upload_link)
        mock_create_artifact.return_value = mock_response

        artifact_id = self.artifact_manager.create_artifact_with_file(
            artifact_name="artifact_name",
            artifact_file_path=artifact_file_path,
        )
        self.assertEqual(artifact_id, "test_artifact_id")
        mock_upload_small_file.assert_called_once_with(upload_link, artifact_file_path, "application/zip")

    def test_create_artifact_with_file_raises_error_for_invalid_file_type(self):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.create_artifact_with_file("artifact_name", "./testdata/test.txt")
        self.assertTrue("File type must be application/zip." in str(context.exception))

    def test_create_artifact_with_file_raises_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError) as context:
            self.artifact_manager.create_artifact_with_file("artifact_name", "./testdata/nonexistent.zip")
        self.assertTrue("File not found: ./testdata/nonexistent.zip" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact_from_template')
    def test_create_artifact_from_template_creates_artifact(self, mock_create_artifact_from_template):
        mock_create_artifact_from_template.return_value = CreateArtifactFromTemplateResponse(artifact_id="1",
                                                                                             status="success")
        artifact_template_id = "template123"
        response = self.artifact_manager.create_artifact_from_template(artifact_template_id)
        self.assertEqual(response, "1")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact_from_template')
    def test_create_artifact_from_template_raises_error_for_invalid_template_id(self,
                                                                                mock_create_artifact_from_template):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.create_artifact_from_template("")
        self.assertTrue("Artifact template ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact_from_template')
    def test_create_artifact_from_template_raises_error_for_nonexistent_template(self,
                                                                                 mock_create_artifact_from_template):
        mock_create_artifact_from_template.side_effect = Exception("Template not found")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.create_artifact_from_template("nonexistent_template_id")
        self.assertTrue("Template not found" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact')
    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_bigfile_upload_url')
    @patch('gmicloud._internal._client._file_upload_client.FileUploadClient.upload_small_file')
    @patch('gmicloud._internal._client._file_upload_client.FileUploadClient.upload_large_file')
    def test_create_artifact_with_model_files(self, mock_upload_large_file, mock_upload_small_file,
                                              mock_get_bigfile_upload_url, mock_create_artifact):
        upload_link = "http://upload-link"
        bigfile_upload_link = "http://bigfile-upload-link"
        artifact_file_path = "./testdata/test.zip"
        model_file_path = "./testdata/model.zip"

        mock_create_artifact.return_value = CreateArtifactResponse(artifact_id="1", upload_link=upload_link)
        mock_get_bigfile_upload_url.return_value = GetBigFileUploadUrlResponse(artifact_id="1",
                                                                               upload_link=bigfile_upload_link)

        artifact_id = self.artifact_manager.create_artifact_with_model_files(artifact_name="artifact_name",
                                                                             artifact_file_path=artifact_file_path,
                                                                             model_file_paths=[model_file_path])
        self.assertEqual(artifact_id, "1")
        mock_upload_small_file.assert_called_once_with(upload_link, artifact_file_path, "application/zip")
        mock_upload_large_file.assert_called_once_with(bigfile_upload_link, model_file_path)

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.create_artifact')
    @patch('gmicloud._internal._client._file_upload_client.FileUploadClient.upload_small_file')
    def test_create_artifact_with_model_files_raises_file_not_found_error_for_model_file(self, mock_create_artifact,
                                                                                         mock_upload_small_file):
        upload_link = "http://upload-link"
        artifact_file_path = "./testdata/test.zip"
        model_file_path = "./testdata/nonexistent.zip"

        mock_create_artifact.return_value = CreateArtifactResponse(artifact_id="1", upload_link=upload_link)

        with self.assertRaises(FileNotFoundError) as context:
            self.artifact_manager.create_artifact_with_model_files(artifact_name="artifact_name",
                                                                   artifact_file_path=artifact_file_path,
                                                                   model_file_paths=[model_file_path])
        self.assertTrue(f"File not found: {model_file_path}" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.rebuild_artifact')
    def test_rebuild_artifact_rebuilds_successfully(self, mock_rebuild_artifact):
        mock_rebuild_artifact.return_value = RebuildArtifactResponse(artifact_id="1", build_status=BuildStatus.SUCCESS)
        response = self.artifact_manager.rebuild_artifact("1")
        self.assertEqual(response.artifact_id, "1")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.rebuild_artifact')
    def test_rebuild_artifact_raises_error_for_invalid_artifact_id(self, mock_rebuild_artifact):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.rebuild_artifact("")
        self.assertTrue("Artifact ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.rebuild_artifact')
    def test_rebuild_artifact_raises_error_for_nonexistent_artifact(self, mock_rebuild_artifact):
        mock_rebuild_artifact.side_effect = Exception("Artifact not found")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.rebuild_artifact("nonexistent_id")
        self.assertTrue("Artifact not found" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_artifact')
    def test_delete_artifact_deletes_successfully(self, mock_delete_artifact):
        mock_delete_artifact.return_value = DeleteArtifactResponse(artifact_id="1")
        response = self.artifact_manager.delete_artifact("1")
        self.assertEqual(response.artifact_id, "1")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_artifact')
    def test_delete_artifact_raises_error_for_invalid_artifact_id(self, mock_delete_artifact):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.delete_artifact("")
        self.assertTrue("Artifact ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_artifact')
    def test_delete_artifact_raises_error_for_nonexistent_artifact(self, mock_delete_artifact):
        mock_delete_artifact.side_effect = Exception("Artifact not found")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.delete_artifact("nonexistent_id")
        self.assertTrue("Artifact not found" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_bigfile_upload_url')
    def test_get_bigfile_upload_url_returns_upload_link(self, mock_get_bigfile_upload_url):
        upload_link = "http://upload-link"
        model_file_path = "./testdata/model.zip"

        mock_get_bigfile_upload_url.return_value = GetBigFileUploadUrlResponse(artifact_id="1", upload_link=upload_link)
        upload_link = self.artifact_manager.get_bigfile_upload_url("1", model_file_path)
        self.assertEqual(upload_link, upload_link)

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_bigfile_upload_url')
    def test_get_bigfile_upload_url_raises_error_for_invalid_artifact_id(self, mock_get_bigfile_upload_url):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.get_bigfile_upload_url("", "./testdata/test.zip")
        self.assertTrue("Artifact ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_bigfile_upload_url')
    def test_get_bigfile_upload_url_raises_error_for_invalid_file_path(self, mock_get_bigfile_upload_url):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.get_bigfile_upload_url("1", "")
        self.assertTrue("File path is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_bigfile_upload_url')
    def test_get_bigfile_upload_url_raises_error_for_nonexistent_file(self, mock_get_bigfile_upload_url):
        with self.assertRaises(FileNotFoundError) as context:
            self.artifact_manager.get_bigfile_upload_url("1", "./testdata/nonexistent.zip")
        self.assertTrue("File not found: ./testdata/nonexistent.zip" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_bigfile')
    def test_delete_bigfile_deletes_successfully(self, mock_delete_bigfile):
        mock_delete_bigfile.return_value = DeleteBigfileResponse(artifact_id="1", file_name="file.txt",
                                                                 status="success")
        response = self.artifact_manager.delete_bigfile("1", "file.txt")
        self.assertEqual(response, "success")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_bigfile')
    def test_delete_bigfile_raises_error_for_invalid_artifact_id(self, mock_delete_bigfile):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.delete_bigfile("", "file.txt")
        self.assertTrue("Artifact ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_bigfile')
    def test_delete_bigfile_raises_error_for_invalid_file_name(self, mock_delete_bigfile):
        with self.assertRaises(ValueError) as context:
            self.artifact_manager.delete_bigfile("1", "")
        self.assertTrue("File name is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.delete_bigfile')
    def test_delete_bigfile_raises_error_for_nonexistent_artifact(self, mock_delete_bigfile):
        mock_delete_bigfile.side_effect = Exception("Artifact not found")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.delete_bigfile("nonexistent_id", "file.txt")
        self.assertTrue("Artifact not found" in str(context.exception))

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_public_templates')
    def test_get_artifact_templates_returns_templates(self, mock_get_public_templates):
        mock_get_public_templates.return_value = [ArtifactTemplate(template_id="1", template_data=TemplateData(name="Template1"))]
        templates = self.artifact_manager.get_public_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].template_id, "1")
        self.assertEqual(templates[0].template_data.name, "Template1")

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_public_templates')
    def test_get_artifact_templates_returns_empty_list_when_no_templates(self, mock_get_public_templates):
        mock_get_public_templates.return_value = []
        templates = self.artifact_manager.get_public_templates()
        self.assertEqual(len(templates), 0)

    @patch('gmicloud._internal._client._artifact_client.ArtifactClient.get_public_templates')
    def test_get_artifact_templates_raises_error_on_failure(self, mock_get_public_templates):
        mock_get_public_templates.side_effect = Exception("Failed to fetch templates")
        with self.assertRaises(Exception) as context:
            self.artifact_manager.get_public_templates()
        self.assertTrue("Failed to fetch templates" in str(context.exception))
