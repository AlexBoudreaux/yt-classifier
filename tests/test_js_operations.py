import unittest
from unittest.mock import patch, MagicMock
from src.js_operations import add_watchlater_to_temp, deselect_cooking_videos

class TestJSOperations(unittest.TestCase):

    @patch('src.js_operations.webdriver.Chrome')
    def test_add_watchlater_to_temp(self, MockChrome):
        mock_driver = MockChrome.return_value
        mock_driver.execute_script.return_value = True
        add_watchlater_to_temp()
        mock_driver.get.assert_called_with('https://www.youtube.com/playlist?list=WL')
        mock_driver.quit.assert_called_once()

    @patch('src.js_operations.webdriver.Chrome')
    def test_deselect_cooking_videos(self, MockChrome):
        mock_driver = MockChrome.return_value
        mock_driver.execute_script.return_value = True
        deselect_cooking_videos()
        mock_driver.get.assert_called_with('https://www.youtube.com/playlist?list=WL')
        mock_driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
