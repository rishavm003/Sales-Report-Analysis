// ── Utility ───────────────────────────────────────────────
function formatNumber(value) {
    return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value || 0);
}

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast-msg${type === "error" ? " error" : ""}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ── Loading bar ───────────────────────────────────────────
const loadingBar = document.getElementById("loadingBar");
function startLoading() {
    loadingBar.classList.remove("done");
    loadingBar.classList.add("loading");
}
function stopLoading() {
    loadingBar.classList.remove("loading");
    loadingBar.classList.add("done");
    setTimeout(() => loadingBar.classList.remove("done"), 700);
}

// ── Dark mode toggle ──────────────────────────────────────
const html = document.documentElement;
const toggle = document.getElementById("darkModeToggle");
const saved = localStorage.getItem("theme") || "light";
html.setAttribute("data-theme", saved);
toggle.textContent = saved === "dark" ? "☀️" : "🌙";

toggle.addEventListener("click", () => {
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    toggle.textContent = next === "dark" ? "☀️" : "🌙";
    // Re-theme Plotly charts on next refresh
    refreshDashboard();
});

// ── Plotly theme helper ───────────────────────────────────
function plotlyTheme() {
    const dark = html.getAttribute("data-theme") === "dark";
    return {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor:  "rgba(0,0,0,0)",
        font: { color: dark ? "#94a3b8" : "#475569", family: "Inter, sans-serif", size: 11 },
    };
}

function renderChart(id, chartJson) {
    const parsed = JSON.parse(chartJson);
    const layout = Object.assign({}, parsed.layout, plotlyTheme(), {
        margin: { l: 40, r: 20, t: 40, b: 40 },
    });
    Plotly.react(id, parsed.data, layout, { responsive: true, displayModeBar: false });
}

// ── Filters ───────────────────────────────────────────────
function currentFilters() {
    return {
        city:           document.getElementById("cityFilter").value,
        category:       document.getElementById("categoryFilter").value,
        order_status:   document.getElementById("orderStatusFilter").value,
        payment_status: document.getElementById("paymentStatusFilter").value,
        start_date:     document.getElementById("startDateFilter").value,
        end_date:       document.getElementById("endDateFilter").value,
    };
}

// ── Main refresh ──────────────────────────────────────────
async function refreshDashboard() {
    startLoading();
    try {
        const params = new URLSearchParams(currentFilters());
        const response = await fetch(`/api/dashboard-data?${params.toString()}`);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const payload = await response.json();

        // KPIs
        document.getElementById("kpiTotalSales").textContent   = `INR ${formatNumber(payload.kpis.total_sales)}`;
        document.getElementById("kpiTotalProfit").textContent  = `INR ${formatNumber(payload.kpis.total_profit)}`;
        document.getElementById("kpiTotalOrders").textContent  = formatNumber(payload.kpis.total_orders);
        document.getElementById("kpiAvgMargin").textContent    = `${formatNumber(payload.kpis.avg_margin)}%`;
        document.getElementById("kpiTotalPaid").textContent    = `INR ${formatNumber(payload.kpis.total_paid)}`;
        document.getElementById("kpiTotalBalance").textContent = `INR ${formatNumber(payload.kpis.total_balance)}`;

        // Charts
        renderChart("trendChart",        payload.charts.trend);
        renderChart("monthlyProfitChart",payload.charts.monthly_profit);
        renderChart("categoryChart",     payload.charts.category);
        renderChart("orderStatusChart",  payload.charts.order_status);
        renderChart("paymentChart",      payload.charts.payment);
        renderChart("indiaMapChart",     payload.charts.india_map);
        renderChart("topProductsChart",  payload.charts.top_products);

        // Gauge
        const dark = html.getAttribute("data-theme") === "dark";
        Plotly.react(
            "paidGaugeChart",
            [{
                type: "indicator",
                mode: "gauge+number",
                value: payload.kpis.paid_ratio,
                number: { suffix: "%", font: { color: dark ? "#f1f5f9" : "#0f172a" } },
                title: { text: "Collection Ratio", font: { color: dark ? "#94a3b8" : "#475569", size: 12 } },
                gauge: {
                    axis: { range: [0, 100], tickcolor: dark ? "#475569" : "#94a3b8" },
                    bar: { color: "#4f46e5" },
                    bgcolor: "rgba(0,0,0,0)",
                    bordercolor: "rgba(0,0,0,0)",
                    steps: [
                        { range: [0,  50], color: dark ? "#3f1a1a" : "#fde8e8" },
                        { range: [50, 80], color: dark ? "#3f3a1a" : "#fef9c3" },
                        { range: [80,100], color: dark ? "#1a3f2a" : "#dcfce7" },
                    ],
                },
            }],
            Object.assign({ margin: { t: 50, r: 20, b: 20, l: 20 } }, plotlyTheme()),
            { responsive: true, displayModeBar: false }
        );

        // Top Retailers
        const retailerList = document.getElementById("topRetailersList");
        retailerList.innerHTML = "";
        for (const row of payload.top_retailers || []) {
            const li = document.createElement("li");
            li.innerHTML = `<span>${row["Retailer Name"] || "N/A"}</span><strong>INR ${formatNumber(row["Grand Total (INR)"])}</strong>`;
            retailerList.appendChild(li);
        }

        // Analytics
        const ana = payload.analytics;
        document.getElementById("forecastValue").textContent   = `INR ${formatNumber(ana.forecast.next_month)}`;
        document.getElementById("forecastDetails").textContent = `Growth expected based on last month's performance.`;
        document.getElementById("rfmChampions").textContent    = `${formatNumber(ana.rfm.champions)} Champions`;
        document.getElementById("rfmAtRisk").textContent       = `${formatNumber(ana.rfm.at_risk)} At Risk`;
        document.getElementById("rfmNew").textContent          = `${formatNumber(ana.rfm.new)} Others`;

        stopLoading();
    } catch (err) {
        stopLoading();
        console.error("Dashboard refresh failed:", err);
        showToast(`⚠ Dashboard refresh failed: ${err.message}`, "error");
    }
}

