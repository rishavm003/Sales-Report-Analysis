# Sales Dashboard (Flask + SQLite + Plotly)

An interactive data analyst web project built with Flask UI and SQLite database using the dataset:
`wholesale_orders_final.xlsx`.

The app provides:
- Interactive dashboard with KPI cards, filters, multiple charts, and India sales map
- Real-time dashboard refresh (every 5 seconds)
- Admin panel with login to manage data (add, delete single record, delete all with safety confirmation)

## Modern Project Structure

This project has been reorganized to follow modern Python project structure conventions:

```
sales-dashboard/
├── README.md
├── CHANGELOG.md
├── configs/
│   └── requirements.txt
├── docs/
│   └── api.md
├── main.py
├── setup.py
├── tests/
│   └── __init__.py
└── src/
    └── sales_dashboard/
        ├── __init__.py
        ├── app.py
        ├── api/
        │   └── __init__.py
        ├── config/
        │   └── config.py
        ├── models/
        │   └── __init__.py
        ├── utils/
        │   └── __init__.py
        └── views/
            └── __init__.py
```

## Key Improvements

1. **Separation of Concerns**: Code is organized into logical modules (api, models, views, utils)
2. **Configuration Management**: Configuration files are centralized in the configs/ directory
3. **Documentation**: API documentation moved to docs/ directory
4. **Package Structure**: Follows modern Python packaging conventions
5. **Test Organization**: Dedicated tests/ directory for unit and integration tests
6. **Entry Point**: Clear main.py entry point for the application

## Installation and Run

### Prerequisites
- Python 3.10+ recommended
- Dataset file: `wholesale_orders_final.xlsx`

### Install dependencies
```bash
python -m pip install -r configs/requirements.txt
```

### Run app
```bash
python main.py
```

### Open in browser
- `http://127.0.0.1:5000` -> Sales Dashboard
- `http://127.0.0.1:5000/admin/login` -> Admin Login

## Development

This project now follows modern Python development practices:
- Source code in src/ directory
- Tests in tests/ directory
- Configuration in configs/ directory
- Documentation in docs/ directory
- Package installation via setup.py