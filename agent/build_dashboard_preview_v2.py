from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCE_SITE = ROOT / "site"
PREVIEW_SITE = ROOT / "preview" / "alforaijboard-v2"
ASSETS = ROOT / "agent" / "assets"


PREVIEW_CSS = r"""
  <style id="professional-preview-v2">
    :root {
      --ink: #071426;
      --muted: #304158;
      --line: #b9c8db;
      --bg: #f3f6fa;
      --blue: #1748c7;
      --orange: #bd5700;
      --green: #00694f;
    }
    body {
      color: var(--ink);
      background: var(--bg);
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
      font-weight: 500;
    }
    label, .panel-hint, .action-toolbar span, .result-head span, .desc {
      color: #304158;
    }
    input, select, button, .action-button {
      color: #0b1729;
      border-color: #b9c8db;
    }
    input::placeholder { color: #65758a; opacity: 1; }
    .metric, .panel, .toolbar, .action-toolbar {
      border-color: #b9c8db;
      box-shadow: 0 5px 16px rgba(15, 23, 42, .07);
    }
    .summary-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .metric small, .metric span, .facts span, .summary-strip b {
      color: #2d3e55;
    }
    .metric-grid {
      grid-template-columns: repeat(5, minmax(190px, 1fr));
    }
    .metric {
      min-height: 148px;
      display: flex;
      flex-direction: column;
      align-items: stretch;
    }
    .metric strong { color: var(--ink); }
    .metric em { margin-top: auto; align-self: flex-start; }
    header {
      min-height: 218px;
      padding-block: 26px;
      background:
        linear-gradient(90deg, rgba(15, 23, 42, 0.97), rgba(15, 23, 42, 0.82) 54%, rgba(15, 23, 42, 0.50)),
        var(--navy);
    }
    .hero-content {
      min-height: 158px;
      grid-template-columns: minmax(0, 1.06fr) minmax(360px, 0.94fr);
    }
    .logo-showcase {
      min-height: 142px;
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.34);
      border-color: rgba(255, 255, 255, 0.28);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 18px 44px rgba(2,6,23,.28);
    }
    .logo-showcase::before,
    .logo-showcase::after { display: none; }
    .brand-logo {
      width: min(92%, 430px);
      min-height: 0;
      max-height: 108px;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
      object-fit: contain;
      filter: drop-shadow(0 4px 10px rgba(2, 6, 23, 0.32));
    }
    .hero-title {
      background: rgba(15, 23, 42, 0.38);
      border-radius: 6px;
    }
    .hero-title h1 { font-size: 36px; }
    .hero-title p { font-size: 19px; line-height: 1.65; }
    .intelligence-grid {
      display: grid;
      margin: 0;
    }
    .layout.operational-layout {
      grid-template-columns: minmax(420px, .9fr) minmax(0, 1.1fr);
      align-items: start;
    }
    .operational-side {
      display: grid;
      gap: 18px;
      min-width: 0;
    }
    .operational-side > .panel { width: 100%; min-width: 0; }
    .operational-side .match-list { grid-template-columns: 1fr; }
    .operational-results .list {
      max-height: none;
      overflow: visible;
      padding-left: 0;
    }
    .operational-results .result-progress {
      position: static;
      margin-top: 16px;
    }
    .load-all {
      border-color: #0f172a;
      background: #0f172a;
      color: #fff;
    }
    .load-all:hover { background: #17243b; }
    .result-evidence {
      margin: 10px 0 0;
      padding: 10px 12px;
      border-right: 4px solid var(--blue);
      background: #f4f8ff;
      color: #24364d;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.65;
    }
    .evidence-line {
      margin: 10px 0 0;
      color: #24364d;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.65;
    }
    .evidence-line b { color: #0b3c8c; }
    .table-scroll {
      overflow-x: hidden !important;
    }
    #govTable {
      table-layout: fixed;
      width: 100%;
      min-width: 0 !important;
    }
    #govTable th,
    #govTable td {
      padding: 7px 6px;
    }
    #govTable th {
      font-size: 13px;
      line-height: 1.25;
    }
    .governor-name-cell {
      width: 30%;
      min-width: 0;
    }
    .governor-name-wrap {
      display: grid;
      gap: 6px;
      justify-items: stretch;
      align-items: center;
    }
    .governor-name-text {
      font-size: 16px;
      font-weight: 900;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .governor-toggle {
      width: auto;
      max-width: 86px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 5px 9px;
      border: 1px solid #b9c8db;
      border-radius: 6px;
      background: #fff;
      color: var(--blue);
      font-size: 12px;
      font-weight: 900;
      cursor: pointer;
      text-align: center;
    }
    .governor-toggle:hover {
      border-color: #2554d9;
      background: #edf4ff;
    }
    .governor-toggle[aria-expanded="true"] {
      border-color: #2554d9;
      background: #edf4ff;
      color: #123b7a;
    }
    .governor-toggle-icon {
      display: none;
    }
    .area-detail-row td {
      padding: 0;
      background: #f8fbff;
      border-top: 0;
    }
    .area-breakdown {
      padding: 10px;
      border-right: 4px solid #2554d9;
    }
    .area-breakdown-title {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
      color: #24364d;
      font-size: 12px;
      font-weight: 900;
    }
    .area-breakdown-grid {
      display: grid;
      gap: 7px;
    }
    .area-breakdown-row {
      display: grid;
      grid-template-columns: minmax(92px, 1.18fr) repeat(5, minmax(34px, .64fr));
      gap: 5px;
      align-items: center;
    }
    .area-breakdown-row.area-active {
      padding: 4px;
      border: 1px solid #9fc2f4;
      border-radius: 7px;
      background: #eef6ff;
    }
    .area-breakdown-row.metric-active-row {
      padding: 4px;
      border-radius: 7px;
      background: #f7fbff;
    }
    .area-name {
      min-height: 32px;
      padding: 5px 6px;
      border: 1px solid #c9d6e8;
      border-radius: 6px;
      background: #fff;
      font-size: 11px;
      font-weight: 900;
      line-height: 1.35;
    }
    .area-breakdown-row.area-active .area-name,
    .area-breakdown-row.metric-active-row .area-name {
      border-color: #2554d9;
      background: #fff;
      color: #123b7a;
    }
    .area-count-button {
      min-height: 30px;
      padding: 3px 4px;
      border: 1px solid #c9d6e8;
      border-radius: 6px;
      background: #fff;
      color: #0b1729;
      font-size: 12px;
      font-weight: 900;
      cursor: pointer;
    }
    .area-count-button:disabled {
      color: #8a98aa;
      cursor: default;
      background: #f1f5f9;
    }
    .area-count-button.empty-count {
      color: #94a3b8;
      background: #f8fafc;
      border-color: #d7e1ef;
    }
    .area-count-button:not(:disabled):hover {
      border-color: #2554d9;
      background: #edf4ff;
      color: #123b7a;
    }
    .area-count-button.metric-active:not(.empty-count) {
      border-color: #2554d9;
      background: #eef4ff;
      color: #0f4bd8;
      box-shadow: inset 0 -3px 0 #f6c431;
    }
    .area-breakdown-row.area-active .area-count-button.metric-active:not(.empty-count) {
      background: #e4efff;
      box-shadow: inset 0 0 0 2px rgba(37,84,217,.22), inset 0 -3px 0 #f6c431;
    }
    .area-breakdown-labels {
      display: grid;
      grid-template-columns: minmax(92px, 1.18fr) repeat(5, minmax(34px, .64fr));
      gap: 5px;
      margin-bottom: 6px;
      color: #304158;
      font-size: 10px;
      font-weight: 900;
      text-align: center;
    }
    .area-breakdown-labels span {
      padding: 3px 2px;
      border-radius: 4px;
      background: #eef4fb;
    }
    .match-method {
      margin: -4px 0 14px;
      padding: 11px 13px;
      border-right: 4px solid var(--blue);
      background: #f4f8ff;
      color: #24364d;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.7;
    }
    .gov-map-active {
      outline: 3px solid rgba(37,84,217,.2);
      outline-offset: 3px;
    }
    .match-panel { min-width: 0; }
    .match-disclosure {
      padding: 0;
      overflow: hidden;
    }
    .match-disclosure-summary {
      position: relative;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      min-height: 68px;
      padding: 15px 52px 15px 18px;
      background: #fff;
      color: #111827;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }
    .match-disclosure-summary::-webkit-details-marker { display: none; }
    .match-disclosure-summary::before {
      content: "\25BC";
      position: absolute;
      right: 20px;
      top: 50%;
      transform: translateY(-50%);
      color: #123b7a;
      font-size: 15px;
    }
    .match-disclosure[open] > .match-disclosure-summary::before { content: "\25B2"; }
    .match-disclosure[open] > .match-disclosure-summary {
      border-bottom: 1px solid #b9c8db;
      background: #f3f7ff;
    }
    .match-disclosure-summary strong {
      display: block;
      font-size: 22px;
    }
    .match-disclosure-summary small {
      color: #304158;
      font-size: 13px;
      font-weight: 800;
    }
    .match-disclosure-count {
      flex: 0 0 auto;
      padding: 7px 11px;
      border: 1px solid #9fc2f4;
      border-radius: 5px;
      background: #fff;
      color: #123b7a;
      font-size: 13px;
      font-weight: 900;
    }
    .match-disclosure-body { padding: 18px; }
    .match-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 18px;
      margin-bottom: 16px;
    }
    .match-head h2 { margin: 0; font-size: 25px; }
    .match-head p {
      margin: 6px 0 0;
      color: #304158;
      font-size: 14px;
      font-weight: 700;
    }
    .match-controls, .match-print-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .match-sector, .match-print {
      min-height: 42px;
      padding: 8px 13px;
      border: 1px solid #aebfd4;
      border-radius: 6px;
      background: #fff;
      color: #13233a;
      font: inherit;
      font-weight: 900;
      cursor: pointer;
    }
    .match-sector:hover, .match-print:hover {
      border-color: var(--blue);
      color: var(--blue);
    }
    .match-sector.active {
      border-color: var(--blue);
      background: var(--blue);
      color: #fff;
    }
    .match-print.primary {
      border-color: #003d91;
      background: #0b3c8c;
      color: #fff;
    }
    .match-summary {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin: 0 0 16px;
      border-top: 1px solid #b9c8db;
      border-right: 1px solid #b9c8db;
    }
    .match-summary > div {
      min-height: 78px;
      padding: 12px;
      border-left: 1px solid #b9c8db;
      border-bottom: 1px solid #b9c8db;
      background: #fff;
    }
    .match-summary span {
      display: block;
      color: #304158;
      font-size: 12px;
      font-weight: 800;
    }
    .match-summary strong {
      display: block;
      margin-top: 4px;
      color: #071426;
      font-size: 24px;
    }
    .match-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .match-card {
      border: 1px solid #b9c8db;
      border-radius: 7px;
      background: #fff;
      overflow: hidden;
    }
    .match-group-card.has-multiple-offers {
      border: 2px solid #2554d9;
      box-shadow: 0 5px 16px rgba(18, 59, 122, .12);
    }
    .match-group-card.has-multiple-offers .match-card-head {
      background: #e8f0ff;
      border-bottom-color: #9fc2f4;
    }
    .match-card-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 12px 14px;
      background: #eef4ff;
      border-bottom: 1px solid #c6d4e6;
    }
    .match-card-head strong { font-size: 17px; }
    .match-group-count {
      min-width: 112px;
      padding: 5px 9px;
      border: 1px solid #9fc2f4;
      border-radius: 5px;
      background: #fff;
      color: #123b7a;
      text-align: center;
      font-size: 13px;
      font-weight: 900;
    }
    .match-group-count.multiple {
      border-color: #123b7a;
      background: #123b7a;
      color: #fff;
    }
    .match-alternatives-heading {
      padding: 10px 12px;
      border-bottom: 1px solid #b9c8db;
      background: #dbe8ff;
      color: #102e5c;
      font-size: 13px;
      font-weight: 900;
    }
    .match-request-overview {
      padding: 12px;
      border-bottom: 1px solid #c6d4e6;
      background: #f8fbff;
    }
    .match-request-overview .match-side { padding: 0; }
    .match-request-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: 10px;
    }
    .match-request-actions button, .match-request-actions a {
      flex: 1 1 150px;
      min-height: 36px;
      padding: 7px 10px;
      border: 1px solid #aebfd4;
      border-radius: 6px;
      background: #fff;
      color: #17345f;
      text-align: center;
      text-decoration: none;
      font: inherit;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
    }
    .match-offers {
      display: grid;
      gap: 10px;
      padding: 12px;
      background: #eef3f8;
    }
    .match-offer-option {
      overflow: hidden;
      border: 1px solid #b9c8db;
      border-radius: 6px;
      background: #fff;
    }
    .match-offer-option.best-option {
      border-color: #2554d9;
      box-shadow: inset -4px 0 #2554d9;
    }
    .match-offer-option.best-option .match-offer-head {
      background: #eef4ff;
    }
    .match-offer-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      padding: 9px 11px;
      border-bottom: 1px solid #d6e0ec;
      background: #fff;
    }
    .match-offer-head strong { font-size: 14px; color: #17345f; }
    .match-offer-option > .match-side { padding: 11px 13px; }
    .match-score {
      min-width: 78px;
      padding: 5px 9px;
      border-radius: 5px;
      background: #0b3c8c;
      color: #fff;
      text-align: center;
      font-size: 13px;
      font-weight: 900;
    }
    .match-score.potential { background: #8a4b05; }
    .match-score.review { background: #4b5f79; }
    .match-pair {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1px;
      background: #c6d4e6;
    }
    .match-side {
      min-width: 0;
      padding: 13px;
      background: #fff;
    }
    .match-side b {
      display: block;
      color: #0b3c8c;
      font-size: 13px;
    }
    .match-side strong {
      display: block;
      margin-top: 5px;
      font-size: 17px;
      overflow-wrap: anywhere;
    }
    .match-side span {
      display: block;
      margin-top: 4px;
      color: #304158;
      font-size: 13px;
      font-weight: 700;
    }
    .match-reasons {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 11px 13px;
      border-top: 1px solid #d3ddea;
    }
    .match-reason {
      padding: 4px 8px;
      border: 1px solid #b8cbed;
      border-radius: 999px;
      background: #f3f7ff;
      color: #123b7a;
      font-size: 12px;
      font-weight: 800;
    }
    .match-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      padding: 0 13px 13px;
    }
    .match-actions button, .match-actions a {
      flex: 1 1 150px;
      min-height: 38px;
      padding: 7px 10px;
      border: 1px solid #aebfd4;
      border-radius: 6px;
      background: #fff;
      color: #17345f;
      text-align: center;
      text-decoration: none;
      font: inherit;
      font-size: 13px;
      font-weight: 900;
      cursor: pointer;
    }
    .match-empty {
      padding: 26px;
      border: 1px dashed #9eb0c6;
      border-radius: 7px;
      background: #f8fafc;
      color: #304158;
      text-align: center;
      font-weight: 800;
    }
    .match-more {
      display: block;
      width: min(100%, 360px);
      min-height: 44px;
      margin: 14px auto 0;
      border: 1px solid #1748c7;
      border-radius: 6px;
      background: #fff;
      color: #1748c7;
      font: inherit;
      font-weight: 900;
      cursor: pointer;
    }
    .match-more:hover { background: #eef4ff; }
    .match-more[hidden] { display: none; }
    .match-caution {
      margin: 14px 0 0;
      padding: 10px 12px;
      border-right: 4px solid #bd5700;
      background: #fff7ed;
      color: #5c2a08;
      font-size: 13px;
      font-weight: 800;
    }
    @media (max-width: 1050px) {
      .hero-content { grid-template-columns: 1fr; }
      .layout.operational-layout { grid-template-columns: 1fr; }
      .metric-grid { grid-template-columns: repeat(2, minmax(180px, 1fr)); }
      .match-list { grid-template-columns: 1fr; }
    }
    @media (min-width: 1051px) {
      .operational-side .match-list {
        max-height: 680px;
        overflow-y: auto;
        padding-left: 4px;
      }
    }
    @media (max-width: 640px) {
      header { min-height: 0; }
      .logo-showcase { min-height: 96px; }
      .brand-logo { width: min(94%, 360px); max-height: 82px; }
      .hero-title h1 { font-size: 25px; }
      .hero-title p { font-size: 16px; }
      .match-disclosure-summary {
        align-items: flex-start;
        padding-left: 12px;
      }
      .match-disclosure-summary strong { font-size: 18px; }
      .match-disclosure-count { font-size: 12px; }
      .match-head { display: block; }
      .match-controls { margin-top: 12px; }
      .match-summary { grid-template-columns: 1fr; }
      .match-pair { grid-template-columns: 1fr; }
      .match-sector, .match-print { flex: 1 1 100%; }
      .metric-grid { grid-template-columns: 1fr; }
      .result-evidence, .evidence-line {
        font-size: 13px;
      }
    }
  </style>
"""


