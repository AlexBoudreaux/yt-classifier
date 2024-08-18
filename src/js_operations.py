from playwright.sync_api import sync_playwright
from config import PROFILE_PATH

def add_watchlater_to_temp():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_data_dir=PROFILE_PATH)
        page = context.new_page()
        page.goto('https://www.youtube.com/playlist?list=WL')

        # Here's your JavaScript code as a multi-line string
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

        # Execute the JavaScript code
        page.evaluate(js_code)

        # Wait for the JavaScript code to complete
        page.wait_for_function("window.scriptCompleted")
        browser.close()


def deselect_cooking_videos():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_data_dir=PROFILE_PATH)
        page = context.new_page()
        page.goto('https://www.youtube.com/playlist?list=WL')

        # Here's your JavaScript code as a multi-line string
        js_code = """
    var videoIndex = 0;
    var cookingVideosRemoved = 0;

    function randomDelay(min, max) {
    return Math.random() * (max - min) + min;
    }

    function deselectWatchLater() {
    var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
    if (videoIndex >= videos.length) {
        console.log('All videos processed');
        console.log('Total cooking videos removed from Watch Later:', cookingVideosRemoved);
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
            if (cookingPlaylistCheckbox && cookingPlaylistCheckbox.getAttribute('aria-checked') === 'true') {
            var watchLaterCheckbox = document.querySelector('ytd-playlist-add-to-option-renderer tp-yt-paper-checkbox[checked] #label[title="Watch later"]');
            if (watchLaterCheckbox) {
                watchLaterCheckbox.click();
                console.log('Cooking video removed from Watch Later at index:', videoIndex);
                cookingVideosRemoved++;
                setTimeout(() => {
                var closeButton = document.querySelector('yt-icon-button[icon="close"], button[aria-label="Close"]');
                if (!closeButton) {
                    closeButton = document.querySelector('button[aria-label="Cancel"]');
                }
                if (closeButton) {
                    closeButton.click();
                }
                videoIndex++;
                setTimeout(deselectWatchLater, randomDelay(1000, 2000)); // Process next video after a delay
                }, randomDelay(500, 1500)); // Wait for the checkbox interaction
            } else {
                closeSaveMenuAndProceed();
            }
            } else {
            closeSaveMenuAndProceed();
            }
        }, randomDelay(1000, 2000));
        } else {
        videoIndex++;
        deselectWatchLater();
        }
    }, randomDelay(500, 1000));
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
    setTimeout(deselectWatchLater, randomDelay(1000, 2000)); // Proceed to next video after a delay
    }

    deselectWatchLater(); // Start the script
    """

        # Execute the JavaScript code
        page.evaluate(js_code)

        # Wait for the JavaScript code to complete
        page.wait_for_function("window.scriptCompleted")
        browser.close()


# def execute_js_function(js_function):
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option('useAutomationExtension', False)
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")

#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get('https://www.youtube.com/playlist?list=WL')

#     # Execute the JavaScript function
#     driver.execute_script(js_function)

#     # Wait for the script to complete
#     while not driver.execute_script("return window.scriptCompleted;"):
#         time.sleep(1)

#     driver.quit()
