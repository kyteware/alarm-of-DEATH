const POLL_INTERVAL_MS = 3000;

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

      fetch("http://localhost:5000/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(simplified),
      })
        .then(() => {
          // Tell Python we're done
          fetch("http://localhost:5000/reset", { method: "POST" });
        })
        .catch((err) => console.error("Send failed:", err));
    }
  );
}

// Poll Python for trigger signal
function pollTrigger() {
  chrome.runtime.getPlatformInfo(() => {});

  fetch("http://localhost:5000/trigger")
    .then((res) => res.json())
    .then((data) => {
      if (data.run === true) {
        exportHistory();
      }
    })
    .catch(() => {
      // Python not running yet — silently retry
    });
}

// Start polling automatically
setInterval(pollTrigger, POLL_INTERVAL_MS);