INTELLIGENCE_HTML = r"""
    <section class="intelligence-grid" aria-label="فرص التوفيق">
      <details id="matchDisclosure" class="panel match-panel match-disclosure">
        <summary class="match-disclosure-summary">
          <span>
            <strong>العروض والطلبات</strong>
            <small>اضغط لعرض الفرص أو إخفائها</small>
          </span>
          <span id="matchDisclosureCount" class="match-disclosure-count">جارٍ تجهيز النتائج</span>
        </summary>
        <div class="match-disclosure-body">
        <div class="match-head">
          <div>
            <h2>الفرص المطابقة للشروط</h2>
            <p>مطابقة تشغيلية حسب المحافظة والمنطقة ونوع العقار والسعر وحداثة الإعلان.</p>
          </div>
          <div class="match-controls" aria-label="اختيار قطاع التوفيق">
            <button class="match-sector active" type="button" data-sector="sale">البيع والشراء</button>
            <button class="match-sector" type="button" data-sector="rent">الإيجار وطلباته</button>
          </div>
        </div>
        <p class="match-method"><b>شروط المطابقة الأساسية:</b> توافق المحافظة والمنطقة ونوع العقار وحالته والسعر المطلوب. تُستبعد تلقائيًا العروض الواقعة خارج نطاق السعر أو المخالفة لحالة العقار المطلوبة.</p>
        <div id="matchSummary" class="match-summary"></div>
        <div class="match-print-actions" aria-label="طباعة العرض والطلب">
          <button class="match-print primary" type="button" data-print-sector="sale">طباعة عروض البيع وطلبات الشراء</button>
          <button class="match-print" type="button" data-print-sector="rent">طباعة عروض الإيجار وطلباته</button>
        </div>
        <div id="matchList" class="match-list"></div>
        <button id="matchLoadMore" class="match-more" type="button">عرض المزيد</button>
        <p class="match-caution">هذه فرص أولية للمراجعة والتواصل، وليست تأكيدًا لإتمام صفقة.</p>
        </div>
      </details>
    </section>
"""


