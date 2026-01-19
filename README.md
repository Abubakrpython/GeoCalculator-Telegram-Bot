# 🌍 GeoCalculator Telegram Bot

GeoCalculator is an asynchronous Telegram bot built with **Aiogram 3** that calculates the distance between two geographic coordinates, splits the route into equal segments, and generates mission files for drone navigation (INAV-compatible).

This project is designed with a **clean architecture**, **PostgreSQL integration**, and **FSM-based user flow**, making it suitable for real-world production use.

---

## 🚀 Features

- 📍 Calculate geodesic distance between two coordinates  
- 🧭 Split routes into equal segments (2–45 points)  
- 🛫 Assign altitude per waypoint (single or cyclic values)  
- 📄 Generate **INAV `.mission` XML files** automatically  
- 📜 Store and display user calculation history  
- 🔐 Admin notifications on user activity  
- ⚙️ Fully asynchronous & scalable architecture  
- 🔒 Secure configuration using `.env`

---

## 🧱 Tech Stack

- **Python 3.10+**
- **Aiogram 3** – Telegram Bot Framework
- **PostgreSQL** – Database
- **asyncpg** – Async DB driver
- **geopy** – Geodesic distance calculations
- **aiohttp** – Async HTTP requests
- **python-dotenv** – Environment configuration
- **FSM (Finite State Machine)** – User flow control
