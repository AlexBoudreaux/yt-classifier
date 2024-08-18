import unittest
from unittest.mock import patch, MagicMock
from src.main import main

class TestMain(unittest.TestCase):

    @patch('src.main.initialize_firebase')
    @patch('src.main.get_authenticated_service')
    @patch('src.main.initialize_pinecone')
    @patch('src.main.fetch_videos_from_playlist')
    @patch('src.main.process_video')
    @patch('src.main.classify_video')
    @patch('src.main.process_cooking_video')
    @patch('src.main.embed_and_store_in_pinecone')
    @patch('src.main.add_to_playlist')
    @patch('src.main.insert_into_firebase')
    @patch('src.main.deselect_cooking_videos')
    def test_main(self, mock_deselect_cooking_videos, mock_insert_into_firebase, mock_add_to_playlist, mock_embed_and_store_in_pinecone, mock_process_cooking_video, mock_classify_video, mock_process_video, mock_fetch_videos_from_playlist, mock_initialize_pinecone, mock_get_authenticated_service, mock_initialize_firebase):
        mock_initialize_firebase.return_value = MagicMock()
        mock_get_authenticated_service.return_value = MagicMock()
        mock_initialize_pinecone.return_value = MagicMock()
        mock_fetch_videos_from_playlist.return_value = [{'snippet': {'resourceId': {'videoId': '123'}, 'title': 'Test Video'}}]
        main()
        mock_fetch_videos_from_playlist.assert_called()
        mock_process_video.return_value = {'video_id': '123', 'title': 'Test Video', 'description': 'Test Description', 'transcript': 'Test Transcript', 'summary': 'Test Summary'}
        mock_classify_video.return_value = '<video_classification>cooking</video_classification>'
        mock_process_cooking_video.return_value = {'video_id': '123', 'title': 'Test Video', 'description': 'Test Description', 'transcript': 'Test Transcript', 'summary': 'Test Summary', 'recipe': 'Test Recipe', 'personalized_description': 'Test Personalized Description', 'food_category': '["Test Category"]'}
        mock_add_to_playlist.return_value = True

        main()

        mock_initialize_firebase.assert_called_once()
        mock_get_authenticated_service.assert_called_once()
        mock_initialize_pinecone.assert_called_once()
        mock_fetch_videos_from_playlist.assert_called_once()
        mock_process_video.assert_called_once()
        mock_classify_video.assert_called_once()
        mock_process_cooking_video.assert_called_once()
        mock_embed_and_store_in_pinecone.assert_called_once()
        mock_add_to_playlist.assert_called_once()
        mock_insert_into_firebase.assert_called_once()
        mock_deselect_cooking_videos.assert_called_once()

if __name__ == '__main__':
    unittest.main()
