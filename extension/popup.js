// Load saved URLs when popup opens
function loadUrls(callback) {
  chrome.storage.local.get(["urls"], (result) => {
    callback(result.urls || []);
  });
}

function saveUrls(urls) {
  chrome.storage.local.set({ urls });
}

function renderAdded(urls) {
  const div = document.getElementById("added");
  div.innerHTML = urls.map(u => `<div class="laptop-slot">✅ ${u.slice(0, 55)}...</div>`).join("");
}

// Show whatever was already added, every time the popup opens
loadUrls((urls) => renderAdded(urls));

document.getElementById("addBtn").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs[0].url;
    if (!url || !url.includes("flipkart.com")) {
      alert("Please switch to a Flipkart product page first.");
      return;
    }
    loadUrls((urls) => {
      urls.push(url);
      saveUrls(urls);
      renderAdded(urls);
    });
  });
});

document.getElementById("compareBtn").addEventListener("click", async () => {
  loadUrls(async (urls) => {
    if (urls.length < 2) {
      alert("Add at least 2 laptops first (visit each product page and click 'Add').");
      return;
    }

    const useCase = document.getElementById("useCase").value;
    const resultDiv = document.getElementById("result");
    resultDiv.innerText = "Fetching pages and comparing... (may take 10-15 sec)";

    try {
      const res = await fetch("http://127.0.0.1:8000/compare-urls", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls, use_case: useCase })
      });
      const data = await res.json();

      if (data.error) {
        resultDiv.innerText = "Error: " + data.error;
        return;
      }

      resultDiv.innerHTML = `
        <b>🏆 Best Overall:</b> ${data.verdict.best_overall}<br>
        <b>💰 Best Value:</b> ${data.verdict.best_value}<br>
        <b>🎯 Best for ${useCase}:</b> ${data.verdict.best_for_use_case}<br><br>
        ${data.summary}
      `;
    } catch (err) {
      resultDiv.innerText = "Error: " + err.message;
    }
  });
});

document.getElementById("clearBtn").addEventListener("click", () => {
  saveUrls([]);
  renderAdded([]);
  document.getElementById("result").innerText = "";
});