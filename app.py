import json
import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_caching import Cache
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "orders.db"
EXCEL_PATH = BASE_DIR / "wholesale_orders_final.xlsx"
TABLE_NAME = "orders"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

CITY_COORDS = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "bengaluru": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "ahmedabad": (23.0225, 72.5714),
    "pune": (18.5204, 73.8567),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "indore": (22.7196, 75.8577),
    "surat": (21.1702, 72.8311),
    "nagpur": (21.1458, 79.0882),
    "bhopal": (23.2599, 77.4126),
    "patna": (25.5941, 85.1376),
    "kanpur": (26.4499, 80.3319),
    "vadodara": (22.3072, 73.1812),
    "ludhiana": (30.9010, 75.8573),
    "agra": (27.1767, 78.0081),
    "nashik": (19.9975, 73.7898),
    "coimbatore": (11.0168, 76.9558),
    "visakhapatnam": (17.6868, 83.2185),
    "varanasi": (25.3176, 82.9739),
    "madurai": (9.9252, 78.1198),
    "rajkot": (22.3039, 70.8022),
    "meerut": (28.9845, 77.7064),
}

DATE_COLUMNS = ["Date", "Delivery Date"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found: {EXCEL_PATH}")

    conn = get_connection()
    try:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Date" TEXT,
                "City" TEXT,
                "Product Category" TEXT,
                "Product Name" TEXT,
                "Unit Type" TEXT,
                "Rate (INR)" REAL,
                "Quantity" REAL,
                "Total Amount (INR)" REAL,
                "Cost per Unit (INR)" REAL,
                "Total Cost (INR)" REAL,
                "Profit (INR)" REAL,
                "Profit Margin (%)" REAL,
                "Delivery Date" TEXT,
                "Retailer Name" TEXT,
                "Phone Number" TEXT,
                "Email ID" TEXT,
                "Payment Terms" TEXT,
                "Amount Paid (INR)" REAL,
                "Balance (INR)" REAL,
                "Order Status" TEXT,
                "Payment Status" TEXT,
                "GST (%)" REAL,
                "GST Amount (INR)" REAL,
                "Grand Total (INR)" REAL,
                "Notes" TEXT
            )
            """
        )
        current_rows = conn.execute(f"SELECT COUNT(*) AS c FROM {TABLE_NAME}").fetchone()["c"]
        if current_rows == 0:
            source = pd.read_excel(EXCEL_PATH)
            source = source.rename(
                columns={
                    "Rate (₹)": "Rate (INR)",
                    "Total Amount (₹)": "Total Amount (INR)",
                    "Cost per Unit (₹)": "Cost per Unit (INR)",
                    "Total Cost (₹)": "Total Cost (INR)",
                    "Profit (₹)": "Profit (INR)",
                    "Amount Paid (₹)": "Amount Paid (INR)",
                    "Balance (₹)": "Balance (INR)",
                    "GST Amount (₹)": "GST Amount (INR)",
                    "Grand Total (₹)": "Grand Total (INR)",
                }
            )
            source.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()


def read_orders():
    conn = get_connection()
    try:
        frame = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    finally:
        conn.close()
    if not frame.empty:
        for col in DATE_COLUMNS:
            if col in frame.columns:
                frame[col] = pd.to_datetime(frame[col], errors="coerce", dayfirst=True)
    return frame


def apply_filters(df, params):
    filtered = df.copy()
    city = params.get("city", "").strip()
    category = params.get("category", "").strip()
    order_status = params.get("order_status", "").strip()
    payment_status = params.get("payment_status", "").strip()
    start_date = params.get("start_date", "").strip()
    end_date = params.get("end_date", "").strip()

    if city:
        filtered = filtered[filtered["City"] == city]
    if category:
        filtered = filtered[filtered["Product Category"] == category]
    if order_status:
        filtered = filtered[filtered["Order Status"] == order_status]
    if payment_status:
        filtered = filtered[filtered["Payment Status"] == payment_status]
    if start_date:
        start = pd.to_datetime(start_date, errors="coerce")
        filtered = filtered[filtered["Date"] >= start]
    if end_date:
        end = pd.to_datetime(end_date, errors="coerce")
        filtered = filtered[filtered["Date"] <= end]

    return filtered


def build_advanced_analytics(filtered):
    # 1. Forecasting: Simple 3-month linear trend
    forecast = {"next_month": 0, "month_after": 0, "q3_expected": 0}
    if not filtered.empty:
        sales_by_month = (
            filtered.dropna(subset=["Date"])
            .groupby(filtered["Date"].dt.to_period("M"))["Grand Total (INR)"]
            .sum()
            .reset_index()
        )
        if len(sales_by_month) >= 2:
            last_val = sales_by_month.iloc[-1]["Grand Total (INR)"]
            prev_val = sales_by_month.iloc[-2]["Grand Total (INR)"]
            growth = last_val - prev_val
            forecast["next_month"] = round(max(0, last_val + growth), 2)
            forecast["month_after"] = round(max(0, last_val + 2 * growth), 2)
            forecast["q3_expected"] = round(max(0, 3 * last_val + 6 * growth), 2)
        elif not sales_by_month.empty:
            forecast["next_month"] = round(sales_by_month.iloc[-1]["Grand Total (INR)"], 2)

    # 2. RFM Analysis: Segmentation
    rfm_segments = {"champions": 0, "at_risk": 0, "new": 0}
    if not filtered.empty:
        customer_agg = (
            filtered.groupby("Retailer Name")
            .agg({"Grand Total (INR)": "sum", "id": "count"})
            .rename(columns={"Grand Total (INR)": "monetary", "id": "frequency"})
        )
        if not customer_agg.empty:
            m_thresh = customer_agg["monetary"].quantile(0.75)
            f_thresh = customer_agg["frequency"].quantile(0.75)
            rfm_segments["champions"] = int(
                len(customer_agg[(customer_agg["monetary"] >= m_thresh) & (customer_agg["frequency"] >= f_thresh)])
            )
            rfm_segments["at_risk"] = int(
                len(customer_agg[(customer_agg["monetary"] < m_thresh) & (customer_agg["frequency"] < f_thresh)])
            )
            rfm_segments["new"] = int(len(customer_agg) - rfm_segments["champions"] - rfm_segments["at_risk"])

    return {"forecast": forecast, "rfm": rfm_segments}


def build_dashboard_payload(filtered):
    total_sales = float(filtered["Grand Total (INR)"].fillna(0).sum())
    total_profit = float(filtered["Profit (INR)"].fillna(0).sum())
    total_orders = int(filtered.shape[0])
    avg_margin = float(filtered["Profit Margin (%)"].fillna(0).mean()) if total_orders else 0.0
    total_paid = float(filtered["Amount Paid (INR)"].fillna(0).sum()) if "Amount Paid (INR)" in filtered else 0.0
    total_balance = float(filtered["Balance (INR)"].fillna(0).sum()) if "Balance (INR)" in filtered else 0.0
    paid_ratio = (total_paid / total_sales * 100.0) if total_sales > 0 else 0.0

    sales_trend = (
        filtered.dropna(subset=["Date"])
        .groupby(filtered["Date"].dt.to_period("M"))["Grand Total (INR)"]
        .sum()
        .reset_index()
    )
    if not sales_trend.empty:
        sales_trend["Date"] = sales_trend["Date"].astype(str)
    trend_fig = px.line(
        sales_trend,
        x="Date",
        y="Grand Total (INR)",
        markers=True,
        title="Sales Trend by Month",
    )
    trend_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    category_sales = (
        filtered.groupby("Product Category")["Grand Total (INR)"]
        .sum()
        .reset_index()
        .sort_values("Grand Total (INR)", ascending=False)
        .head(10)
    )
    category_fig = px.bar(
        category_sales,
        x="Product Category",
        y="Grand Total (INR)",
        title="Top Categories by Sales",
    )
    category_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    payment_split = filtered.groupby("Payment Status").size().reset_index(name="Count")
    payment_fig = px.pie(payment_split, names="Payment Status", values="Count", title="Payment Status Split")
    payment_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    order_split = filtered.groupby("Order Status").size().reset_index(name="Count")
    order_fig = px.bar(order_split, x="Order Status", y="Count", title="Order Status Count")
    order_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    city_sales = filtered.groupby("City")["Grand Total (INR)"].sum().reset_index()
    city_sales["city_key"] = city_sales["City"].astype(str).str.strip().str.lower()
    city_sales["lat"] = city_sales["city_key"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    city_sales["lon"] = city_sales["city_key"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])
    map_data = city_sales.dropna(subset=["lat", "lon"]).copy()
    if map_data.empty:
        map_data = pd.DataFrame(
            {
                "City": ["No mapped city"],
                "Grand Total (INR)": [0],
                "lat": [22.9734],
                "lon": [78.6569],
            }
        )
    map_fig = px.scatter_geo(
        map_data,
        lat="lat",
        lon="lon",
        size="Grand Total (INR)",
        hover_name="City",
        color="Grand Total (INR)",
        projection="natural earth",
        title="India Sales Map",
    )
    map_fig.update_geos(
        scope="asia",
        center=dict(lat=22.9734, lon=78.6569),
        lataxis_range=[6, 38],
        lonaxis_range=[67, 97],
        showland=True,
        landcolor="rgb(240, 240, 240)",
    )
    map_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    monthly_profit = (
        filtered.dropna(subset=["Date"])
        .groupby(filtered["Date"].dt.to_period("M"))["Profit (INR)"]
        .sum()
        .reset_index()
    )
    if not monthly_profit.empty:
        monthly_profit["Date"] = monthly_profit["Date"].astype(str)
    profit_fig = px.area(
        monthly_profit,
        x="Date",
        y="Profit (INR)",
        title="Monthly Profit",
    )
    profit_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    top_products = (
        filtered.groupby("Product Name")["Grand Total (INR)"]
        .sum()
        .reset_index()
        .sort_values("Grand Total (INR)", ascending=False)
        .head(8)
    )
    product_fig = px.bar(
        top_products,
        x="Product Name",
        y="Grand Total (INR)",
        title="Top Products by Sales",
    )
    product_fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))

    top_retailers = (
        filtered.groupby("Retailer Name")["Grand Total (INR)"]
        .sum()
        .reset_index()
        .sort_values("Grand Total (INR)", ascending=False)
        .head(5)
    )

    return {
        "kpis": {
            "total_sales": round(total_sales, 2),
            "total_profit": round(total_profit, 2),
            "total_orders": total_orders,
            "avg_margin": round(avg_margin, 2),
            "total_paid": round(total_paid, 2),
            "total_balance": round(total_balance, 2),
            "paid_ratio": round(paid_ratio, 2),
        },
        "top_retailers": json.loads(top_retailers.to_json(orient="records", date_format="iso")),
        "charts": {
            "trend": trend_fig.to_json(),
            "category": category_fig.to_json(),
            "payment": payment_fig.to_json(),
            "order_status": order_fig.to_json(),
            "india_map": map_fig.to_json(),
            "monthly_profit": profit_fig.to_json(),
            "top_products": product_fig.to_json(),
        },
        "analytics": build_advanced_analytics(filtered),
    }


def get_filter_options(df):
    return {
        "cities": sorted(df["City"].dropna().astype(str).unique().tolist()),
        "categories": sorted(df["Product Category"].dropna().astype(str).unique().tolist()),
        "order_statuses": sorted(df["Order Status"].dropna().astype(str).unique().tolist()),
        "payment_statuses": sorted(df["Payment Status"].dropna().astype(str).unique().tolist()),
    }


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-key-123")
app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "SimpleCache")
app.config["CACHE_DEFAULT_TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

cache = Cache(app)
initialize_database()


def is_admin_logged_in():
    return session.get("is_admin") is True


def api_admin_guard():
    if not is_admin_logged_in():
        return jsonify({"message": "Unauthorized"}), 401
    return None


@app.get("/")
def dashboard():
    df = read_orders()
    return render_template("dashboard.html", filter_options=get_filter_options(df))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if is_admin_logged_in():
            return redirect(url_for("database_view"))
        return render_template("admin_login.html", error=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
        session["is_admin"] = True
        return redirect(url_for("database_view"))
    return render_template("admin_login.html", error="Invalid username or password.")


@app.get("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.get("/database")
def database_view():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))
    df = read_orders()
    return render_template("database.html", filter_options=get_filter_options(df))


@app.get("/api/dashboard-data")
@cache.cached(query_string=True)
def dashboard_data():
    df = read_orders()
    filtered = apply_filters(df, request.args)
    return jsonify(build_dashboard_payload(filtered))


@app.get("/api/export/<fmt>")
def export_data(fmt):
    df = read_orders()
    filtered = apply_filters(df, request.args)
    if fmt == "csv":
        temp_path = BASE_DIR / "export.csv"
        filtered.to_csv(temp_path, index=False)
        return send_file(temp_path, as_attachment=True, download_name="sales_export.csv")
    elif fmt == "excel":
        temp_path = BASE_DIR / "export.xlsx"
        filtered.to_excel(temp_path, index=False)
        return send_file(temp_path, as_attachment=True, download_name="sales_export.xlsx")
    return jsonify({"message": "Invalid format"}), 400


@app.get("/api/orders")
def list_orders():
    unauthorized = api_admin_guard()
    if unauthorized:
        return unauthorized
    limit = int(request.args.get("limit", "250"))
    df = read_orders()
    filtered = apply_filters(df, request.args)
    if filtered.empty:
        return jsonify([])
    filtered = filtered.sort_values("id", ascending=False).head(limit)
    # Use pandas to_json to safely convert NaN/NaT → null (avoids invalid JSON)
    records = json.loads(filtered.to_json(orient="records", date_format="iso"))
    return jsonify(records)


@app.post("/api/order")
def add_order():
    unauthorized = api_admin_guard()
    if unauthorized:
        return unauthorized
    payload = request.get_json(force=True) or {}
    columns = [
        "Date",
        "City",
        "Product Category",
        "Product Name",
        "Unit Type",
        "Rate (INR)",
        "Quantity",
        "Total Amount (INR)",
        "Cost per Unit (INR)",
        "Total Cost (INR)",
        "Profit (INR)",
        "Profit Margin (%)",
        "Delivery Date",
        "Retailer Name",
        "Phone Number",
        "Email ID",
        "Payment Terms",
        "Amount Paid (INR)",
        "Balance (INR)",
        "Order Status",
        "Payment Status",
        "GST (%)",
        "GST Amount (INR)",
        "Grand Total (INR)",
        "Notes",
    ]

    values = [payload.get(col, None) for col in columns]
    placeholders = ", ".join(["?"] * len(columns))
    quoted_columns = ", ".join([f'"{col}"' for col in columns])

    conn = get_connection()
    try:
        cursor = conn.execute(
            f'INSERT INTO {TABLE_NAME} ({quoted_columns}) VALUES ({placeholders})',
            values,
        )
        conn.commit()
        inserted_id = cursor.lastrowid
    finally:
        conn.close()
    return jsonify({"message": "Order added successfully", "id": inserted_id}), 201


@app.delete("/api/order/<int:order_id>")
def delete_single_order(order_id):
    unauthorized = api_admin_guard()
    if unauthorized:
        return unauthorized
    conn = get_connection()
    try:
        cursor = conn.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (order_id,))
        conn.commit()
        deleted = cursor.rowcount
    finally:
        conn.close()
    if deleted == 0:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({"message": f"Order {order_id} deleted"})


@app.delete("/api/orders")
def delete_all_orders():
    unauthorized = api_admin_guard()
    if unauthorized:
        return unauthorized
    payload = request.get_json(silent=True) or {}
    if payload.get("confirm_text", "").strip() != "DELETE ALL":
        return jsonify({"message": "Confirmation text is incorrect."}), 400
    conn = get_connection()
    try:
        conn.execute(f"DELETE FROM {TABLE_NAME}")
        conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "All orders deleted"})


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