PREVIEW_JS = r"""
  <script id="professional-preview-v2-script">
    const governorateNameMap = {
      "Ahmadi": "محافظة الاحمدي",
      "Al Asimah": "محافظة العاصمة",
      "Farwaniya": "محافظة الفروانية",
      "Hawalli": "محافظة حولي",
      "Jahra": "محافظة الجهراء",
      "Mubarak Al-Kabeer": "محافظة مبارك الكبير"
    };
    const comparisonMetrics = ["movement", "sell", "buy", "rent", "rent_request"];
    let activeMatchSector = "sale";
    let visibleMatchLimit = 10;
    let lastMatchScopeKey = "";

    function initializeDashboardTabs() {
      const layout = document.querySelector(".layout");
      const governoratePanel = document.getElementById("govTable").closest(".panel");
      const resultPanel = document.getElementById("resultList").closest(".panel");
      const operationalSide = document.createElement("div");
      operationalSide.className = "operational-side";
      layout.classList.add("operational-layout");
      layout.insertBefore(operationalSide, governoratePanel);
      operationalSide.append(governoratePanel);
      resultPanel.classList.add("operational-results");
      const resultEvidence = document.createElement("p");
      resultEvidence.id = "resultEvidence";
      resultEvidence.className = "result-evidence";
      document.getElementById("resultStats").after(resultEvidence);
    }

    function nonTransactionScopeRows() {
      return records.filter(row => rowMatchesSharedFilters(row, true, false));
    }

    function metricRows(metric) {
      return nonTransactionScopeRows().filter(row => matchesMetric(row, metric));
    }

    function percentage(part, whole) {
      if (!whole) return 0;
      return Math.round((part * 1000) / whole) / 10;
    }

    function renderProfessionalMetrics() {
      const grid = document.getElementById("metricGrid");
      if (!grid) return;
      const allRows = nonTransactionScopeRows();
      const metricOrder = ["movement", "sell", "buy", "rent", "rent_request"];
      grid.innerHTML = "";
      metricOrder.forEach(metric => {
        const rows = metric === "movement" ? allRows : metricRows(metric);
        const priced = rows.filter(row => Number.isFinite(Number(row.price)) && Number(row.price) > 0);
        const button = document.createElement("button");
        button.className = "metric";
        button.dataset.metric = metric;
        button.classList.toggle("active", state.metric === metric);

        const label = document.createElement("span");
        label.textContent = metricLabels[metric];
        const count = document.createElement("strong");
        count.textContent = formatNumber(rows.length);
        const price = document.createElement("small");
        price.textContent = metric === "movement"
          ? "إجمالي البنود الأربعة"
          : `أسعار معلنة: ${formatNumber(priced.length)} من ${formatNumber(rows.length)}`;
        const action = document.createElement("em");
        action.textContent = "اضغط للاختيار";
        button.append(label, count, price, action);
        button.addEventListener("click", () => applyFilter(metric));
        grid.appendChild(button);
      });
    }

    function rowMatchesSharedFilters(row, includeGovernorate = false, includeTransaction = true) {
      const q = normalizeText(document.getElementById("searchBox").value);
      const priceMode = document.getElementById("priceFilter").value;
      const listingMode = document.getElementById("listingModeFilter").value;
      const transaction = document.getElementById("transactionFilter").value;
      const property = document.getElementById("propertyFilter").value;
      const area = document.getElementById("areaFilter").value;
      if (includeGovernorate && !matchesChoice(row.governorate, selectedGovernorate())) return false;
      if (includeTransaction && !matchesChoice(row.transaction, transaction)) return false;
      if (!matchesChoice(row.property_type, property)) return false;
      if (!matchesChoice(row.area, area)) return false;
      if (listingMode && listingModeGroup(row.listingMode) !== listingMode) return false;
      if (priceMode === "priced" && !row.price) return false;
      if (priceMode === "unpriced" && row.price) return false;
      if (!q) return true;
      return [
        row.code, row.transaction, row.property_type, row.detail_class,
        row.governorate, row.area, row.priceText, row.listingMode,
        row.summary, row.features, row.publishedDate, row.detailText
      ].map(normalizeText).join(" ").includes(q);
    }

    function rowMatchesReferenceFilters(row, includeGovernorate = false, includeTransaction = true) {
      const q = normalizeText(document.getElementById("searchBox").value);
      const priceMode = document.getElementById("priceFilter").value;
      const listingMode = document.getElementById("listingModeFilter").value;
      const transaction = document.getElementById("transactionFilter").value;
      const property = document.getElementById("propertyFilter").value;
      if (includeGovernorate && !matchesChoice(row.governorate, selectedGovernorate())) return false;
      if (includeTransaction && !matchesChoice(row.transaction, transaction)) return false;
      if (!matchesChoice(row.property_type, property)) return false;
      if (listingMode && listingModeGroup(row.listingMode) !== listingMode) return false;
      if (priceMode === "priced" && !row.price) return false;
      if (priceMode === "unpriced" && row.price) return false;
      if (!q) return true;
      return [
        row.code, row.transaction, row.property_type, row.detail_class,
        row.governorate, row.area, row.priceText, row.listingMode,
        row.summary, row.features, row.publishedDate, row.detailText
      ].map(normalizeText).join(" ").includes(q);
    }

    function governorateMetricCount(governorate, metric) {
      return records.filter(row =>
        row.governorate === governorate &&
        rowMatchesReferenceFilters(row, false, true) &&
        matchesMetric(row, metric)
      ).length;
    }

    const expandedGovernorates = new Set();

    function areaMetricCount(governorate, area, metric) {
      return records.filter(row =>
        row.governorate === governorate &&
        row.area === area &&
        rowMatchesReferenceFilters(row, false, true) &&
        matchesMetric(row, metric)
      ).length;
    }

    function governorateAreas(governorate) {
      const areaTotals = new Map();
      records.forEach(row => {
        if (row.governorate !== governorate) return;
        if (!rowMatchesReferenceFilters(row, false, true)) return;
        const area = row.area || "غير محدد";
        const total = areaTotals.get(area) || 0;
        areaTotals.set(area, total + (matchesMetric(row, "movement") ? 1 : 0));
      });
      return Array.from(areaTotals.entries())
        .filter(([, total]) => total > 0)
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "ar"));
    }

    function renderAreaBreakdownRow(governorate) {
      const detailRow = document.createElement("tr");
      detailRow.className = "area-detail-row";
      detailRow.dataset.governorate = governorate;
      const detailCell = document.createElement("td");
      detailCell.colSpan = comparisonMetrics.length + 1;

      const wrapper = document.createElement("div");
      wrapper.className = "area-breakdown";
      const title = document.createElement("div");
      title.className = "area-breakdown-title";
      const label = document.createElement("span");
      label.textContent = `تفصيل مناطق ${governorate}`;
      const hint = document.createElement("small");
      hint.textContent = "اضغط على أي رقم لاختيار المنطقة والمحور";
      title.append(label, hint);
      wrapper.appendChild(title);

      const grid = document.createElement("div");
      grid.className = "area-breakdown-grid";
      const areas = governorateAreas(governorate);
      if (!areas.length) {
        const empty = document.createElement("div");
        empty.className = "area-name";
        empty.textContent = "لا توجد مناطق مطابقة للفلاتر الحالية.";
        grid.appendChild(empty);
      } else {
        const labels = document.createElement("div");
        labels.className = "area-breakdown-labels";
        ["المنطقة", ...comparisonMetrics.map(metric => metricLabels[metric])].forEach(text => {
          const labelCell = document.createElement("span");
          labelCell.textContent = text;
          labels.appendChild(labelCell);
        });
        grid.appendChild(labels);
        const selectedAreaValue = document.getElementById("areaFilter").value;
        const activeMetric = state.metric || "movement";
        areas.forEach(([area]) => {
          const row = document.createElement("div");
          row.className = "area-breakdown-row";
          row.dataset.area = area;
          const activeMetricCount = areaMetricCount(governorate, area, activeMetric);
          const isSelectedArea = Boolean(selectedAreaValue && area === selectedAreaValue);
          row.classList.toggle("area-active", isSelectedArea);
          row.classList.toggle("metric-active-row", !selectedAreaValue && activeMetricCount > 0);
          const name = document.createElement("div");
          name.className = "area-name";
          name.textContent = area;
          row.appendChild(name);
          comparisonMetrics.forEach(metric => {
            const count = areaMetricCount(governorate, area, metric);
            const button = document.createElement("button");
            button.className = "area-count-button";
            button.type = "button";
            button.textContent = count ? formatNumber(count) : "-";
            button.disabled = !count;
            button.classList.toggle("empty-count", !count);
            const shouldHighlightMetric = metric === activeMetric && count > 0 && (!selectedAreaValue || isSelectedArea);
            button.classList.toggle("metric-active", shouldHighlightMetric);
            button.title = `${governorate} - ${area} - ${metricLabels[metric]}: ${formatNumber(count)}`;
            button.addEventListener("click", () => {
              applyFilter(metric, governorate);
              document.getElementById("areaFilter").value = area;
              expandedGovernorates.clear();
              expandedGovernorates.add(governorate);
              renderResults();
            });
            row.appendChild(button);
          });
          grid.appendChild(row);
        });
      }
      wrapper.appendChild(grid);
      detailCell.appendChild(wrapper);
      detailRow.appendChild(detailCell);
      return detailRow;
    }

    function renderProfessionalGovernorTable() {
      const tbody = document.querySelector("#govTable tbody");
      tbody.innerHTML = "";
      Object.values(governorateNameMap).forEach(governorate => {
        const counts = comparisonMetrics.map(metric => governorateMetricCount(governorate, metric));
        const tr = document.createElement("tr");
        tr.dataset.governorate = governorate;
        const nameCell = document.createElement("td");
        nameCell.className = "governor-name-cell";
        const nameWrap = document.createElement("div");
        nameWrap.className = "governor-name-wrap";
        const nameText = document.createElement("strong");
        nameText.className = "governor-name-text";
        nameText.textContent = governorate;
        const toggle = document.createElement("button");
        toggle.className = "governor-toggle";
        toggle.type = "button";
        toggle.setAttribute("aria-expanded", expandedGovernorates.has(governorate) ? "true" : "false");
        toggle.textContent = "المناطق";
        toggle.addEventListener("click", () => {
          if (expandedGovernorates.has(governorate)) {
            expandedGovernorates.delete(governorate);
          } else {
            expandedGovernorates.add(governorate);
          }
          renderProfessionalGovernorTable();
        });
        nameWrap.append(nameText, toggle);
        nameCell.appendChild(nameWrap);
        tr.appendChild(nameCell);
        comparisonMetrics.forEach((metric, index) => {
          const count = counts[index];
          const td = document.createElement("td");
          td.dataset.metric = metric;
          const button = document.createElement("button");
          button.className = "count-button";
          button.textContent = formatNumber(count);
          button.disabled = !count;
          button.title = `${governorate} - ${metricLabels[metric]}: ${formatNumber(count)}`;
          button.addEventListener("click", () => applyFilter(metric, governorate));
          td.appendChild(button);
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
        if (expandedGovernorates.has(governorate)) {
          tbody.appendChild(renderAreaBreakdownRow(governorate));
        }
      });
      highlightGovernorate();
      highlightMetricColumn();
    }

    function propertyCompatibility(offer, request) {
      const offerType = normalizeText(offer.property_type);
      const requestType = normalizeText(request.property_type);
      const offerText = matchingText(offer);
      const generic = value => !value || value === "عقارات" || value === "عقار";
      const propertyGroup = (value, text) => {
        if (/(?:للايجار|للبيع)\s+دور(?:\s|$)/.test(text) && !text.includes("شق")) return "floor";
        if (text.includes("عماره")) return "building";
        if (["فيلا", "بيت", "منزل", "قسيمه"].some(term => text.includes(term))) return "house";
        if (text.includes("شقه")) return "apartment";
        if (text.includes("ارض")) return "land";
        if (text.includes("شاليه")) return "chalet";
        if (generic(value)) return "any";
        if (["بيت", "فيلا", "قسيمه"].some(term => value.includes(term))) return "house";
        if (value.includes("شق")) return "apartment";
        if (value.includes("عماره")) return "building";
        if (value.includes("ارض")) return "land";
        if (value.includes("شاليه")) return "chalet";
        return value;
      };
      const requestText = matchingText(request);
      const offerGroup = propertyGroup(offerType, offerText);
      const requestGroup = propertyGroup(requestType, requestText);
      if (offerGroup === requestGroup && offerGroup !== "any" && offerType && offerType === requestType) {
        return { compatible: true, score: 25, reason: "نوع العقار متطابق" };
      }
      if (offerGroup === requestGroup && offerGroup !== "any") {
        return { compatible: true, score: 20, reason: "فئة العقار متوافقة" };
      }
      if (offerGroup === "any" || requestGroup === "any") {
        return { compatible: true, score: 10, reason: "نوع العقار عام ويحتاج تأكيد" };
      }
      return { compatible: false, score: 0, reason: "" };
    }

    function parsedAmount(numberText, hasThousandsUnit) {
      const value = Number(String(numberText || "").replace(/,/g, ""));
      if (!Number.isFinite(value) || value <= 0) return 0;
      return hasThousandsUnit && value < 10000 ? value * 1000 : value;
    }

    function extractRequestBudget(request) {
      const structured = Number(request.price);
      const text = normalizeDigitsForRules(matchingText(request)).replace(/،/g, ",");
      const rangeMatch = text.match(
        /(?:ميزانيه|ميزانية|بسعر|بحدود|حدود|يتراوح بين)[^0-9]{0,45}([\d,]+(?:\.\d+)?)\s*(الف)?\s*(?:الى|الي|-)\s*([\d,]+(?:\.\d+)?)\s*(الف)?/
      );
      if (rangeMatch) {
        const hasThousandsUnit = Boolean(rangeMatch[2] || rangeMatch[4]);
        const first = parsedAmount(rangeMatch[1], hasThousandsUnit);
        const second = parsedAmount(rangeMatch[3], hasThousandsUnit);
        if (first > 0 && second > 0) {
          const minimum = Math.min(first, second);
          const maximum = Math.max(first, second);
          return {
            value: maximum,
            min: minimum,
            max: maximum,
            derived: true,
            explicitRange: true
          };
        }
      }
      if (structured > 0) {
        return {
          value: structured,
          min: 0,
          max: structured,
          derived: false,
          explicitRange: false
        };
      }
      const match = text.match(
        /(?:حتى|حد اقصى|حد أقصى|ميزانيه|ميزانية|بسعر|بحدود|حدود)[^0-9]{0,45}([\d,]+(?:\.\d+)?)\s*(الف)?\s*(?:د\s*\.?\s*ك|دينار)?/
      );
      if (!match) return { value: 0, min: 0, max: 0, derived: false, explicitRange: false };
      const value = parsedAmount(match[1], Boolean(match[2]));
      return { value, min: 0, max: value, derived: true, explicitRange: false };
    }

    function extractOfferPrice(offer) {
      const structured = Number(offer.price);
      if (structured > 0) return { value: structured, derived: false };
      const text = normalizeDigitsForRules(matchingText(offer)).replace(/،/g, ",");
      const match = text.match(
        /(?:السعر|السوم|واصل|بياع)[^0-9]{0,28}([\d,]+(?:\.\d+)?)\s*(الف)?\s*(?:د\s*\.?\s*ك|دينار)/
      );
      if (!match) return { value: 0, derived: false };
      return { value: parsedAmount(match[1], Boolean(match[2])), derived: true };
    }

    function priceCompatibility(offer, request) {
      const offerAmount = extractOfferPrice(offer);
      const requestAmount = extractRequestBudget(request);
      const offerPrice = offerAmount.value;
      const budget = requestAmount.max || requestAmount.value;
      if (!(offerPrice > 0) || !(budget > 0)) {
        return {
          compatible: true,
          score: 5,
          reason: "السعر أو الميزانية يحتاج تأكيد",
          offerPrice,
          budget,
          offerDerived: offerAmount.derived,
          budgetDerived: requestAmount.derived
        };
      }
      const minimum = Number(requestAmount.min) || 0;
      if (minimum > 0 && offerPrice < minimum) {
        const shortfall = (minimum - offerPrice) / minimum;
        if (shortfall > .10) {
          return {
            compatible: false,
            score: 0,
            reason: "",
            offerPrice,
            budget,
            offerDerived: offerAmount.derived,
            budgetDerived: requestAmount.derived
          };
        }
        return {
          compatible: true,
          score: 10,
          reason: `السعر أقل من الحد الأدنى المطلوب بـ ${formatNumber(Math.round(shortfall * 100))}% ويحتاج تأكيد`,
          offerPrice,
          budget,
          offerDerived: offerAmount.derived,
          budgetDerived: requestAmount.derived
        };
      }
      const difference = (offerPrice - budget) / budget;
      if (difference <= 0) {
        return {
          compatible: true,
          score: 25,
          reason: requestAmount.explicitRange ? "السعر داخل النطاق المطلوب" : "السعر داخل الميزانية",
          offerPrice,
          budget,
          offerDerived: offerAmount.derived,
          budgetDerived: requestAmount.derived
        };
      }
      if (difference <= .05) {
        return {
          compatible: true,
          score: 18,
          reason: `السعر أعلى من الميزانية بـ ${formatNumber(Math.round(difference * 100))}%`,
          offerPrice,
          budget,
          offerDerived: offerAmount.derived,
          budgetDerived: requestAmount.derived
        };
      }
      if (difference <= .10) {
        return {
          compatible: true,
          score: 10,
          reason: `فارق السعر ${formatNumber(Math.round(difference * 100))}% ويحتاج تفاوض`,
          offerPrice,
          budget,
          offerDerived: offerAmount.derived,
          budgetDerived: requestAmount.derived
        };
      }
      return {
        compatible: false,
        score: 0,
        reason: "",
        offerPrice,
        budget,
        offerDerived: offerAmount.derived,
        budgetDerived: requestAmount.derived
      };
    }

    function recordQualityCompatibility(offer, request) {
      const age = Math.max(Number(offer.daysSince) || 999, Number(request.daysSince) || 999);
      const detailsAvailable = offer.detailAvailable === "نعم" && request.detailAvailable === "نعم";
      if (detailsAvailable && age <= 90) {
        return { score: 10, reason: "تفاصيل الطرفين متاحة وحديثة للمراجعة" };
      }
      if (detailsAvailable) {
        return { score: 7, reason: "التفاصيل متاحة ويلزم تأكيد استمرار الإعلانين" };
      }
      return { score: 4, reason: "بيانات أحد الطرفين تحتاج استكمالًا" };
    }

    function matchingText(row) {
      return normalizeText([row.summary, row.features, row.detailTitle, row.detailText].join(" "));
    }

    function conditionCompatibility(offer, request) {
      const offerText = matchingText(offer);
      const requestText = matchingText(request);
      const hasAny = (text, terms) => terms.some(term => text.includes(normalizeText(term)));
      const requestNeedsNew = hasAny(requestText, [
        "جديد", "ما انسكن", "لم يسكن", "غير مسكون", "اول ساكن", "أول ساكن"
      ]);
      const offerNeedsDemolition = hasAny(offerText, [
        "هدام", "للهدم", "بيت هدم", "قديم جدا", "قديم جدًا"
      ]);
      const offerIsNew = hasAny(offerText, ["جديد", "ما انسكن", "لم يسكن", "غير مسكون", "اول ساكن", "أول ساكن"]);
      if (requestNeedsNew && (offerNeedsDemolition || !offerIsNew)) return { compatible: false, reason: "" };
      const requestNeedsDemolition = hasAny(requestText, ["هدام", "للهدم", "بيت هدم"]);
      if (requestNeedsDemolition && !offerNeedsDemolition) return { compatible: false, reason: "" };
      return { compatible: true, reason: "" };
    }

    function locationCompatibility(offer, request) {
      const offerArea = normalizeText(offer.area);
      const requestArea = normalizeText(request.area);
      const requestText = matchingText(request);
      if (offerArea && offerArea === requestArea) {
        return { compatible: true, score: 40, reason: "المحافظة والمنطقة متطابقتان" };
      }
      if (offerArea && requestText.includes(offerArea)) {
        return { compatible: true, score: 40, reason: "منطقة العرض مذكورة ضمن بدائل الطلب" };
      }
      const broadRequest = [
        "اي منطقه", "اي منطقة", "جميع مناطق", "كل مناطق",
        "اي مكان", "او اي منطقه", "او اي منطقة"
      ].some(term => requestText.includes(normalizeText(term)));
      if (broadRequest) {
        return { compatible: true, score: 30, reason: "الطلب يقبل أي منطقة داخل المحافظة" };
      }
      return { compatible: false, score: 0, reason: "" };
    }

    function normalizeDigitsForRules(value) {
      return String(value || "")
        .replace(/[٠-٩]/g, digit => "٠١٢٣٤٥٦٧٨٩".indexOf(digit))
        .replace(/[۰-۹]/g, digit => "۰۱۲۳۴۵۶۷۸۹".indexOf(digit));
    }

    function buildingUnitRangeIsCompatible(offer, request) {
      const requestText = normalizeDigitsForRules(matchingText(request));
      const offerText = normalizeDigitsForRules(matchingText(offer));
      const requestedRange = requestText.match(/(\d+)\s*(?:الى|الي|-)\s*(\d+)\s*شق/);
      if (!requestedRange) return true;
      const offeredUnits = [...offerText.matchAll(/(\d+)\s*شق/g)]
        .map(match => Number(match[1]))
        .filter(Number.isFinite);
      if (!offeredUnits.length) return true;
      const minimum = Number(requestedRange[1]);
      const maximum = Number(requestedRange[2]);
      return offeredUnits.some(units => units >= minimum && units <= maximum);
    }

    function extractSpaceValues(row) {
      const values = [];
      const structured = Number(row.space);
      if (structured >= 50 && structured <= 10000) values.push(structured);
      const text = normalizeDigitsForRules(matchingText(row));
      for (const match of text.matchAll(/(\d{2,4})\s*(?:م(?:2|²)?|متر(?:\s+مربع)?)/g)) {
        const value = Number(match[1]);
        if (value >= 50 && value <= 10000) values.push(value);
      }
      return [...new Set(values)];
    }

    function extractFloorRange(row) {
      const text = normalizeDigitsForRules(matchingText(row));
      const range = text.match(/(\d+(?:\.\d+)?)\s*(?:او|الى|الي|-)\s*(\d+(?:\.\d+)?)\s*(?:دور|ادوار)/);
      if (range) {
        const first = Number(range[1]);
        const second = Number(range[2]);
        return { min: Math.min(first, second), max: Math.max(first, second) };
      }
      const exact = text.match(/(\d+(?:\.\d+)?)\s*(?:دور|ادوار)/);
      if (exact) {
        const value = Number(exact[1]);
        return { min: value, max: value };
      }
      if (text.includes("دورين ونصف")) return { min: 2.5, max: 2.5 };
      if (text.includes("دورين")) return { min: 2, max: 2 };
      if (text.includes("دور ونصف")) return { min: 1.5, max: 1.5 };
      if (/ثلاث(?:ه)?\s+ادوار/.test(text)) return { min: 3, max: 3 };
      if (/(?:اربع|اربعه)\s+ادوار/.test(text)) return { min: 4, max: 4 };
      return null;
    }

    function requestedSiteFeature(row) {
      const text = normalizeText([row.summary, row.detailTitle, row.detailText].join(" "));
      const corner = ["زاويه", "زاوية", "زويه", "زوية"].some(term => text.includes(normalizeText(term)));
      const frontBack = ["بطن وظهر", "يطن وظهر"].some(term => text.includes(normalizeText(term)));
      return { required: corner || frontBack, corner, frontBack };
    }

    function offeredSiteFeature(row) {
      const text = normalizeText([row.summary, row.detailTitle, row.detailText].join(" "))
        .replace(/اخو\s+(?:زاويه|زاوية|زويه|زوية)/g, "");
      return {
        corner: ["زاويه", "زاوية", "زويه", "زوية", "شارعين"].some(term => text.includes(normalizeText(term))),
        frontBack: ["بطن وظهر", "يطن وظهر"].some(term => text.includes(normalizeText(term)))
      };
    }

    function extractBlocks(row) {
      const text = normalizeDigitsForRules(matchingText(row));
      return [...new Set([...text.matchAll(/(?:قطعه|قطعة)\s*[:\-]?\s*(\d{1,2})/g)].map(match => Number(match[1])))];
    }

    function requirementCompatibility(offer, request) {
      const reasons = [];
      let adjustment = 0;
      const requestedSpaces = extractSpaceValues(request);
      const offeredSpaces = extractSpaceValues(offer);
      if (requestedSpaces.length) {
        if (offeredSpaces.length) {
          const spaceMatches = requestedSpaces.some(required =>
            offeredSpaces.some(available => Math.abs(available - required) / required <= .05)
          );
          if (!spaceMatches) return { compatible: false, adjustment: 0, reasons: [] };
          reasons.push("المساحة توافق الطلب");
        } else {
          adjustment -= 5;
          reasons.push("مساحة العرض غير مذكورة وتحتاج تأكيد");
        }
      }

      const requestedFloors = extractFloorRange(request);
      const offeredFloors = extractFloorRange(offer);
      if (requestedFloors) {
        if (offeredFloors) {
          const overlaps = offeredFloors.max >= requestedFloors.min && offeredFloors.min <= requestedFloors.max;
          if (!overlaps) return { compatible: false, adjustment: 0, reasons: [] };
          reasons.push("عدد الأدوار يوافق الطلب");
        } else {
          adjustment -= 5;
          reasons.push("عدد أدوار العرض غير مذكور ويحتاج تأكيد");
        }
      }

      const requestedFeature = requestedSiteFeature(request);
      if (requestedFeature.required) {
        const offeredFeature = offeredSiteFeature(offer);
        const featureMatches =
          (requestedFeature.corner && offeredFeature.corner) ||
          (requestedFeature.frontBack && offeredFeature.frontBack);
        if (!featureMatches) return { compatible: false, adjustment: 0, reasons: [] };
        reasons.push("موقع العقار يوافق الشرط المطلوب");
      }

      const requestedBlocks = extractBlocks(request);
      if (requestedBlocks.length) {
        const offeredBlocks = extractBlocks(offer);
        if (offeredBlocks.length) {
          if (!offeredBlocks.some(block => requestedBlocks.includes(block))) {
            return { compatible: false, adjustment: 0, reasons: [] };
          }
          reasons.push("رقم القطعة ضمن القطع المطلوبة");
        } else {
          adjustment -= 10;
          reasons.push("رقم قطعة العرض غير مذكور ويحتاج تأكيد");
        }
      }
      return { compatible: true, adjustment, reasons };
    }

    function matchOpportunity(offer, request, sector) {
      if (!offer.governorate || offer.governorate !== request.governorate) return null;
      if (["AF-3"].includes(offer.code) || ["AF-3"].includes(request.code)) return null;
      const property = propertyCompatibility(offer, request);
      if (!property.compatible) return null;
      const condition = conditionCompatibility(offer, request);
      if (!condition.compatible) return null;
      const location = locationCompatibility(offer, request);
      if (!location.compatible) return null;
      if (!buildingUnitRangeIsCompatible(offer, request)) return null;
      const requirements = requirementCompatibility(offer, request);
      if (!requirements.compatible) return null;
      const price = priceCompatibility(offer, request);
      if (!price.compatible) return null;
      const quality = recordQualityCompatibility(offer, request);
      const score = Math.min(100, location.score + property.score + price.score + quality.score + requirements.adjustment);
      if (score < 55) return null;
      return {
        sector,
        offer,
        request,
        score,
        offerPrice: price.offerPrice,
        budget: price.budget,
        offerPriceDerived: price.offerDerived,
        budgetDerived: price.budgetDerived,
        reasons: [location.reason, property.reason, ...requirements.reasons, price.reason, quality.reason].filter(Boolean)
      };
    }

    function computeMatches(sector = activeMatchSector) {
      const config = sector === "rent"
        ? { offer: "للإيجار", request: "مطلوب للإيجار" }
        : { offer: "للبيع", request: "مطلوب للشراء" };
      const scopeRows = records.filter(row => rowMatchesSharedFilters(row, true, false));
      const offers = scopeRows.filter(row => row.transaction === config.offer);
      const requests = scopeRows.filter(row => row.transaction === config.request);
      const matches = [];
      requests.forEach(request => {
        offers.forEach(offer => {
          const match = matchOpportunity(offer, request, sector);
          if (match) matches.push(match);
        });
      });
      matches.sort((a, b) =>
        b.score - a.score ||
        Number(a.offer.daysSince) - Number(b.offer.daysSince) ||
        a.offer.code.localeCompare(b.offer.code, "en")
      );
      return { offers, requests, matches };
    }

    function createMatchSide(label, row, match, isRequest = false) {
      const side = document.createElement("div");
      side.className = "match-side";
      const sideLabel = document.createElement("b");
      sideLabel.textContent = label;
      const code = document.createElement("strong");
      code.textContent = `${row.code} · ${row.area || "منطقة غير محددة"}`;
      const property = document.createElement("span");
      const matchedAmount = isRequest ? match.budget : match.offerPrice;
      const derived = isRequest ? match.budgetDerived : match.offerPriceDerived;
      const amountLabel = matchedAmount
        ? `${isRequest ? "ميزانية حتى " : ""}${formatNumber(matchedAmount)} د.ك${derived ? " (من التفاصيل)" : ""}`
        : (row.priceText || "سعر غير معلن");
      property.textContent = `${row.property_type || "نوع غير محدد"} · ${amountLabel}`;
      side.append(sideLabel, code, property);
      return side;
    }

    function appendMatchAction(container, label, handler) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.addEventListener("click", handler);
      container.appendChild(button);
    }

    function appendOriginalMatchLink(container, row) {
      if (!row.originalAvailable || !row.originalUrl) return;
      const link = document.createElement("a");
      link.href = row.originalUrl;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = `فتح الأصلية ${row.code}`;
      container.appendChild(link);
    }

    function resolveTypedArea(value) {
      const typed = normalizeText(value);
      if (!typed) return null;
      const areas = Object.keys(areaGovernorateMap);
      const exact = areas.find(area => normalizeText(area) === typed);
      if (exact) return { area: exact, governorate: areaGovernorateMap[exact] };
      if (typed.length < 2) return null;
      const partial = areas.filter(area => normalizeText(area).includes(typed));
      if (partial.length !== 1) return null;
      return { area: partial[0], governorate: areaGovernorateMap[partial[0]] };
    }

    function syncAreaGovernorateExpansion() {
      const areaInput = document.getElementById("areaFilter");
      const governorateInput = document.getElementById("governorateFilter");
      if (!areaInput || !governorateInput) return null;
      const resolved = resolveTypedArea(areaInput.value);
      if (!resolved) return null;
      areaInput.value = resolved.area;
      state.governorate = "";
      governorateInput.value = resolved.governorate;
      expandedGovernorates.clear();
      expandedGovernorates.add(resolved.governorate);
      return resolved;
    }

    const basePreviewRenderSuggestions = renderSuggestions;
    renderSuggestions = function(id) {
      const input = document.getElementById(id);
      const box = document.getElementById(`${id}Suggest`);
      if (!input || !box) return;
      const typed = normalizeText(input.value);
      const exactChoice = (choiceOptions[id] || []).some(option => normalizeText(option) === typed);
      if (typed && exactChoice) {
        box.innerHTML = "";
        box.classList.remove("show");
        return;
      }
      basePreviewRenderSuggestions(id);
    };

    const basePreviewChooseSuggestion = chooseSuggestion;
    chooseSuggestion = function(id, value) {
      basePreviewChooseSuggestion(id, value);
      hideSuggestions(id);
      const input = document.getElementById(id);
      if (input) input.blur();
    };

    const basePreviewHandleFilterChange = handleFilterChange;
    handleFilterChange = function(id) {
      if (id === "areaFilter") {
        const areaInput = document.getElementById("areaFilter");
        const hasTypedArea = Boolean(areaInput && areaInput.value.trim());
        const resolvedBeforeBase = syncAreaGovernorateExpansion();
        if (hasTypedArea && !resolvedBeforeBase) {
          renderResults();
          return;
        }
      }
      basePreviewHandleFilterChange(id);
      if (id === "areaFilter") {
        syncAreaGovernorateExpansion();
      } else if (id === "governorateFilter") {
        expandedGovernorates.clear();
        const governorate = selectedGovernorate();
        if (governorate) expandedGovernorates.add(governorate);
      }
      renderResults();
    };

    function groupMatchesByRequest(matches) {
      const grouped = new Map();
      matches.forEach(match => {
        if (!grouped.has(match.request.code)) {
          grouped.set(match.request.code, { request: match.request, matches: [] });
        }
        grouped.get(match.request.code).matches.push(match);
      });
      return [...grouped.values()]
        .map(group => {
          group.matches.sort((a, b) =>
            b.score - a.score ||
            Number(a.offer.daysSince) - Number(b.offer.daysSince) ||
            a.offer.code.localeCompare(b.offer.code, "en")
          );
          group.bestScore = group.matches[0]?.score || 0;
          return group;
        })
        .sort((a, b) =>
          b.bestScore - a.bestScore ||
          b.matches.length - a.matches.length ||
          a.request.code.localeCompare(b.request.code, "en")
        );
    }

    function renderMatches() {
      const { offers, requests, matches } = computeMatches(activeMatchSector);
      const matchGroups = groupMatchesByRequest(matches);
      const scopeKey = JSON.stringify([
        activeMatchSector,
        selectedGovernorate(),
        document.getElementById("propertyFilter").value,
        document.getElementById("areaFilter").value,
        document.getElementById("listingModeFilter").value,
        document.getElementById("priceFilter").value,
        document.getElementById("searchBox").value
      ]);
      if (scopeKey !== lastMatchScopeKey) {
        visibleMatchLimit = 10;
        lastMatchScopeKey = scopeKey;
      }
      document.querySelectorAll(".match-sector").forEach(button => {
        button.classList.toggle("active", button.dataset.sector === activeMatchSector);
      });
      const multiOfferRequests = matchGroups.filter(group => group.matches.length > 1).length;
      const summary = [
        ["طلبات لها عروض متوافقة", matchGroups.length],
        ["إجمالي العروض المتوافقة", matches.length],
        ["طلبات متعددة البدائل", multiOfferRequests]
      ];
      document.getElementById("matchDisclosureCount").textContent =
        `${formatNumber(matchGroups.length)} طلبات · ${formatNumber(matches.length)} عروض`;
      const summaryContainer = document.getElementById("matchSummary");
      summaryContainer.innerHTML = "";
      summary.forEach(([label, value]) => {
        const box = document.createElement("div");
        const labelNode = document.createElement("span");
        labelNode.textContent = label;
        const valueNode = document.createElement("strong");
        valueNode.textContent = formatNumber(value);
        box.append(labelNode, valueNode);
        summaryContainer.appendChild(box);
      });

      const container = document.getElementById("matchList");
      const loadMore = document.getElementById("matchLoadMore");
      container.innerHTML = "";
      if (!matches.length) {
        loadMore.hidden = true;
        const empty = document.createElement("div");
        empty.className = "match-empty";
        empty.textContent = requests.length
          ? "لا توجد مطابقة قوية وفق الاختيارات الحالية. راجع المنطقة أو نوع العقار أو السعر."
          : "لا توجد طلبات ضمن الاختيارات الحالية لبدء التوفيق.";
        container.appendChild(empty);
        return;
      }
      matchGroups.slice(0, visibleMatchLimit).forEach(group => {
        const primaryMatch = group.matches[0];
        const card = document.createElement("article");
        card.className = "match-card match-group-card";
        card.classList.toggle("has-multiple-offers", group.matches.length > 1);
        card.dataset.requestCode = group.request.code;
        card.dataset.offerCount = String(group.matches.length);
        const head = document.createElement("div");
        head.className = "match-card-head";
        const title = document.createElement("strong");
        title.textContent = `الطلب ${group.request.code} · ${group.request.area || "منطقة غير محددة"}`;
        const groupCount = document.createElement("span");
        groupCount.className = "match-group-count";
        groupCount.classList.toggle("multiple", group.matches.length > 1);
        groupCount.textContent = group.matches.length === 1
          ? "عرض واحد متوافق"
          : `${formatNumber(group.matches.length)} بدائل متوافقة`;
        head.append(title, groupCount);

        const requestOverview = document.createElement("div");
        requestOverview.className = "match-request-overview";
        requestOverview.appendChild(createMatchSide("بيانات الطلب", group.request, primaryMatch, true));
        const requestActions = document.createElement("div");
        requestActions.className = "match-request-actions";
        appendMatchAction(requestActions, `عرض تفاصيل الطلب ${group.request.code}`, () => openDetailsModal(group.request.code));
        appendOriginalMatchLink(requestActions, group.request);
        requestOverview.appendChild(requestActions);

        const offerList = document.createElement("div");
        offerList.className = "match-offers";
        let alternativesHeading = null;
        if (group.matches.length > 1) {
          alternativesHeading = document.createElement("div");
          alternativesHeading.className = "match-alternatives-heading";
          alternativesHeading.textContent = "البدائل مرتبة من الأعلى إلى الأقل توافقًا";
        }
        group.matches.forEach((match, offerIndex) => {
          const option = document.createElement("section");
          option.className = "match-offer-option";
          option.classList.toggle("best-option", group.matches.length > 1 && offerIndex === 0);
          option.dataset.offerCode = match.offer.code;
          const optionHead = document.createElement("div");
          optionHead.className = "match-offer-head";
          const optionTitle = document.createElement("strong");
          optionTitle.textContent = group.matches.length > 1 && offerIndex === 0
            ? `أفضل تطابق · ${match.offer.code}`
            : group.matches.length > 1
              ? `البديل ${formatNumber(offerIndex + 1)} · ${match.offer.code}`
              : `العرض ${match.offer.code}`;
          const score = document.createElement("span");
          score.className = `match-score ${match.score >= 85 ? "strong" : match.score >= 70 ? "potential" : "review"}`;
          score.textContent = `تطابق ${formatNumber(match.score)}%`;
          optionHead.append(optionTitle, score);

          const offerSide = createMatchSide("العرض المقترح", match.offer, match, false);
          const reasons = document.createElement("div");
          reasons.className = "match-reasons";
          match.reasons.forEach(reason => {
            const chip = document.createElement("span");
            chip.className = "match-reason";
            chip.textContent = reason;
            reasons.appendChild(chip);
          });
          const actions = document.createElement("div");
          actions.className = "match-actions";
          appendMatchAction(actions, `عرض تفاصيل ${match.offer.code}`, () => openDetailsModal(match.offer.code));
          appendOriginalMatchLink(actions, match.offer);
          option.append(optionHead, offerSide, reasons, actions);
          offerList.appendChild(option);
        });
        card.append(head, requestOverview);
        if (alternativesHeading) card.appendChild(alternativesHeading);
        card.appendChild(offerList);
        container.appendChild(card);
      });
      loadMore.hidden = visibleMatchLimit >= matchGroups.length;
      loadMore.textContent = `عرض المزيد من الطلبات (${formatNumber(matchGroups.length - Math.min(visibleMatchLimit, matchGroups.length))})`;
      summaryContainer.title =
        `${formatNumber(offers.length)} عرضًا و${formatNumber(requests.length)} طلبًا ضمن الاختيارات الحالية`;
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    function printableDetail(row) {
      return row.detailText || row.summary || row.features || "لا توجد تفاصيل نصية مسجلة.";
    }

    function selectedFiltersForPrint() {
      return [
        ["المحور", metricLabels[state.metric] || state.label || "كل السجلات"],
        ["المحافظة", selectedGovernorate() || "كل المحافظات"],
        ["المنطقة", document.getElementById("areaFilter").value || "كل المناطق"],
        ["نوع المعاملة", document.getElementById("transactionFilter").value || "كل المعاملات"],
        ["نوع العقار", document.getElementById("propertyFilter").value || "كل أنواع العقار"],
        ["نمط الإدراج", document.getElementById("listingModeFilter").value || "كل الأنماط"],
        ["حالة السعر", document.getElementById("priceFilter").selectedOptions[0]?.textContent || "كل الأسعار"],
        ["البحث", document.getElementById("searchBox").value || "بدون بحث نصي"]
      ];
    }

    function printFilterSummary() {
      return `<div class="print-filters">${
        selectedFiltersForPrint().map(([label, value]) =>
          `<span><b>${escapeHtml(label)}</b>${escapeHtml(value)}</span>`
        ).join("")
      }</div>`;
    }

    function printListingCards(rows) {
      return rows.map(row => `
        <article class="listing-print-card">
          <div class="listing-print-head">
            <h3>${escapeHtml(row.code)} - ${escapeHtml(row.area || "منطقة غير محددة")}</h3>
            <span>${escapeHtml(row.transaction || "غير محدد")}</span>
          </div>
          <div class="listing-print-facts">
            <span><b>المحافظة</b>${escapeHtml(row.governorate || "غير محدد")}</span>
            <span><b>نوع العقار</b>${escapeHtml(row.property_type || "غير محدد")}</span>
            <span><b>التصنيف</b>${escapeHtml(row.detail_class || "غير محدد")}</span>
            <span><b>السعر</b>${escapeHtml(row.priceText || "غير معلن")}</span>
            <span><b>المساحة</b>${escapeHtml(row.space ? `${formatNumber(row.space)} م²` : "غير محدد")}</span>
            <span><b>نمط الإدراج</b>${escapeHtml(listingModeLabels[listingModeGroup(row.listingMode)])}</span>
            <span><b>تاريخ النشر</b>${escapeHtml(row.publishedDate || "غير محدد")}</span>
            <span><b>رابط الإعلان</b>${escapeHtml(row.originalUrl || "غير متاح")}</span>
          </div>
          <div class="listing-print-details">
            <b>تفاصيل الإعلان</b>
            <p>${escapeHtml(printableDetail(row))}</p>
          </div>
        </article>`).join("");
    }

    function printRowsTable(title, rows) {
      const body = rows.map(row => `
        <tr>
          <td>${escapeHtml(row.code)}</td>
          <td>${escapeHtml(row.governorate)}</td>
          <td>${escapeHtml(row.area)}</td>
          <td>${escapeHtml(row.property_type)}</td>
          <td>${escapeHtml(row.priceText || "غير معلن")}</td>
          <td>${escapeHtml(row.publishedDate || "غير محدد")}</td>
          <td>${escapeHtml(listingModeLabels[listingModeGroup(row.listingMode)])}</td>
          <td class="detail-cell">${escapeHtml(printableDetail(row))}</td>
        </tr>`).join("");
      return `
        <section>
          <h2>${escapeHtml(title)} <small>(${formatNumber(rows.length)})</small></h2>
          <table>
            <thead><tr><th>الكود</th><th>المحافظة</th><th>المنطقة</th><th>نوع العقار</th><th>السعر</th><th>التاريخ</th><th>النمط</th><th>تفاصيل الإعلان</th></tr></thead>
            <tbody>${body || '<tr><td colspan="8">لا توجد سجلات مطابقة.</td></tr>'}</tbody>
          </table>
        </section>`;
    }

    function printCurrentFilteredReport() {
      const rows = currentRows();
      const printWindow = window.open("", "_blank");
      if (!printWindow) {
        window.alert("اسمح بالنوافذ المنبثقة حتى تتمكن من طباعة التقرير.");
        return;
      }
      printWindow.document.write(`<!doctype html>
        <html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>تقرير الإعلانات المطابقة</title>
        <style>
          body{font-family:Tahoma,Arial,sans-serif;color:#071426;margin:22px;direction:rtl;background:#fff}
          header{border-bottom:4px solid #bd5700;padding-bottom:12px;margin-bottom:16px}
          h1{margin:0;font-size:24px} h2{margin:18px 0 8px;font-size:18px}
          .print-filters{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:12px 0}
          .print-filters span,.listing-print-facts span{border:1px solid #b9c8db;background:#f7faff;padding:7px;border-radius:5px;font-size:11px}
          .print-filters b,.listing-print-facts b{display:block;color:#304158;font-size:10px;margin-bottom:3px}
          .listing-print-card{break-inside:avoid;border:1px solid #aebfd4;border-radius:7px;margin:0 0 10px;background:#fff}
          .listing-print-head{display:flex;justify-content:space-between;gap:10px;background:#0f1a2d;color:#fff;padding:9px 11px}
          .listing-print-head h3{margin:0;font-size:16px}.listing-print-head span{font-weight:900}
          .listing-print-facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;padding:9px}
          .listing-print-details{padding:0 10px 10px}.listing-print-details b{display:block;margin-bottom:4px;color:#0f1a2d}
          .listing-print-details p{white-space:pre-wrap;margin:0;border-right:3px solid #2554d9;background:#f8fbff;padding:8px;line-height:1.65;font-size:11px}
          @page{size:A4 landscape;margin:10mm}
        </style></head><body>
        <header><h1>تقرير الإعلانات المطابقة</h1><p>عدد الإعلانات: ${formatNumber(rows.length)}</p>${printFilterSummary()}</header>
        ${rows.length ? printListingCards(rows) : "<p>لا توجد إعلانات مطابقة للاختيارات الحالية.</p>"}
        <script>window.onload=()=>window.print();<\/script></body></html>`);
      printWindow.document.close();
    }

    function printSectorReport(sector) {
      const config = sector === "rent"
        ? { title: "عروض الإيجار وطلبات الإيجار", offer: "للإيجار", request: "مطلوب للإيجار" }
        : { title: "عروض البيع وطلبات الشراء", offer: "للبيع", request: "مطلوب للشراء" };
      const scopeRows = records.filter(row => rowMatchesSharedFilters(row, true, false));
      const offers = scopeRows.filter(row => row.transaction === config.offer);
      const requests = scopeRows.filter(row => row.transaction === config.request);
      const matches = computeMatches(sector).matches;
      const matchRows = matches.slice(0, 50).map(match => `
        <tr>
          <td>${escapeHtml(match.request.code)}</td>
          <td>${escapeHtml(match.offer.code)}</td>
          <td>${formatNumber(match.score)}%</td>
          <td>${escapeHtml(match.reasons.join("، "))}</td>
        </tr>`).join("");
      const printWindow = window.open("", "_blank");
      if (!printWindow) {
        window.alert("اسمح بالنوافذ المنبثقة حتى تتمكن من طباعة التقرير.");
        return;
      }
      printWindow.document.write(`<!doctype html>
        <html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>${escapeHtml(config.title)}</title>
        <style>
          body{font-family:Tahoma,Arial,sans-serif;color:#071426;margin:24px;direction:rtl}
          header{border-bottom:4px solid #bd5700;padding-bottom:12px;margin-bottom:20px}
          h1{margin:0;font-size:24px} h2{margin:24px 0 8px;font-size:19px}
          small{color:#304158} table{width:100%;border-collapse:collapse;font-size:11px}
          th{background:#0f1a2d;color:#fff} th,td{border:1px solid #aebfd4;padding:6px;text-align:right}
          .detail-cell{white-space:pre-wrap;line-height:1.55;min-width:280px}
          section{break-inside:avoid;margin-bottom:18px}
          @page{size:A4 landscape;margin:12mm}
        </style></head><body>
        <header><h1>${escapeHtml(config.title)}</h1><p>تقرير تشغيلي وفق اختيارات الفلاتر الحالية.</p></header>
        ${printRowsTable(config.offer, offers)}
        ${printRowsTable(config.request, requests)}
        <section><h2>العروض والطلبات المطابقة <small>(${formatNumber(matches.length)})</small></h2>
          <table><thead><tr><th>كود الطلب</th><th>كود العرض</th><th>درجة التطابق</th><th>أسباب المطابقة</th></tr></thead>
          <tbody>${matchRows || '<tr><td colspan="4">لا توجد فرص مطابقة وفق الاختيارات الحالية.</td></tr>'}</tbody></table>
        </section>
        <script>window.onload=()=>window.print();<\/script></body></html>`);
      printWindow.document.close();
    }

    function toEnglishDigits(value) {
      return String(value)
        .replace(/[\u0660-\u0669]/g, digit => String(digit.charCodeAt(0) - 0x0660))
        .replace(/[\u06F0-\u06F9]/g, digit => String(digit.charCodeAt(0) - 0x06F0));
    }

    function convertVisibleDigits(root = document.body) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        const parent = node.parentElement;
        if (!parent || ["SCRIPT", "STYLE"].includes(parent.tagName)) return;
        const converted = toEnglishDigits(node.nodeValue);
        if (converted !== node.nodeValue) node.nodeValue = converted;
      });
    }

    renderResultStats = function(rows) {
      const priced = rows.filter(row => Number.isFinite(Number(row.price)) && Number(row.price) > 0);
      const directModes = rows.filter(row => listingModeGroup(row.listingMode) === "direct").length;
      const officeModes = rows.filter(row => listingModeGroup(row.listingMode) === "office").length;
      const mixedModes = rows.filter(row => listingModeGroup(row.listingMode) === "both").length;
      const knownModes = directModes + officeModes + mixedModes;
      const stats = [
        ["النتائج المطابقة", `${formatNumber(rows.length)} إعلانًا`],
        ["إعلانات بسعر واضح", `${formatNumber(priced.length)} إعلانًا`],
        ["طريقة النشر محددة", `${formatNumber(knownModes)} إعلانًا: ${formatNumber(directModes)} مباشر، ${formatNumber(officeModes)} مكتب، ${formatNumber(mixedModes)} يجمعهما`]
      ];
      const container = document.getElementById("resultStats");
      container.innerHTML = "";
      stats.forEach(([label, value]) => {
        const box = document.createElement("div");
        const labelNode = document.createElement("b");
        labelNode.textContent = label;
        const valueNode = document.createElement("span");
        valueNode.textContent = value;
        box.append(labelNode, valueNode);
        container.appendChild(box);
      });
      const evidence = document.getElementById("resultEvidence");
      if (evidence) {
        evidence.textContent = "الأرقام أعلاه تخص الإعلانات المطابقة للاختيارات الحالية.";
      }
    };

    const basePreviewRenderResults = renderResults;
    renderResults = function() {
      basePreviewRenderResults();
      renderProfessionalMetrics();
      renderProfessionalGovernorTable();
      const showAll = document.getElementById("showAllButton");
      if (showAll) {
        showAll.hidden = document.querySelectorAll("#resultList .item").length >= currentRows().length;
      }
      convertVisibleDigits();
    };

    initializeDashboardTabs();

    const originalPrintButton = document.getElementById("printPdfButton");
    if (originalPrintButton) {
      const printButton = originalPrintButton.cloneNode(true);
      originalPrintButton.replaceWith(printButton);
      printButton.addEventListener("click", printCurrentFilteredReport);
    }
    document.getElementById("searchBox").addEventListener("input", () => renderResults());
    document.getElementById("priceFilter").addEventListener("change", () => renderResults());
    document.getElementById("showAllButton").addEventListener("click", () => {
      visibleResultLimit = currentRows().length;
      renderResults();
    });
    renderResultStats(currentRows());
    renderProfessionalMetrics();
    renderProfessionalGovernorTable();
    convertVisibleDigits();
    const digitObserver = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) {
            node.nodeValue = toEnglishDigits(node.nodeValue);
          } else if (node.nodeType === Node.ELEMENT_NODE && !["SCRIPT", "STYLE"].includes(node.tagName)) {
            convertVisibleDigits(node);
          }
        });
      });
    });
    digitObserver.observe(document.body, { childList: true, subtree: true });
  </script>
"""


