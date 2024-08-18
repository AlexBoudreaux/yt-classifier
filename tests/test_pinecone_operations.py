import unittest
from unittest.mock import patch, MagicMock
from src.pinecone_operations import initialize_pinecone, embed_and_store_in_pinecone

class TestPineconeOperations(unittest.TestCase):

    @patch('src.pinecone_operations.Pinecone')
    def test_initialize_pinecone(self, MockPinecone):
        mock_instance = MockPinecone.return_value
        result = initialize_pinecone()
        self.assertEqual(result, mock_instance)

    @patch('src.pinecone_operations.openai.Embedding.create')
    @patch('src.pinecone_operations.Pinecone')
    def test_embed_and_store_in_pinecone(self, MockIndex, mock_openai):
        mock_index_instance = MockIndex.return_value
        mock_openai.return_value.create.return_value = {'data': [{'embedding': [0.1, 0.2, 0.3]}]}
        mock_index_instance.upsert.return_value = None
        video_data = {
            'title': 'Test Video',
            'creator': 'Test Creator',
            'description': 'Test Description',
            'summary': 'Test Summary',
            'recipe': 'Test Recipe',
            'personalized_description': 'Test Personalized Description',
            'food_category': '["Test Category"]',
            'video_id': '123',
            'transcript': 'Test Transcript'
        }
        embed_and_store_in_pinecone(mock_index_instance, video_data)
        embed_and_store_in_pinecone(mock_index_instance, video_data)
        mock_index_instance.upsert.assert_called_once()
        mock_index_instance.upsert.return_value = None
        mock_openai.return_value.create.return_value = {'data': [{'embedding': [0.1, 0.2, 0.3]}]}
        video_data = {
            'title': 'Test Video',
            'creator': 'Test Creator',
            'description': 'Test Description',
            'summary': 'Test Summary',
            'recipe': 'Test Recipe',
            'personalized_description': 'Test Personalized Description',
            'food_category': '["Test Category"]',
            'video_id': '123',
            'transcript': 'Test Transcript'
        }
        embed_and_store_in_pinecone(mock_index_instance, video_data)
        mock_index_instance.upsert.assert_called()

if __name__ == '__main__':
    unittest.main()
