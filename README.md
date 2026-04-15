# Sales Dashboard (Flask + SQLite + Plotly)

An interactive data analyst web project built with Flask UI and SQLite database using the dataset:
`wholesale_orders_final.xlsx`.

The app provides:
- Interactive dashboard with KPI cards, filters, multiple charts, and India sales map
- Real-time dashboard refresh (every 5 seconds)
- Admin panel with login to manage data (add, delete single record, delete all with safety confirmation)

---

## 1) Libraries Used and Their Usage

### `Flask`
- **Why used:** lightweight Python web framework to build pages and APIs quickly.
- **Usage in this project:**
  - Serves dashboard and admin HTML pages
  - Provides REST-style API endpoints for chart/KPI data and CRUD operations
  - Handles admin authentication session (login/logout)

### `sqlite3` (Python standard library)
- **Why used:** simple file-based database (no external DB server needed).
- **Usage in this project:**
  - Stores all order records in `orders.db`
  - Supports add/delete/list operations from admin panel

### `pandas`
- **Why used:** best for Excel reading and fast data transformations.
- **Usage in this project:**
  - Reads `wholesale_orders_final.xlsx`
  - Cleans and converts date columns
  - Applies filter logic (city/category/status/date range)
  - Aggregates KPI and chart data

### `openpyxl`
- **Why used:** engine required by pandas to read `.xlsx` files.
- **Usage in this project:**
  - Enables `pd.read_excel(...)` for the source dataset

### `plotly`
- **Why used:** rich interactive charts (zoom, hover, pan, legends).
- **Usage in this project:**
  - Builds chart JSON on backend
  - Renders charts in browser via Plotly JS
  - Used for trend charts, bar charts, pie charts, gauge, and India map

### `werkzeug.security` (via Flask dependency)
- **Why used:** secure password hash checking.
- **Usage in this project:**
  - Validates admin password using hash verification

### Frontend/CDN libraries
- **Bootstrap 5:** layout/grid/forms/cards for clean responsive UI
- **Plotly JS CDN:** renders backend-provided chart JSON on dashboard

---

## 2) Project Structure

- `app.py` -> main Flask app, routes, auth, data processing, APIs
- `templates/dashboard.html` -> dashboard UI
- `templates/database.html` -> admin panel UI (data management)
- `templates/admin_login.html` -> admin login screen
- `static/dashboard.js` -> dashboard live updates and chart rendering
- `static/database.js` -> admin CRUD logic and filters
- `static/styles.css` -> common styling/theme
- `requirements.txt` -> Python dependencies
- `orders.db` -> SQLite database (auto-created on first run)
- `wholesale_orders_final.xlsx` -> original source dataset

---

## 3) How This Project Is Built (From Scratch)

### Step 1: Initialize basic Flask app
1. Create `app.py`
2. Add Flask instance and base route `/`
3. Add templates and static folder setup

### Step 2: Connect dataset and database
1. Place `wholesale_orders_final.xlsx` in project root
2. On app startup:
   - Create SQLite table `orders` if not exists
   - Load Excel with pandas
   - Rename currency columns from `(₹)` to `(INR)`
   - Insert records into SQLite when DB is empty

### Step 3: Build dashboard backend logic
1. Read rows from SQLite into pandas DataFrame
2. Apply filters (city/category/order status/payment status/date range)
3. Compute KPIs:
   - total sales, total profit, total orders, avg margin, paid, pending
4. Build Plotly figures:
   - Sales trend
   - Monthly profit
   - Top categories
   - Top products
   - Payment split
   - Order status split
   - India map by city coordinates
   - Collection ratio gauge
5. Return all results via `/api/dashboard-data`

### Step 4: Build dashboard frontend
1. Create KPI cards and filter controls in `dashboard.html`
2. Use `dashboard.js` to:
   - Call `/api/dashboard-data`
   - Render KPIs
   - Render Plotly charts
   - Auto-refresh every 5 seconds

### Step 5: Build admin panel (CRUD)
1. Create `database.html` for table + forms
2. Add admin filters for table browsing
3. Add APIs:
   - `GET /api/orders`
   - `POST /api/order`
   - `DELETE /api/order/<id>`
   - `DELETE /api/orders`
4. Use `database.js` to call these APIs and refresh table in near real-time

### Step 6: Add admin authentication and safety
1. Add login page `/admin/login`
2. Protect `/database` and admin APIs with session check
3. Add logout route `/admin/logout`
4. Add delete-all confirmation phrase (`DELETE ALL`) in frontend + backend validation

### Step 7: Polish UI
1. Add card-based modern styling in `styles.css`
2. Improve responsive layout for dashboard cards/charts
3. Align interface naming to **Sales Dashboard**

---

## 4) Installation and Run

### Prerequisites
- Python 3.10+ recommended
- Dataset file: `wholesale_orders_final.xlsx`

### Install dependencies
```bash
python -m pip install -r requirements.txt
```

### Run app
```bash
python app.py
```

### Open in browser
- `http://127.0.0.1:5000` -> Sales Dashboard
- `http://127.0.0.1:5000/admin/login` -> Admin Login

---

## 5) Routes and API Usage

### UI Routes
- `GET /` -> main dashboard
- `GET /admin/login` -> admin login page
- `POST /admin/login` -> login submit
- `GET /admin/logout` -> logout
- `GET /database` -> admin panel (requires login)

### Data APIs
- `GET /api/dashboard-data`
  - Query params (optional): `city`, `category`, `order_status`, `payment_status`, `start_date`, `end_date`
  - Returns KPIs + chart JSON payload

- `GET /api/orders`
  - Query params: `limit` (default 250) + same filters as above
  - Returns filtered order rows for admin table

- `POST /api/order`
  - Adds one order record from JSON body

- `DELETE /api/order/<id>`
  - Deletes one row by ID

- `DELETE /api/orders`
  - Deletes all rows
  - Requires JSON body:
    ```json
    { "confirm_text": "DELETE ALL" }
    ```

---

## 6) Default Admin Credentials

- Username: `admin`
- Password: `admin123`

For production use, change credentials and secret key immediately.

---

## 7) Real-Time Behavior

- Dashboard auto-refreshes every 5 seconds to show latest KPIs/charts
- Admin order table also auto-refreshes every 5 seconds
- Any add/delete in admin reflects on dashboard in next refresh cycle

---

## 8) Future Improvements (Recommended)

- Move admin username/password and Flask secret key to `.env`
- Add edit/update API for existing records
- Add audit log for delete operations
- Add role-based access (viewer/admin)
- Add export feature for filtered data (CSV/Excel)
