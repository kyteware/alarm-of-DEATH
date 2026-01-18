const PUSH_INTERVAL_MS = 10000;

// Fetch browser history and send to Python
function exportHistory() {
  chrome.history.search(
    {
      text: "",
      startTime: 0,
      maxResults: 100,
    },
    (results) => {
      const simplified = results.map((item) => ({
        url: item.url,
        title: item.title,
        lastVisitTime: item.lastVisitTime,
      }));

      // Send to history server (history_logger.py) on port 5000
      fetch("http://localhost:5000/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(simplified),
      })
        .then(() => console.log("History sent successfully"))
        .catch((err) => console.error("Send failed (is test.py running?):", err));
    }
  );
}

// Push history automatically
setInterval(exportHistory, PUSH_INTERVAL_MS);
