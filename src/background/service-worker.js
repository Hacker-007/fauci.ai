const GOOGLE_ORIGIN = "https://google.com";

// chrome.sidePanel
//   .setPanelBehavior({ openPanelOnActionClick: true })
//   .catch((error) => console.error(error));

function contentScript() {
  const preTags = document.querySelectorAll("pre");
  preTags.forEach((tag) => {
    console.log(tag.textContent);
  });
}

chrome.action.onClicked.addListener(async (tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: contentScript,
  });
});
