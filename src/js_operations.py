from selenium import webdriver
import time
from tenacity import retry, stop_after_attempt, wait_fixed
import os
import logging

PROFILE_PATH = "/Users/alexboudreaux/Library/Application Support/Google/Chrome/Default"

def add_watchlater_to_temp():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {str(e)}", exc_info=True)
        return

    try:
        # Navigate to Watch Later playlist
        retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(driver.get)('https://www.youtube.com/playlist?list=WL')
    except Exception as e:
        logging.error(f"Error navigating to Watch Later playlist: {str(e)}", exc_info=True)
        driver.quit()
        return

    # Here's your JavaScript code as a multi-line string
    js_code = """
    function randomDelay(min, max) {
        return Math.random() * (max - min) + min;
    }

    function scrollToBottom() {
        return new Promise((resolve) => {
            let lastHeight = document.documentElement.scrollHeight;
            let scrollAttempts = 0;
            const maxScrollAttempts = 100; // Adjust this value if needed

            function scroll() {
                window.scrollTo(0, document.documentElement.scrollHeight);
                setTimeout(() => {
                    let newHeight = document.documentElement.scrollHeight;
                    if (newHeight === lastHeight || scrollAttempts >= maxScrollAttempts) {
                        resolve();
                    } else {
                        lastHeight = newHeight;
                        scrollAttempts++;
                        scroll();
                    }
                }, randomDelay(1000, 2000)); // Adjust delay as needed
            }

            scroll();
        });
    }

    async function processVideos() {
        await scrollToBottom();
        console.log("Finished scrolling, all videos should be loaded.");

        var videoIndex = 0;
        var consecutiveAddedCount = 0;

        function findStartingPoint() {
            var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
            if (videoIndex >= videos.length) {
                console.log('All videos processed in findStartingPoint');
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
                                console.log('Found starting point at video index:', videoIndex - 4);
                                videoIndex -= 5;
                                addVideosToTemp();
                                return;
                            }
                        } else {
                            consecutiveAddedCount = 0;
                        }
                        videoIndex++;
                        findStartingPoint();
                    }, randomDelay(300, 550));
                } else {
                    console.log('Save to playlist button not found at video index:', videoIndex);
                    videoIndex++;
                    findStartingPoint();
                }
            }, randomDelay(300, 550));
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
                                    addVideosToTemp();
                                } else {
                                    console.log('Exit button not found');
                                }
                            }, randomDelay(300, 550));
                        } else {
                            console.log('Temp Playlist button not found');
                        }
                    }, randomDelay(300, 550));
                } else {
                    console.log('Save to playlist button not found');
                }
            }, randomDelay(300, 550));
        }

        findStartingPoint();
    }

    processVideos();
    """

    # Execute the JavaScript code
    try:
        driver.execute_script(js_code)
    except Exception as e:
        logging.error(f"Error executing JavaScript code: {str(e)}", exc_info=True)
        driver.quit()
        return

    def is_script_completed():
        return driver.execute_script("return window.scriptCompleted;")

    # Wait for the JavaScript code to complete
    while not is_script_completed():
        try:
            time.sleep(1)  # Check every second
        except Exception as e:
            logging.error(f"Error during script completion check: {str(e)}", exc_info=True)
            break
    driver.quit()

