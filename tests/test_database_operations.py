import unittest
from unittest.mock import MagicMock, patch
from src.database_operations import get_playlist_map, get_all_videos, insert_into_firebase

class TestDatabaseOperations(unittest.TestCase):

    @patch('src.database_operations.db')
    def test_get_playlist_map(self, mock_db):
        mock_db.collection.return_value.get.return_value = [
            MagicMock(to_dict=MagicMock(return_value={'playlist_name': 'Test Playlist', 'playlist_id': '123'}), id='abc')
        ]
        result = get_playlist_map(mock_db)
        self.assertEqual(result, {'Test Playlist': {'playlist_id': '123', 'firebase_id': 'abc'}})

    @patch('src.database_operations.db')
    def test_get_all_videos(self, mock_db):
        mock_db.collection.return_value.get.return_value = [
            MagicMock(to_dict=MagicMock(return_value={'video_id': '123'}))
        ]
        result = get_all_videos(mock_db)
        self.assertEqual(result, [{'video_id': '123'}])

    @patch('src.database_operations.db')
    def test_insert_into_firebase(self, mock_db):
        mock_db.collection.return_value.where.return_value.get.return_value = [MagicMock(id='abc')]
        mock_db.collection.return_value.add.return_value = (None, MagicMock(get=MagicMock(return_value=MagicMock(to_dict=MagicMock(return_value={'video_id': '123'})))))
        video_data = {
            'playlist_id': '123',
            'playlist_name': 'Test Playlist',
            'video_id': '123',
            'title': 'Test Video',
            'description': 'Test Description',
            'transcript': 'Test Transcript',
            'summary': 'Test Summary'
        }
        result = insert_into_firebase(mock_db, video_data)
        self.assertEqual(result, {'video_id': '123'})

if __name__ == '__main__':
    unittest.main()
