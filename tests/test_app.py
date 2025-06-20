import io
import unittest
docker compose up --buildfrom unittest.mock import patch
from flask_app.app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Backend running', response.data)

    def test_upload_success(self):
        data = {
            'file': (io.BytesIO(b"test audio content"), 'test.wav')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded', response.data)

    def test_upload_no_file(self):
        response = self.app.post('/upload', data={}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file part', response.data)

    def test_upload_empty_filename(self):
        data = {
            'file': (io.BytesIO(b""), '')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No selected file', response.data)

    def test_process_success(self):
        response = self.app.post('/process', json={'param': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Processing started', response.data)

    def test_process_invalid_json(self):
        response = self.app.post('/process', data='notjson', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_process_url_no_url(self):
        response = self.app.post('/process_url', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No URL provided', response.data)

    @patch('app.download_youtube_audio')
    def test_process_url_success(self, mock_download):
        mock_download.return_value = 'mockfile.mp3'
        response = self.app.post('/process_url', json={'url': 'http://youtube.com/fake'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Audio downloaded successfully', response.data)
        self.assertIn(b'mockfile.mp3', response.data)

    @patch('app.download_youtube_audio')
    def test_process_url_failure(self, mock_download):
        mock_download.return_value = None
        response = self.app.post('/process_url', json={'url': 'http://youtube.com/fake'})
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Failed to download audio', response.data)

if __name__ == '__main__':
    unittest.main()