def deselect_cooking_and_podcast_videos():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {str(e)}", exc_info=True)
        return

    try:
        # Navigate to Watch Later playlist
        driver.get('https://www.youtube.com/playlist?list=WL')
    except Exception as e:
        logging.error(f"Error navigating to Watch Later playlist: {str(e)}", exc_info=True)
        driver.quit()
        return

    # Here's your JavaScript code as a multi-line string
    js_code = """
    function randomDelay(min, max) {
        return Math.random() * (max - min) + min;
    }

    function scrollToBottom() {
        return new Promise((resolve) => {
            let lastHeight = document.documentElement.scrollHeight;
            let scrollAttempts = 0;
            const maxScrollAttempts = 100; // Adjust this value if needed

            function scroll() {
                window.scrollTo(0, document.documentElement.scrollHeight);
                setTimeout(() => {
                    let newHeight = document.documentElement.scrollHeight;
                    if (newHeight === lastHeight || scrollAttempts >= maxScrollAttempts) {
                        resolve();
                    } else {
                        lastHeight = newHeight;
                        scrollAttempts++;
                        scroll();
                    }
                }, randomDelay(1000, 2000)); // Adjust delay as needed
            }

            scroll();
        });
    }

    async function processVideos() {
        await scrollToBottom();
        console.log("Finished scrolling, all videos should be loaded.");

        deselectWatchLater();
    }

    var videoIndex = 0;
    var videosRemoved = 0;
    var consecutiveNonMatches = 0;  // New variable to track consecutive non-matches

    function deselectWatchLater() {
        var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
        if (videoIndex >= videos.length || consecutiveNonMatches >= 20) {
            console.log('All videos processed or 20 consecutive non-matches reached');
            console.log('Total videos removed from Watch Later:', videosRemoved);
            window.scriptCompleted = true;
            return;
        }
        var video = videos[videoIndex];
        video.querySelector('#primary button[aria-label="Action menu"]').click();
        setTimeout(() => {
            var saveButton = document.evaluate(
                '//yt-formatted-string[contains(text(),"Save to playlist")]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;
            if (saveButton) {
                saveButton.click();
                setTimeout(() => {
                    var cookingPlaylistCheckbox = document.evaluate(
                        '//yt-formatted-string[contains(text(),"Cooking")]/ancestor::tp-yt-paper-checkbox',
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    var podcastPlaylistCheckbox = document.evaluate(
                        '//yt-formatted-string[contains(text(),"Podcast/Comedy")]/ancestor::tp-yt-paper-checkbox',
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    
                    if ((cookingPlaylistCheckbox && cookingPlaylistCheckbox.getAttribute('aria-checked') === 'true') ||
                        (podcastPlaylistCheckbox && podcastPlaylistCheckbox.getAttribute('aria-checked') === 'true')) {
                        var watchLaterCheckbox = document.querySelector('ytd-playlist-add-to-option-renderer tp-yt-paper-checkbox[checked] #label[title="Watch later"]');
                        if (watchLaterCheckbox) {
                            watchLaterCheckbox.click();
                            console.log('Video removed from Watch Later at index:', videoIndex);
                            videosRemoved++;
                            consecutiveNonMatches = 0;  // Reset consecutive non-matches
                            setTimeout(() => {
                                var closeButton = document.querySelector('yt-icon-button[icon="close"], button[aria-label="Close"]');
                                if (!closeButton) {
                                    closeButton = document.querySelector('button[aria-label="Cancel"]');
                                }
                                if (closeButton) {
                                    closeButton.click();
                                }
                                videoIndex++;
                                setTimeout(deselectWatchLater, randomDelay(300, 550));
                            }, randomDelay(300, 550));
                        } else {
                            closeSaveMenuAndProceed();
                        }
                    } else {
                        consecutiveNonMatches++;  // Increment consecutive non-matches
                        closeSaveMenuAndProceed();
                    }
                }, randomDelay(300, 550));
            } else {
                videoIndex++;
                deselectWatchLater();
            }
        }, randomDelay(300, 550));
    }

    function closeSaveMenuAndProceed() {
        var closeButton = document.querySelector('yt-icon-button[icon="close"], button[aria-label="Close"]');
        if (!closeButton) {
            closeButton = document.querySelector('button[aria-label="Cancel"]');
        }
        if (closeButton) {
            closeButton.click();
        }
        videoIndex++;
        setTimeout(deselectWatchLater, randomDelay(300, 550));
    }

    processVideos(); // Start the script
    """

    # Execute the JavaScript code
    try:
        driver.execute_script(js_code)
    except Exception as e:
        logging.error(f"Error executing JavaScript code: {str(e)}", exc_info=True)
        driver.quit()
        return

    def is_script_completed():
        return driver.execute_script("return window.scriptCompleted;")

    # Wait for the JavaScript code to complete
    while not is_script_completed():
        try:
            time.sleep(1)  # Check every second
        except Exception as e:
            logging.error(f"Error during script completion check: {str(e)}", exc_info=True)
            break
    driver.quit()


if __name__ == '__main__':
    add_watchlater_to_temp()
