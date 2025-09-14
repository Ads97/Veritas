// ---- Utilities ----
const $ = (s, el=document) => el.querySelector(s);
const header   = $("#app-header");
const card     = $("#results-card");
const statusEl = $("#status");

// Escape HTML to prevent injection
function esc(s){ return s?.replace(/[&<>"']/g, m=>({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[m])) ?? ""; }

// Normalize Scam Likelihood per contract
function computeLikelihood(clear_outcome, scam_likelihood) {
  if (clear_outcome === false) return "Inconclusive";
  const n = Number(scam_likelihood);
  if (!Number.isFinite(n)) return "Inconclusive";
  // 0–1 → 0–100 rounded integer
  return Math.round(Math.min(Math.max(n, 0), 1) * 100);
}

// Header theme function removed - keeping original header styling from index.html

// Render helpers
function renderReasons(items) {
  const ul = $("#reasons-list");
  const empty = $("#reasons-empty");
  ul.innerHTML = "";
  if (!Array.isArray(items) || items.length === 0) { empty.hidden = false; return; }
  empty.hidden = true;
  for (const [kind, text] of items) {
    const li = document.createElement("li");
    const good = kind === "good";
    const icon = good ? "✅" : "⚠️";
    li.innerHTML = `<span class="${good ? "reason--good" : "reason--bad"}">${icon}</span> ${esc(text||"")}`;
    ul.appendChild(li);
  }
}

function renderAnalyzedData(pairs) {
  const ul = $("#insights-list");
  const empty = $("#insights-empty");
  ul.innerHTML = "";
  if (!Array.isArray(pairs) || pairs.length === 0) { empty.hidden = false; return; }
  empty.hidden = true;
  for (const [label, value] of pairs) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${esc(label||"")}</strong>: ${esc(value||"")}`;
    ul.appendChild(li);
  }
}

function renderQuestions(arr) {
  const ul = $("#questions-list");
  const empty = $("#questions-empty");
  ul.innerHTML = "";
  if (!Array.isArray(arr) || arr.length === 0) { empty.hidden = false; return; }
  empty.hidden = true;
  for (const t of arr) {
    const li = document.createElement("li");
    li.textContent = t || "";
    ul.appendChild(li);
  }
}

// ---- Data load ----
// Preferred: read address from query (?address=...) or from sessionStorage key "veritas_address"
function getInputAddress() {
  const p = new URLSearchParams(location.search).get("address");
  return p || sessionStorage.getItem("veritas_address") || "";
}

async function fetchResults(address) {
  const url = `/api/results?address=${encodeURIComponent(address)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Mock data for demo purposes (since we don't have a real backend)
function getMockResults(address) {
  // Simulate different scenarios based on address content
  const addressLower = address.toLowerCase();
  const isHighRisk = addressLower.includes('mathilda');
  const isLowRisk = addressLower.includes('king st');
  
  if (isHighRisk) {
    return {
      clear_outcome: true,
      scam_likelihood: 0.85,
      address: address,
      reasons: [
        ["bad", "Landlord requesting wire transfer before viewing property"],
        ["bad", "Price significantly below market rate for the area"],
        ["bad", "Landlord claims to be out of country"],
        ["bad", "Pressure to send money quickly"],
        ["good", "Property photos appear to be legitimate"]
      ],
      analyzed_data: [
        ["Rental Price", "$1,200/month (65% below market average)"],
        ["Market Average", "$3,400/month for similar properties"],
        ["Landlord Contact", "Email only, no phone verification"],
        ["Property History", "Recently listed on multiple platforms"],
        ["Payment Method", "Wire transfer requested (high risk)"]
      ],
      additional_questions: [
        "Have you been able to verify the landlord's identity through official channels?",
        "Can you schedule an in-person viewing of the property?",
        "Has the landlord provided verifiable references or credentials?",
        "Are there any official property management companies associated with this listing?"
      ]
    };
  } else if (isLowRisk) {
    return {
      clear_outcome: true,
      scam_likelihood: 0.15,
      address: address,
      reasons: [
        ["good", "Landlord provided verifiable contact information"],
        ["good", "Property price is within market range"],
        ["good", "In-person viewing scheduled and confirmed"],
        ["bad", "Limited online presence for the property"]
      ],
      analyzed_data: [
        ["Rental Price", "$2,800/month (within market range)"],
        ["Market Average", "$3,200/month for similar properties"],
        ["Landlord Contact", "Phone and email verified"],
        ["Property History", "Listed by established real estate agency"],
        ["Payment Method", "Standard lease agreement and deposit"]
      ],
      additional_questions: [
        "Have you completed the background check process?",
        "Are all lease terms clearly documented?",
        "Have you verified the property management company's credentials?"
      ]
    };
  } else {
    // Default inconclusive case
    return {
      clear_outcome: false,
      scam_likelihood: 0.5,
      address: address,
      reasons: [
        ["bad", "Limited information available for analysis"],
        ["good", "No obvious red flags detected"]
      ],
      analyzed_data: [
        ["Information Available", "Insufficient data for complete analysis"],
        ["Recommendation", "Gather more information before proceeding"]
      ],
      additional_questions: [
        "Can you provide more details about the landlord?",
        "What payment methods are being requested?",
        "Have you been able to view the property in person?",
        "Are there any unusual requests or pressure tactics?"
      ]
    };
  }
}

// ---- Page init ----
window.addEventListener("DOMContentLoaded", async () => {
  statusEl.innerHTML = `
    <div class="status-card">
      <div class="status-header">
        <h4>Loading results…</h4>
        <span class="status-spinner" aria-hidden="true"></span>
      </div>
      <div class="status-content"><p>Fetching analysis…</p></div>
    </div>`;

  try {
    const address = getInputAddress();
    
    // For demo purposes, use mock data instead of real API call
    // In production, replace this with: const data = await fetchResults(address);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate loading time
    const data = getMockResults(address);

    // Compute score text
    const score = computeLikelihood(data.clear_outcome, data.scam_likelihood);

    // Populate header/summary
    $("#result-address").textContent = `Results for ${data.address || address || "Unknown Address"}`;
    $("#likelihood-value").textContent = (score === "Inconclusive") ? "Inconclusive" : `${score}%`;

    // Apply conditional styling to likelihood box
    const likelihoodEl = $(".likelihood");
    likelihoodEl.classList.remove("likelihood--high", "likelihood--low", "likelihood--inconclusive");
    if (score === "Inconclusive") {
      likelihoodEl.classList.add("likelihood--inconclusive");
    } else if (score > 50) {
      likelihoodEl.classList.add("likelihood--high");
    } else {
      likelihoodEl.classList.add("likelihood--low");
    }

    // Render lists
    renderReasons(data.reasons || []);
    renderAnalyzedData(data.analyzed_data || []);
    renderQuestions(data.additional_questions || []);

    statusEl.innerHTML = "";
    card.hidden = false;
  } catch (e) {
    console.error('Error loading results:', e);
    statusEl.innerHTML = `
      <div class="error-alert">
        <div class="alert-content">
          <h4>Unable to load results</h4>
          <p>Please retry.</p>
          <button class="retry-btn" onclick="location.reload()">Retry</button>
          <a class="btn" href="index.html" style="margin-left:.5rem;">Restart</a>
        </div>
      </div>`;
  }
});
