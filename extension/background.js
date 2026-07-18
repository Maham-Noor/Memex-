const CAPTURE_EVENT = "PAGE_CAPTURE";
const STORAGE_QUEUE_KEY = "memex_capture_queue";
const BACKEND_CAPTURE_URL = "http://127.0.0.1:8000/capture/";
const RETRY_ALARM_NAME = "memexRetry";
const RETRY_FALLBACK_TIMEOUT_MS = 60_000;
let retryTimeoutId = null;

async function initializeQueue() {
  const stored = await chrome.storage.local.get(STORAGE_QUEUE_KEY);
  if (!stored[STORAGE_QUEUE_KEY]) {
    await chrome.storage.local.set({ [STORAGE_QUEUE_KEY]: [] });
  }
}

function scheduleFallbackRetry() {
  if (chrome.alarms?.create) {
    return;
  }
  if (retryTimeoutId) {
    clearTimeout(retryTimeoutId);
  }
  retryTimeoutId = setTimeout(async () => {
    await handleQueueSend().catch((error) => log("Fallback retry failed", error.message));
    scheduleFallbackRetry();
  }, RETRY_FALLBACK_TIMEOUT_MS);
}

function log(...args) {
  console.log("[Memex Background]", ...args);
}

async function getQueue() {
  const result = await chrome.storage.local.get(STORAGE_QUEUE_KEY);
  return result[STORAGE_QUEUE_KEY] || [];
}

async function setQueue(queue) {
  await chrome.storage.local.set({ [STORAGE_QUEUE_KEY]: queue });
}

async function enqueueCapture(payload) {
  const queue = await getQueue();
  const existingIndex = queue.findIndex((item) => item.captureId === payload.captureId);
  if (existingIndex !== -1) {
    queue[existingIndex] = payload;
  } else {
    queue.push(payload);
  }
  await setQueue(queue);
  log("Enqueued capture", payload.captureId, "queue size", queue.length);
}

async function dispatchCapture(payload) {
  const response = await fetch(BACKEND_CAPTURE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Backend rejected capture: ${response.status} ${response.statusText}`);
  }

  const body = await response.json();
  log("Dispatched capture", payload.captureId, "response", body);
  return body;
}

async function handleQueueSend() {
  const queue = await getQueue();
  if (!queue.length) {
    log("Queue is empty, nothing to send");
    return;
  }

  const remaining = [];
  for (const payload of queue) {
    try {
      await dispatchCapture(payload);
    } catch (error) {
      log("Capture dispatch failed, keeping payload in queue", payload.captureId, error.message);
      remaining.push(payload);
    }
  }

  await setQueue(remaining);
  log("Queue flush complete", { sent: queue.length - remaining.length, remaining: remaining.length });
}

chrome.runtime.onInstalled.addListener(() => {
  log("Installed extension and initializing queue");
  initializeQueue()
    .then(() => {
      if (chrome.alarms?.create) {
        chrome.alarms.create(RETRY_ALARM_NAME, { periodInMinutes: 1 });
      } else {
        log("chrome.alarms.create unavailable; retry alarms not scheduled");
        scheduleFallbackRetry();
      }
    })
    .then(handleQueueSend);
});

chrome.runtime.onStartup.addListener(() => {
  log("Extension startup");
  initializeQueue()
    .then(() => {
      if (chrome.alarms?.create) {
        chrome.alarms.create(RETRY_ALARM_NAME, { periodInMinutes: 1 });
      } else {
        log("chrome.alarms.create unavailable; retry alarms not scheduled");
        scheduleFallbackRetry();
      }
    })
    .then(handleQueueSend);
});

if (chrome.alarms?.onAlarm?.addListener) {
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name !== RETRY_ALARM_NAME) {
      return;
    }
    log("Retry alarm fired", alarm.name);
    handleQueueSend().catch((error) => log("Retry flush failed", error.message));
  });
} else {
  log("chrome.alarms is unavailable; retry alarm support is disabled");
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === CAPTURE_EVENT) {
    const payload = message.payload;
    if (!payload?.captureId) {
      sendResponse({ status: "error", error: "Capture payload missing captureId" });
      return true;
    }

    enqueueCapture(payload)
      .then(() => handleQueueSend())
      .then(() => sendResponse({ status: "queued" }))
      .catch((error) => {
        console.error("Failed to enqueue capture", error);
        sendResponse({ status: "error", error: error.message });
      });

    return true;
  }

  if (message?.type === "MEMEX_QUEUE_INFO") {
    getQueue()
      .then((queue) => sendResponse({ status: "ok", queueLength: queue.length }))
      .catch((error) => sendResponse({ status: "error", error: error.message }));
    return true;
  }

  if (message?.type === "MEMEX_QUEUE_FLUSH") {
    handleQueueSend()
      .then(() => sendResponse({ status: "ok" }))
      .catch((error) => sendResponse({ status: "error", error: error.message }));
    return true;
  }

  return false;
});

chrome.action.onClicked.addListener(async (tab) => {
  log("Action clicked", tab?.id);
  const queue = await getQueue();
  if (tab.id != null) {
    chrome.tabs.sendMessage(tab.id, { type: "MEMEX_QUEUE_UPDATE", queueLength: queue.length });
  }
});

