# 🌍 Mzansi Market Tracker

Mzansi Market Tracker is a **Python-based terminal application** designed to help stall owners manage their market products, sales, and weekly reports. The application uses **PostgreSQL** as its database and supports **stall owner registration, login, product management, sales tracking, and report generation**.

---

## 🛠 Features

1. **Stall Owner Registration & Login**
   - Secure registration with username and password.
   - Passwords are hashed using SHA-256.
   - Login system ensures only authorized users can manage products and sales.

2. **Product Management**
   - Add new products with price and stock quantity.
   - View all available products.
   - Search products by name or ID.

3. **Sales Management**
   - Record product sales with quantity and automatic stock update.
   - Weekly sales report with total sold and total revenue.

4. **Reporting**
   - Export weekly sales reports to CSV for easy sharing.
   - Display sales reports directly in the terminal.

5. **User-Friendly Interface**
   - Emojis and clear commit messages for successful database actions.
   - Color-coded messages (optional with `colorama`).

---

## 💾 Technology Stack

- **Python 3**
- **PostgreSQL**
- **pandas** (for exporting reports)
- **hashlib** (for password hashing)
- **csv** (for CSV report export)

---

## ⚙️ Installation

1. Clone the repository:


