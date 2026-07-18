const CAPTURE_EVENT = "PAGE_CAPTURE";
const STORAGE_QUEUE_KEY = "memex_capture_queue";

const state = {
  startTimeMs: Date.now(),
  activeStartMs: Date.now(),
  activeTimeMs: 0,
  maxScrollPercent: 0,
  lastVisibilityState: document.visibilityState,
  lastCaptureSent: null,
};

function getPageMetadata() {
  const url = location.href;
  const title = document.title || "";
  const domain = location.hostname;

  const queryMeta = (selector) => {
    const node = document.querySelector(selector);
    return node ? node.getAttribute("content") || "" : "";
  };

  const description =
    queryMeta("meta[name=description]") ||
    queryMeta("meta[property='og:description']") ||
    queryMeta("meta[name='twitter:description']");

  const canonicalUrl =
    document.querySelector("link[rel='canonical']")?.href || url;
  const siteName =
    queryMeta("meta[property='og:site_name']") ||
    queryMeta("meta[name='application-name']") ||
    domain;

  return { url, title, domain, description, canonicalUrl, siteName };
}

const CONTENT_SELECTORS = [
  "article",
  "main",
  "[role=main]",
  "[itemprop=articleBody]",
  "[itemprop=mainEntityOfPage]",
  "#content",
  ".content",
  ".post",
  ".entry-content",
  ".article-body",
];

function isVisibleNode(node) {
  if (!node || node.nodeType !== Node.ELEMENT_NODE) {
    return true;
  }

  const style = window.getComputedStyle(node);
  if (!style || style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
    return false;
  }

  if (node.hidden || node.getAttribute("aria-hidden") === "true") {
    return false;
  }

  return true;
}

function findBestContentElement() {
  const candidates = CONTENT_SELECTORS
    .map((selector) => Array.from(document.querySelectorAll(selector)))
    .flat();

  const scored = candidates
    .filter((element) => element && element.innerText)
    .map((element) => ({
      element,
      textLength: element.innerText.trim().length,
    }))
    .sort((a, b) => b.textLength - a.textLength);

  if (scored.length > 0 && scored[0].textLength > 200) {
    return scored[0].element;
  }

  return document.body;
}

function cleanElement(node) {
  if (!(node instanceof Element)) {
    return;
  }

  const selectorsToRemove = [
    "script",
    "style",
    "noscript",
    "img",
    "svg",
    "iframe",
    "video",
    "audio",
    "canvas",
    "form",
    "button",
    ".advertisement",
    ".ads",
    ".promo",
    ".sidebar",
    ".nav",
    ".footer",
  ];

  selectorsToRemove.forEach((selector) => {
    node.querySelectorAll(selector).forEach((child) => child.remove());
  });

  Array.from(node.children).forEach((child) => {
    if (!isVisibleNode(child)) {
      child.remove();
      return;
    }
    cleanElement(child);
  });
}

function getReadableContent() {
  const main = findBestContentElement();
  if (!main) {
    return "";
  }

  const clone = main.cloneNode(true);
  cleanElement(clone);

  const text = clone.innerText.trim().replace(/\s+/g, " ");
  if (text.length > 0) {
    return text;
  }

  return document.body.innerText.trim().replace(/\s+/g, " ");
}

function getHeadingAnchors() {
  const container = document.querySelector("article") || document.body;
  const headings = Array.from(container.querySelectorAll("h1, h2, h3, h4, h5, h6"));
  const usedIds = new Set();

  return headings
    .map((heading, index) => {
      const text = heading.textContent?.trim() || "";
      if (!text) {
        return null;
      }

      let id = heading.id?.trim();
      if (!id) {
        id = `memex-heading-${index}-${text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}`;
      }

      let uniqueId = id;
      let suffix = 1;
      while (usedIds.has(uniqueId)) {
        uniqueId = `${id}-${suffix}`;
        suffix += 1;
      }

      usedIds.add(uniqueId);
      heading.id = uniqueId;

      return {
        tag: heading.tagName.toLowerCase(),
        text,
        anchor: `#${uniqueId}`,
      };
    })
    .filter(Boolean);
}

function updateScrollDepth() {
  const scrollTop = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  if (scrollHeight <= 0) {
    state.maxScrollPercent = 100;
    return;
  }
  const percent = Math.min(100, Math.round((scrollTop / scrollHeight) * 100));
  if (percent > state.maxScrollPercent) {
    state.maxScrollPercent = percent;
  }
}

function updateVisibility() {
  if (document.visibilityState === "visible" && state.lastVisibilityState !== "visible") {
    state.activeStartMs = Date.now();
  }
  if (document.visibilityState !== "visible" && state.lastVisibilityState === "visible") {
    state.activeTimeMs += Date.now() - state.activeStartMs;
  }
  state.lastVisibilityState = document.visibilityState;
}

function getReadingDurationSeconds() {
  const now = Date.now();
  let activeTimeMs = state.activeTimeMs;
  if (document.visibilityState === "visible") {
    activeTimeMs += now - state.activeStartMs;
  }
  return Math.round(activeTimeMs / 1000);
}

function buildCapturePayload(finalCapture = false) {
  const metadata = getPageMetadata();
  const headings = getHeadingAnchors();
  const content = getReadableContent();
  const now = Date.now();
  const timestamps = {
    capturedAt: new Date(now).toISOString(),
    sourceCreatedAt: new Date(state.startTimeMs).toISOString(),
    lastUpdatedAt: new Date().toISOString(),
  };

  const payload = {
    captureId: `${metadata.url}::${state.startTimeMs}`,
    page: metadata,
    content,
    headings,
    scrollDepthPercent: state.maxScrollPercent,
    readingDurationSeconds: getReadingDurationSeconds(),
    timestamps,
    finalCapture,
  };
  state.lastCaptureSent = payload;
  return payload;
}

async function saveCaptureLocally(payload) {
  if (!chrome.storage?.local) {
    console.warn("chrome.storage.local unavailable, falling back to page localStorage");
    const stored = localStorage.getItem(STORAGE_QUEUE_KEY);
    const queue = stored ? JSON.parse(stored) : [];
    const existingIndex = queue.findIndex((item) => item.captureId === payload.captureId);
    if (existingIndex !== -1) {
      queue[existingIndex] = payload;
    } else {
      queue.push(payload);
    }
    localStorage.setItem(STORAGE_QUEUE_KEY, JSON.stringify(queue));
    console.log("[Memex Content] Saved capture locally", payload.captureId, "queue size", queue.length);
    return;
  }

  const stored = await chrome.storage.local.get(STORAGE_QUEUE_KEY);
  const queue = stored[STORAGE_QUEUE_KEY] || [];
  const existingIndex = queue.findIndex((item) => item.captureId === payload.captureId);
  if (existingIndex !== -1) {
    queue[existingIndex] = payload;
  } else {
    queue.push(payload);
  }
  await chrome.storage.local.set({ [STORAGE_QUEUE_KEY]: queue });
  console.log("[Memex Content] Saved capture locally", payload.captureId, "queue size", queue.length);
}

function sendCapture(finalCapture = false) {
  const payload = buildCapturePayload(finalCapture);
  chrome.runtime.sendMessage({ type: CAPTURE_EVENT, payload }, async (response) => {
    if (chrome.runtime.lastError) {
      console.warn("Memex capture failed to send message", chrome.runtime.lastError.message);
      await saveCaptureLocally(payload);
      return;
    }
    if (response?.status !== "queued") {
      console.warn("Memex capture got unexpected response", response);
      await saveCaptureLocally(payload);
    }
  });
}

function handleVisibilityChange() {
  updateVisibility();
}

function handleScroll() {
  updateScrollDepth();
}

function initCaptureLifecycle() {
  updateScrollDepth();
  updateVisibility();
  window.addEventListener("scroll", handleScroll, { passive: true });
  document.addEventListener("visibilitychange", handleVisibilityChange);
  window.addEventListener("beforeunload", () => sendCapture(true));
  window.addEventListener("pagehide", () => sendCapture(true));
  setTimeout(() => sendCapture(false), 2500);
}

initCaptureLifecycle();