// ── Filter listeners ──────────────────────────────────────
document.querySelectorAll("select, input[type=date]").forEach((el) => {
    el.addEventListener("change", refreshDashboard);
});

// ── Export CSV ────────────────────────────────────────────
document.getElementById("exportCsvBtn").addEventListener("click", () => {
    const params = new URLSearchParams(currentFilters());
    window.location.href = `/api/export/csv?${params.toString()}`;
    showToast("✅ CSV export started");
});

// ── Export Excel ──────────────────────────────────────────
document.getElementById("exportExcelBtn").addEventListener("click", () => {
    const params = new URLSearchParams(currentFilters());
    window.location.href = `/api/export/excel?${params.toString()}`;
    showToast("✅ Excel export started");
});

// ── Export PDF (html2canvas + jsPDF) ─────────────────────
document.getElementById("exportPdfBtn").addEventListener("click", async () => {
    showToast("📄 Generating PDF, please wait…");
    try {
        const { jsPDF } = window.jspdf;
        const isDark = html.getAttribute("data-theme") === "dark";

        // Solid color values that html2canvas can actually render
        const solidBg    = isDark ? "#1e293b" : "#ffffff";
        const solidBg2   = isDark ? "#111827" : "#f8fafc";
        const solidText  = isDark ? "#f1f5f9" : "#0f172a";
        const solidText2 = isDark ? "#94a3b8" : "#475569";
        const bodyBg     = isDark ? "#0b0f1a" : "#f0f4ff";

        // ── Build a report header element ──────────────────
        const filters = currentFilters();
        const activeFilters = Object.entries(filters)
            .filter(([, v]) => v)
            .map(([k, v]) => `${k.replace(/_/g," ")}: ${v}`)
            .join("  |  ");

        const header = document.createElement("div");
        header.id = "pdf-report-header";
        header.style.cssText = `
            background: linear-gradient(120deg, #0f172a 0%, #1e1b4b 50%, #1e3a8a 100%);
            color: #ffffff;
            padding: 20px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: Inter, sans-serif;
        `;
        header.innerHTML = `
            <div>
                <div style="font-size:22px;font-weight:800;letter-spacing:-0.5px;">Sales Dashboard Report</div>
                <div style="font-size:12px;opacity:0.7;margin-top:4px;">
                    ${activeFilters ? "Filters: " + activeFilters : "All data — no filters applied"}
                </div>
            </div>
            <div style="text-align:right;font-size:12px;opacity:0.7;">
                <div>Generated on</div>
                <div style="font-weight:600;">${new Date().toLocaleString("en-IN")}</div>
            </div>
        `;

        const content = document.getElementById("dashboardContent");
        content.prepend(header);

        // ── Inject solid-bg overrides (fix glassmorphism) ──
        const tmpStyle = document.createElement("style");
        tmpStyle.id = "pdf-override";
        tmpStyle.textContent = `
            .kpi-card, .chart-card, .insight-card, .filter-card, .card {
                background: ${solidBg} !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border-color: rgba(99,120,200,0.25) !important;
            }
            .kpi-label, .section-label { color: ${solidText2} !important; }
            .kpi-value                 { color: ${solidText}  !important; }
            .top-list li               { color: ${solidText2} !important; border-color: rgba(99,120,200,0.2) !important; }
            .top-list li strong        { color: #4f46e5 !important; }
            .card-header {
                background: ${solidBg2} !important;
                color: ${solidText2} !important;
                border-color: rgba(99,120,200,0.2) !important;
            }
            .text-gradient {
                -webkit-text-fill-color: #4f46e5 !important;
                color: #4f46e5 !important;
            }
            .badge { opacity: 1 !important; }
        `;
        document.head.appendChild(tmpStyle);

        // Small paint delay
        await new Promise(r => setTimeout(r, 200));

        const canvas = await html2canvas(content, {
            scale: 1.8,
            useCORS: true,
            allowTaint: true,
            logging: false,
            backgroundColor: bodyBg,
        });

        // ── Cleanup ────────────────────────────────────────
        document.getElementById("pdf-override").remove();
        document.getElementById("pdf-report-header").remove();

        // ── Build PDF ──────────────────────────────────────
        const imgData = canvas.toDataURL("image/png");
        const pdfW = canvas.width;
        const pdfH = canvas.height;
        const pdf = new jsPDF({
            orientation: pdfW > pdfH ? "landscape" : "portrait",
            unit: "px",
            format: [pdfW, pdfH],
        });
        pdf.addImage(imgData, "PNG", 0, 0, pdfW, pdfH);
        pdf.save("sales_dashboard.pdf");
        showToast("✅ PDF saved successfully");

    } catch (err) {
        // Always clean up on error
        ["pdf-override", "pdf-report-header"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.remove();
        });
        console.error("PDF export failed:", err);
        showToast("⚠ PDF export failed: " + err.message, "error");
    }
});

// ── Auto-refresh ──────────────────────────────────────────
refreshDashboard();
setInterval(refreshDashboard, 5000);
