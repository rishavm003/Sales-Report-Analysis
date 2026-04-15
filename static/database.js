// ── Theme sync ────────────────────────────────────────────
const savedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);

// ── Toast ─────────────────────────────────────────────────
function showAdminToast(message, type = "success") {
    let container = document.getElementById("adminToastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "adminToastContainer";
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `toast-msg${type === "error" ? " error" : ""}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ── Format number ─────────────────────────────────────────
function fmt(value) {
    if (value === null || value === undefined || value === "") return "—";
    if (!isNaN(value)) return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(Number(value));
    return value;
}

// ── Payment status badge ──────────────────────────────────
function paymentBadge(status) {
    const map = {
        "Paid":    "bg-success",
        "Pending": "bg-danger",
        "Partial": "bg-warning text-dark",
    };
    const cls = map[status] || "bg-secondary";
    return `<span class="badge ${cls}" style="font-size:11px;">${status || "—"}</span>`;
}

// ── Load orders ───────────────────────────────────────────
async function loadOrders() {
    const params = new URLSearchParams({
        limit:          "250",
        city:           document.getElementById("adminCityFilter")?.value || "",
        category:       document.getElementById("adminCategoryFilter")?.value || "",
        order_status:   document.getElementById("adminOrderStatusFilter")?.value || "",
        payment_status: document.getElementById("adminPaymentStatusFilter")?.value || "",
        start_date:     document.getElementById("adminStartDateFilter")?.value || "",
        end_date:       document.getElementById("adminEndDateFilter")?.value || "",
    });

    try {
        const response = await fetch(`/api/orders?${params.toString()}`);
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        if (!response.ok) throw new Error(`Server error ${response.status}`);

        const rows = await response.json();
        const tbody = document.querySelector("#ordersTable tbody");
        tbody.innerHTML = "";

        if (!rows.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="table-empty-state">
                        <span class="empty-icon">📭</span>
                        No orders found for the selected filters.
                    </td>
                </tr>`;
            return;
        }

        for (const row of rows) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><span style="font-weight:600;color:var(--accent-1);">#${row.id}</span></td>
                <td>${row["Date"] ? String(row["Date"]).slice(0, 10) : "—"}</td>
                <td>${row["City"] || "—"}</td>
                <td>${row["Product Category"] || "—"}</td>
                <td style="font-weight:600;">₹${fmt(row["Grand Total (INR)"])}</td>
                <td style="color:var(--accent-3);">₹${fmt(row["Profit (INR)"])}</td>
                <td>${paymentBadge(row["Payment Status"])}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" style="font-size:11px;padding:3px 10px;"
                        onclick="deleteOrder(${row.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    } catch (err) {
        console.error("Failed to load orders:", err);
        showAdminToast("⚠ Failed to load orders: " + err.message, "error");
    }
}

// ── Delete single order ───────────────────────────────────
async function deleteOrder(id) {
    if (!confirm(`Delete order #${id}? This cannot be undone.`)) return;
    try {
        const response = await fetch(`/api/order/${id}`, { method: "DELETE" });
        if (response.status === 401) { window.location.href = "/admin/login"; return; }
        if (!response.ok) throw new Error(`Server error ${response.status}`);
        showAdminToast(`✅ Order #${id} deleted`);
        await loadOrders();
    } catch (err) {
        showAdminToast("⚠ Delete failed: " + err.message, "error");
    }
}

// ── Add order form ────────────────────────────────────────
document.getElementById("addOrderForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = {};
    new FormData(form).forEach((value, key) => { data[key] = value; });

    try {
        const response = await fetch("/api/order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (response.status === 401) { window.location.href = "/admin/login"; return; }
        if (!response.ok) throw new Error(`Server error ${response.status}`);
        const result = await response.json();
        showAdminToast(`✅ Order #${result.id} added successfully`);
        form.reset();
        await loadOrders();
    } catch (err) {
        showAdminToast("⚠ Failed to add order: " + err.message, "error");
    }
});

// ── Delete all ────────────────────────────────────────────
document.getElementById("deleteAllBtn").addEventListener("click", async () => {
    const confirmText = prompt("Type DELETE ALL to permanently remove every record:");
    if (confirmText === null) return;
    try {
        const response = await fetch("/api/orders", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ confirm_text: confirmText }),
        });
        if (response.status === 401) { window.location.href = "/admin/login"; return; }
        const result = await response.json();
        if (!response.ok) {
            showAdminToast("⚠ " + (result.message || "Delete all failed."), "error");
            return;
        }
        showAdminToast("✅ All orders deleted");
        await loadOrders();
    } catch (err) {
        showAdminToast("⚠ Delete all failed: " + err.message, "error");
    }
});

// ── Filter listeners ──────────────────────────────────────
["adminCityFilter", "adminCategoryFilter", "adminOrderStatusFilter",
 "adminPaymentStatusFilter", "adminStartDateFilter", "adminEndDateFilter"
].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", loadOrders);
});

// ── Init ──────────────────────────────────────────────────
loadOrders();
setInterval(loadOrders, 5000);
