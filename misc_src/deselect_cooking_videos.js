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