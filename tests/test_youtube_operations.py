import unittest
from unittest.mock import patch, MagicMock
from src.youtube_operations import get_authenticated_service, fetch_videos_from_playlist, add_to_playlist, video_exists_in_playlists

class TestYouTubeOperations(unittest.TestCase):

    @patch('src.youtube_operations.build')
    @patch('src.youtube_operations.Credentials')
    def test_get_authenticated_service(self, MockCredentials, mock_build):
        mock_creds = MockCredentials.from_authorized_user_file.return_value
        mock_build.return_value = 'YouTube Service'
        result = get_authenticated_service()
        self.assertEqual(result, 'YouTube Service')

    @patch('src.youtube_operations.get_authenticated_service')
    def test_fetch_videos_from_playlist(self, mock_get_authenticated_service):
        mock_youtube = mock_get_authenticated_service.return_value
        mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = {
            'items': [{'snippet': {'title': 'Test Video'}}]
        }
        result = fetch_videos_from_playlist(mock_youtube, 'test_playlist_id')
        self.assertEqual(result, [{'snippet': {'title': 'Test Video'}}])

    @patch('src.youtube_operations.get_authenticated_service')
    def test_add_to_playlist(self, mock_get_authenticated_service):
        mock_youtube = mock_get_authenticated_service.return_value
        mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = {
            'items': [{'snippet': {'resourceId': {'videoId': '123'}}}]
        }
        result = add_to_playlist(mock_youtube, '123', 'test_playlist_id', 'Test Video')
        self.assertFalse(result)

    @patch('src.youtube_operations.get_authenticated_service')
    def test_video_exists_in_playlists(self, mock_get_authenticated_service):
        mock_youtube = mock_get_authenticated_service.return_value
        mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = {
            'items': [{'snippet': {'resourceId': {'videoId': '123'}}}]
        }
        playlist_map = {'Test Playlist': {'playlist_id': 'test_playlist_id'}}
        result = video_exists_in_playlists(mock_youtube, playlist_map, '123')
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
