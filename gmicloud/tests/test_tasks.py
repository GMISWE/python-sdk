import unittest
from unittest.mock import MagicMock, patch, Mock
from gmicloud._internal._manager._task_manager import TaskManager
from gmicloud._internal._client._iam_client import IAMClient
from gmicloud._internal._models import *


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.mock_user_id = "test_user_id"
        self.mock_token = "test_token"

        self.iam_client = IAMClient(client_id="test_client_id", email="test_email", password="test_password")
        self.iam_client._user_id = self.mock_user_id
        self.iam_client._access_token = self.mock_token
        self.task_manager = TaskManager(self.iam_client)

    @patch('gmicloud._internal._client._task_client.TaskClient.get_task')
    def test_get_task_returns_task_successfully(self, mock_get_task):
        mock_get_task.return_value = Task(task_id="1")
        task = self.task_manager.get_task("1")
        self.assertEqual(task.task_id, "1")

    @patch('gmicloud._internal._client._task_client.TaskClient.get_task')
    def test_get_task_raises_error_for_invalid_task_id(self, mock_get_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.get_task("")
        self.assertTrue("Task ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.get_task')
    def test_get_task_raises_error_for_nonexistent_task(self, mock_get_task):
        mock_get_task.side_effect = Exception("Task not found")
        with self.assertRaises(Exception) as context:
            self.task_manager.get_task("nonexistent_id")
        self.assertTrue("Task not found" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.get_all_tasks')
    def test_get_all_tasks_returns_list_of_tasks(self, mock_get_all_tasks):
        mock_dict = {
            'task_id': 'test',
            'owner': {
                'user_id': 'test',
                'group_id': 'current_group_id',
                'service_account_id': 'current_sa_id'
            },
            'config': {
                'ray_task_config': {
                    'ray_version': 'latest-py311-gpu',
                    'ray_cluster_image': '',
                    'file_path': 'serve',
                    'deployment_name': 'app',
                    'artifact_id': 'test',
                    'replica_resource': {
                        'cpu': 6,
                        'ram_gb': 64,
                        'gpu': 2,
                        'gpu_name': ''
                    },
                    'volume_mounts': None
                },
                'task_scheduling': {
                    'scheduling_oneoff': {
                        'trigger_timestamp': 0,
                        'min_replicas': 0,
                        'max_replicas': 0
                    },
                    'scheduling_daily': {
                        'triggers': None
                    }
                },
                'create_timestamp': 1734951094,
                'last_update_timestamp': 1734975798
            },
            'task_status': 'running',
            'readiness_status': '',
            'info': {
                'endpoint_status': 'ready',
                'endpoint': 'api.GMICOULD.ai/INFERENCEENGINE/c49bfbc9-3'
            }
        }
        mock_get_all_tasks.return_value = MagicMock(tasks=[Task(**mock_dict)])
        tasks = self.task_manager.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "test")

    @patch('gmicloud._internal._client._task_client.TaskClient.get_all_tasks')
    def test_get_all_tasks_handles_empty_list(self, mock_get_all_tasks):
        mock_get_all_tasks.return_value = MagicMock(tasks=[])
        tasks = self.task_manager.get_all_tasks()
        self.assertEqual(len(tasks), 0)

    @patch('gmicloud._internal._client._task_client.TaskClient.create_task')
    def test_create_task_raises_error_for_none_task(self, mock_create_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task(None)
        self.assertTrue("Task object is required and cannot be None." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.create_task')
    def test_create_task_from_file_creates_task(self, mock_create_task):
        self.task_manager.create_task_from_file("1", "./testdata/one-off_task.json", int(datetime.now().timestamp()))
        mock_create_task.assert_called_once()

    @patch('gmicloud._internal._client._task_client.TaskClient.create_task')
    def test_create_task_from_file_raises_error_for_invalid_file(self, mock_create_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task_from_file("1", "./testdata/one-off_task_err.json")
        self.assertTrue("Failed to parse Task from file" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.update_task_schedule')
    def test_update_task_schedule_raises_error_for_none_task(self, mock_update_task_schedule):
        with self.assertRaises(ValueError) as context:
            self.task_manager.update_task_schedule(None)
        self.assertTrue("Task object is required and cannot be None." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.update_task_schedule')
    def test_update_task_schedule_from_file_updates_schedule(self, mock_update_task_schedule):
        self.task_manager.update_task_schedule_from_file("1", "1", "./testdata/daily_task.json")
        mock_update_task_schedule.assert_called_once()

    @patch('gmicloud._internal._client._task_client.TaskClient.update_task_schedule')
    def test_update_task_schedule_from_file_raises_error_for_invalid_file(self, mock_update_task_schedule):
        with self.assertRaises(ValueError) as context:
            self.task_manager.update_task_schedule_from_file("1", "1", "./testdata/one-off_task_err.json")
        self.assertTrue("Failed to parse Task from file" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.start_task')
    def test_start_task_starts_successfully(self, mock_start_task):
        mock_start_task.return_value = None
        self.task_manager.start_task("1")
        mock_start_task.assert_called_once_with("1")

    @patch('gmicloud._internal._client._task_client.TaskClient.start_task')
    def test_start_task_raises_error_for_invalid_task_id(self, mock_start_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.start_task("")
        self.assertTrue("Task ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.start_task')
    def test_start_task_raises_error_for_nonexistent_task(self, mock_start_task):
        mock_start_task.side_effect = Exception("Task not found")
        with self.assertRaises(Exception) as context:
            self.task_manager.start_task("nonexistent_id")
        self.assertTrue("Task not found" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.stop_task')
    def test_stop_task_stops_successfully(self, mock_stop_task):
        mock_stop_task.return_value = None
        self.task_manager.stop_task("1")
        mock_stop_task.assert_called_once_with("1")

    @patch('gmicloud._internal._client._task_client.TaskClient.stop_task')
    def test_stop_task_raises_error_for_invalid_task_id(self, mock_stop_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.stop_task("")
        self.assertTrue("Task ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.stop_task')
    def test_stop_task_raises_error_for_nonexistent_task(self, mock_stop_task):
        mock_stop_task.side_effect = Exception("Task not found")
        with self.assertRaises(Exception) as context:
            self.task_manager.stop_task("nonexistent_id")
        self.assertTrue("Task not found" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.get_usage_data')
    def test_get_usage_data_returns_data_successfully(self, mock_get_usage_data):
        mock_get_usage_data.return_value = GetUsageDataResponse(usage_data=[Usage(replica_count=1)])
        response = self.task_manager.get_usage_data("2023-01-01T00:00:00Z", "2023-01-31T23:59:59Z")
        self.assertEqual(response.usage_data[0].replica_count, 1)

    @patch('gmicloud._internal._client._task_client.TaskClient.get_usage_data')
    def test_get_usage_data_raises_error_for_invalid_start_timestamp(self, mock_get_usage_data):
        with self.assertRaises(ValueError) as context:
            self.task_manager.get_usage_data("", "2023-01-31T23:59:59Z")
        self.assertTrue("Start timestamp is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.get_usage_data')
    def test_get_usage_data_raises_error_for_invalid_end_timestamp(self, mock_get_usage_data):
        with self.assertRaises(ValueError) as context:
            self.task_manager.get_usage_data("2023-01-01T00:00:00Z", "")
        self.assertTrue("End timestamp is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.get_usage_data')
    def test_get_usage_data_raises_error_on_failure(self, mock_get_usage_data):
        mock_get_usage_data.side_effect = Exception("Failed to fetch usage data")
        with self.assertRaises(Exception) as context:
            self.task_manager.get_usage_data("2023-01-01T00:00:00Z", "2023-01-31T23:59:59Z")
        self.assertTrue("Failed to fetch usage data" in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.archive_task')
    def test_archive_task_archives_successfully(self, mock_archive_task):
        mock_archive_task.return_value = None
        self.task_manager.archive_task("1")
        mock_archive_task.assert_called_once_with("1")

    @patch('gmicloud._internal._client._task_client.TaskClient.archive_task')
    def test_archive_task_raises_error_for_invalid_task_id(self, mock_archive_task):
        with self.assertRaises(ValueError) as context:
            self.task_manager.archive_task("")
        self.assertTrue("Task ID is required and cannot be empty." in str(context.exception))

    @patch('gmicloud._internal._client._task_client.TaskClient.archive_task')
    def test_archive_task_raises_error_for_nonexistent_task(self, mock_archive_task):
        mock_archive_task.side_effect = Exception("Task not found")
        with self.assertRaises(Exception) as context:
            self.task_manager.archive_task("nonexistent_id")
        self.assertTrue("Task not found" in str(context.exception))
