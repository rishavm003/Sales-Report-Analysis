# API Documentation

## Endpoints

- GET / - Dashboard view
- GET /login - User authentication
- GET /register - User registration
- GET /database - Database management
- GET /users - User management
- GET /charts-report - Data visualization

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    role TEXT
);
```
