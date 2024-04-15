const GOOGLE_ORIGIN = "https://google.com";

// chrome.sidePanel
//   .setPanelBehavior({ openPanelOnActionClick: true })
//   .catch((error) => console.error(error));

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.contentScriptQuery == "postData") {
    fetch("http://localhost:5000/get_urls", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json; charset=utf-8",
      },
      body: JSON.stringify(request.data),
    })
      .then((response) => response.json())
      .then((response) => sendResponse(response))
      .catch((error) => console.log("Error:", error));
    return true;
  }
});

function contentScript() {
  const preTags = document.querySelectorAll("pre");
  let count = 0;
  for (const tag of preTags) {
    console.log(tag.textContent);
    count += 1;
    if (count == 7) {
      break
    }

    chrome.runtime.sendMessage(
      {
        contentScriptQuery: "postData",
        data: { html: tag.textContent },
      },
      function (response) {
        console.log(response)
      }
    );
  }
}

chrome.action.onClicked.addListener(async (tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: contentScript,
  });
});