def build_preview() -> Path:
    if not SOURCE_SITE.exists():
        raise FileNotFoundError(f"Missing source site: {SOURCE_SITE}")

    if PREVIEW_SITE.exists():
        shutil.rmtree(PREVIEW_SITE)
    shutil.copytree(SOURCE_SITE, PREVIEW_SITE)

    logo = Image.open(ASSETS / "alforaij_logo.png").convert("RGBA")
    symbol = logo.crop((350, 0, logo.width, logo.height))
    alpha_bounds = symbol.getchannel("A").getbbox()
    if alpha_bounds:
        symbol = symbol.crop(alpha_bounds)
    side = max(symbol.width, symbol.height)
    icon = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    icon.alpha_composite(symbol, ((side - symbol.width) // 2, (side - symbol.height) // 2))
    icon = icon.resize((512, 512), Image.Resampling.LANCZOS)
    icon.save(PREVIEW_SITE / "assets" / "alforaij-official-symbol.png", optimize=True)

    html_path = PREVIEW_SITE / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(
        r"\n?\s*<style id=\"professional-preview-v2\">.*?</style>",
        "",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"\n?\s*<script id=\"professional-preview-v2-script\">.*?</script>",
        "",
        html,
        flags=re.S,
    )
    html = html.replace(
        "<title>استعراض الأرقام والعروض الفعلية</title>",
        "<meta http-equiv=\"Cache-Control\" content=\"no-store, no-cache, must-revalidate, max-age=0\">\n  <meta http-equiv=\"Pragma\" content=\"no-cache\">\n  <meta http-equiv=\"Expires\" content=\"0\">\n  <title>لوحة الفريج العقارية | الأرقام والعروض</title>",
    )
    html = html.replace(
        'href="assets/alforaij-favicon-32.png"',
        'href="assets/alforaij-official-symbol.png"',
    )
    html = html.replace(
        'href="assets/alforaij-favicon-v2.png"',
        'href="assets/alforaij-official-symbol.png"',
    )
    html = html.replace(
        "new Intl.NumberFormat('ar-KW')",
        "new Intl.NumberFormat('en-US')",
    )
    html = html.replace("const RESULT_PAGE_SIZE = 24;", "const RESULT_PAGE_SIZE = 7;")
    html = html.replace(
        "meta.textContent = `تاريخ النشر: ${row.publishedDate || 'غير محدد'} | تفاصيل متاحة: ${row.detailAvailable} | صورة: ${row.imageUrl ? 'نعم' : 'لا'}`;",
        "meta.textContent = `تاريخ النشر: ${row.publishedDate || 'غير محدد'}`;",
    )
    html = html.replace("فتح صفحة الإعلان الأصلية", "فتح الإعلان الأصلي")
    html = html.replace("٪", "%")
    html = html.replace(
        '<button id="loadMoreButton" class="load-more" type="button">عرض المزيد</button>',
        '<button id="loadMoreButton" class="load-more" type="button">عرض المزيد</button>\n'
        '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>',
    )
    html = html.replace(
        '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>\n'
        '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>',
        '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>',
    )
    while html.count('id="showAllButton"') > 1:
        html = html.replace(
            '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>\n'
            '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>',
            '          <button id="showAllButton" class="load-more load-all" type="button">عرض الكل</button>',
        )
    html = html.replace("</head>", PREVIEW_CSS + "\n</head>", 1)
    preview_js = PREVIEW_JS
    preview_js = preview_js.replace("٪", "%")
    before_body, sep, after_body = html.rpartition("</body>")
    if not sep:
        raise ValueError("Missing closing body tag in dashboard HTML")
    html = before_body + preview_js + "\n</body>" + after_body
    html_path.write_text(html, encoding="utf-8")
    return html_path


def main() -> None:
    output = build_preview()
    print(
        json.dumps(
            {
                "preview": str(output),
                "published": False,
                "source_records": "site/index.html",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()





