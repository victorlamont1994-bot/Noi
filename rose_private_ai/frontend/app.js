const API = "http://127.0.0.1:8000";

const statusEl = document.getElementById("status");
const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const uploadResult = document.getElementById("uploadResult");
const sendBtn = document.getElementById("sendBtn");
const messageEl = document.getElementById("message");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");
const strictSourcesEl = document.getElementById("strictSources");
const apiKeyEl = document.getElementById("apiKey");
const saveKeyBtn = document.getElementById("saveKeyBtn");
const clearKeyBtn = document.getElementById("clearKeyBtn");

apiKeyEl.value = localStorage.getItem("ROSE_API_KEY") || "";

function roseHeaders(extra = {}) {
  const key = localStorage.getItem("ROSE_API_KEY") || "";
  const headers = {...extra};
  if (key) headers["x-rose-api-key"] = key;
  return headers;
}

saveKeyBtn.addEventListener("click", () => {
  localStorage.setItem("ROSE_API_KEY", apiKeyEl.value.trim());
  statusEl.textContent = "API key saved locally";
});

clearKeyBtn.addEventListener("click", () => {
  localStorage.removeItem("ROSE_API_KEY");
  apiKeyEl.value = "";
  statusEl.textContent = "API key cleared";
});

async function checkHealth() {
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    statusEl.textContent = `API online · ${data.model} · key required: ${data.api_key_required}`;
    statusEl.classList.add("ok");
  } catch (err) {
    statusEl.textContent = "API offline";
    statusEl.classList.add("bad");
  }
}

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadResult.textContent = "Select a file first.";
    return;
  }

  const form = new FormData();
  form.append("file", file);

  uploadResult.textContent = "Ingesting...";
  try {
    const res = await fetch(`${API}/ingest`, {
      method: "POST",
      headers: roseHeaders(),
      body: form
    });
    const data = await res.json();
    uploadResult.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    uploadResult.textContent = String(err);
  }
});

sendBtn.addEventListener("click", async () => {
  const message = messageEl.value.trim();
  if (!message) {
    answerEl.textContent = "Enter a question first.";
    return;
  }

  answerEl.textContent = "ROSE is analyzing...";
  sourcesEl.textContent = "";

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: roseHeaders({"Content-Type": "application/json"}),
      body: JSON.stringify({
        message,
        strict_sources: strictSourcesEl.checked
      })
    });

    const data = await res.json();

    if (!res.ok) {
      answerEl.textContent = data.detail || "Request failed.";
      return;
    }

    answerEl.textContent = data.answer;
    sourcesEl.textContent = JSON.stringify(data.sources, null, 2);
  } catch (err) {
    answerEl.textContent = String(err);
  }
});

checkHealth();
