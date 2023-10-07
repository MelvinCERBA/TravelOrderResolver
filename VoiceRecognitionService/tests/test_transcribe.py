import os
import unittest
from index import create_app


class TranscribeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['UPLOADED_AUDIO_DEST'] = 'tests/uploads/audio'  # Use a different folder for tests
        self.client = self.app.test_client()

    def tearDown(self):
        # Cleanup code if needed (like removing uploaded test files)
        pass

    def test_transcribe_endpoint(self):
        with open('tests/test_data/CeciEstUnTest.wav', 'rb') as audio:
            response = self.client.post('/transcribe', content_type='multipart/form-data', data={'audio': audio})
        
        json_data = response.get_json()
        print(json_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('transcription', json_data)
        self.assertEqual(json_data['transcription'], "ceci est un test")

if __name__ == "__main__":
    unittest.main()
