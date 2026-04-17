# 📦 Inventory Management System (Backend)

A scalable backend system for managing inventory across multiple warehouses. Built with **Django** and **Django REST Framework**, it provides structured stock tracking, product management, and stock movement logging.

---

## 🚀 Features

- 📦 Item/Product management (SKU-based)
- 🏢 Multiple warehouse support
- 📊 Real-time stock tracking
- ➕ Stock In (restocking items)
- ➖ Stock Out (sales/usage)
- 🧾 Stock movement logs (audit trail)
- 🔐 Authentication & protected APIs (JWT/session-based)
- ⚙️ Clean service-based architecture

---

## 🏗️ Tech Stack

- Python 3.x
- Django
- Django REST Framework
- PostgreSQL / SQLite
- Git & GitHub

---

## ⚙️ Installation

### 1. Clone repository

git clone https://github.com/jospin-Byadunia/Instock.git <br>
cd Instock/backend

### 2. Create virtual environment

- python -m venv venv
- source venv/Scripts/activate # Windows

### 3. Install dependencies

pip install -r requirements.txt

### 4. Setup environment variables

Create a .env file in backend root:

- SECRET_KEY=your_secret_key
- DEBUG=True
- DATABASE_URL=your_database_url

### 5. Run migrations

- python manage.py makemigrations
- python manage.py migrate

### 6. Create superuser

python manage.py createsuperuser

### 7. Run server

python manage.py runserver

---

## 📡 API Endpoints

### Authentication

- POST /api/auth/login/
- POST /api/auth/logout/

### Items

- GET /api/items/
- POST /api/items/

### Stock

- POST /api/v1/manage/stock/in/
- POST /api/v1/manage/stock/out/
- GET /api/v1/manage/stock/

### Warehouses

- GET /api/warehouses/
- POST /api/warehouses/

## 👨‍💻 Author

Jospin Murhiorhakube B. <br>
Backend Developer | Django | Networking & Systems

## ⭐ Notes

This project is designed for real-world inventory system foundations, focusing on clean architecture and scalable backend design.
