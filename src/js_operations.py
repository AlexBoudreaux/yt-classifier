from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

def add_watchlater_to_temp():
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={os.getenv('CHROME_PROFILE_PATH')}")
    chrome_options.add_argument("--start-maximized")

    service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.youtube.com/playlist?list=WL")

        def is_script_completed(driver):
            return driver.execute_script("return window.scriptCompleted === true")

        js_code = """
        var videoIndex = 0;
        var consecutiveAddedCount = 0;

        function randomDelay(min, max) {
            return Math.random() * (max - min) + min;
        }

        function findStartingPoint() {
            var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
            if (videoIndex >= videos.length) {
                console.log('All videos processed in findStartingPoint');
                window.scriptCompleted = true;
                return;
            }

            var video = videos[videoIndex];
            video.querySelector('#primary button[aria-label="Action menu"]').click();

            setTimeout(function() {
                var saveButton = document.evaluate(
                    '//yt-formatted-string[contains(text(),"Save to playlist")]',
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;

                if (saveButton) {
                    saveButton.click();

                    setTimeout(function() {
                        var tempPlaylistCheckbox = document.evaluate(
                            '//yt-formatted-string[contains(text(),"Temp Playlist")]/ancestor::tp-yt-paper-checkbox',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;

                        if (tempPlaylistCheckbox && tempPlaylistCheckbox.getAttribute('aria-checked') === 'true') {
                            consecutiveAddedCount++;
                            if (consecutiveAddedCount >= 5) {
                                console.log('Found starting point at video index:', videoIndex - 4); // Adjusting for 0-based index and to go 5 videos up
                                videoIndex -= 5;  // Adjust to the starting point for adding videos
                                addVideosToTemp();  // Start the second function
                                return;
                            }
                        } else {
                            consecutiveAddedCount = 0;  // Reset the counter if a video not in Temp Playlist is found
                        }
                        videoIndex++;
                        findStartingPoint();
                    }, randomDelay(1000, 2000));
                } else {
                    console.log('Save to playlist button not found at video index:', videoIndex);
                    videoIndex++;
                    findStartingPoint();
                }
            }, randomDelay(1000, 2000));
        }

        function addVideosToTemp() {
            if (videoIndex < 0) {
                console.log('All videos processed');
                window.scriptCompleted = true;
                return;
            }

            var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
            var video = videos[videoIndex];
            video.querySelector('#primary button[aria-label="Action menu"]').click();

            setTimeout(function() {
                var saveButton = document.evaluate(
                    '//yt-formatted-string[contains(text(),"Save to playlist")]',
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;

                if (saveButton) {
                    saveButton.click();

                    setTimeout(function() {
                        var tempPlaylistButton = document.evaluate(
                            '//yt-formatted-string[contains(text(),"Temp Playlist")]/ancestor::tp-yt-paper-checkbox',
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;

                        if (tempPlaylistButton) {
                            tempPlaylistButton.click();

                            setTimeout(function() {
                                var exitButton = document.querySelector('button[aria-label="Cancel"]');
                                if (exitButton) {
                                    exitButton.click();
                                    videoIndex--;
                                    addVideosToTemp();  // Move to the previous video and continue
                                } else {
                                    console.log('Exit button not found');
                                }
                            }, randomDelay(1000, 2000));
                        } else {
                            console.log('Temp Playlist button not found');
                        }
                    }, randomDelay(1000, 2000));
                } else {
                    console.log('Save to playlist button not found');
                }
            }, randomDelay(1000, 2000));
        }

        findStartingPoint();  // Start the first function
        """

        driver.execute_script(js_code)

        try:
            WebDriverWait(driver, 600).until(is_script_completed)
        except TimeoutException:
            print("Script did not complete within the expected time.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
