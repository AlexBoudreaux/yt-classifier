import unittest
from unittest.mock import patch, MagicMock
from src.config import load_dotenv, DEVELOPER_KEY, PROFILE_PATH, OPENAI_API_KEY, PINECONE_API_KEY, FIREBASE_ADMIN_SDK_PATH

class TestConfig(unittest.TestCase):

    @patch('src.config.load_dotenv')
    def test_load_dotenv(self, mock_load_dotenv):
        mock_load_dotenv.return_value = True
        result = load_dotenv()
        self.assertTrue(result)

    def test_developer_key(self):
        self.assertIsNotNone(DEVELOPER_KEY)

    def test_profile_path(self):
        self.assertIsNotNone(PROFILE_PATH)

    def test_openai_api_key(self):
        self.assertIsNotNone(OPENAI_API_KEY)

    def test_pinecone_api_key(self):
        self.assertIsNotNone(PINECONE_API_KEY)

    def test_firebase_admin_sdk_path(self):
        self.assertIsNotNone(FIREBASE_ADMIN_SDK_PATH)

if __name__ == '__main__':
    unittest.main()
