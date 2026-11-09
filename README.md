# MediCare – Medical Store Management System

A web-based Medical Store Management System built using **Python, Django, and PostgreSQL**. MediCare helps medical store owners manage medicines, inventory, suppliers, customers, purchases, sales, billing, expenses, and business reports through a centralized dashboard.

---

## 📌 Project Overview

MediCare is designed to simplify the daily operations of a medical store by providing an organized and user-friendly management platform.

The system includes medicine and batch management, purchase and sales tracking, automatic stock updates, payment records, expiry monitoring, expense management, and business reports.

It also provides role-based access for Admin and Staff users.

## 🚀 Live Demo

**Live Website:** https://medicare-viqr.onrender.com/

**GitHub Repository:** https://github.com/RohanJagtap431/MediCare

## ✨ Key Features

### 1. Dashboard
- Overview of daily sales and bills.
- Purchase and expense summaries for Admin.
- Low-stock batch alerts.
- Expired medicine alerts.
- Recent bills overview.
- Quick access to important operations.

### 2. Medicine Management
- Add, update, and delete medicine categories.
- Manage medicine manufacturers.
- Add and update medicine details.
- Manage medicine batches.
- Track batch numbers and expiry dates.
- Maintain purchase price, MRP, and selling price.
- Activate or deactivate medicines and categories.

### 3. Supplier Management
- Add and manage suppliers.
- Store supplier contact details.
- Maintain GSTIN and drug licence information.
- Track supplier opening balances.
- Search and filter supplier records.

### 4. Customer Management
- Add and manage customer information.
- Maintain customer contact details.
- Store customer address information.
- Track customer opening balances.
- Search and manage customer records.

### 5. Purchase Management
- Create purchase invoices.
- Select suppliers and medicine batches.
- Add purchase quantities and free quantities.
- Calculate purchase totals.
- Receive purchases and automatically update stock.
- Prevent duplicate stock addition when receiving the same purchase again.

### 6. Sales & Billing
- Generate customer bills.
- Add multiple medicines to a bill.
- Calculate bill totals and discounts.
- Automatically deduct stock after processing a sale.
- Generate printable invoices.
- Maintain bill history.
- Cancel eligible unpaid sales and restore deducted stock.

### 7. Payment Management
- Record purchase payments.
- Record sales payments.
- Support partial and full payments.
- Maintain payment history.
- Track paid amount, remaining amount, and payment status.
- Support Cash, UPI, Card, Bank Transfer, and Other payment methods.

### 8. Inventory Management
- View available stock.
- Monitor batch-wise quantities.
- Identify low-stock batches.
- Track expired medicines.
- Monitor upcoming expiry dates.
- View expiry alerts and stock status.

### 9. Reports Management
- Reports dashboard.
- Detailed sales reports.
- Detailed purchase reports.
- Date-based filtering.
- CSV export for sales and purchase reports.
- Stock valuation report.
- Purchase value and MRP-based stock valuation.

### 10. Expense Management
- Create and manage expense categories.
- Record daily business expenses.
- Edit and delete expenses.
- Filter expenses by category and date.
- Search expense records.
- View total expense summaries.

### 11. User & Access Management
- Custom Django User Model.
- Admin and Staff roles.
- Login and logout functionality.
- Role-based access restrictions.
- Django Admin Panel integration.

### 12. Responsive UI
- Professional dashboard interface.
- Dark navy sidebar.
- Royal blue highlights.
- Clean white content cards.
- Responsive desktop, tablet, and mobile layouts.
- Mobile-friendly navigation and tables.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Django | Web Framework |
| Django REST Framework | API Framework |
| PostgreSQL | Database |
| Neon | Cloud PostgreSQL Hosting |
| HTML5 | Page Structure |
| CSS3 | Styling and Responsive Design |
| JavaScript | Frontend Interactions |
| Git | Version Control |
| GitHub | Source Code Management |
| Render | Application Deployment |
| WhiteNoise | Static File Serving |
| Gunicorn | Production WSGI Server |

---

## 📂 Project Structure

```text
MediCare/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── decorators.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│
├── medicines/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── suppliers/
├── customers/
├── purchases/
├── sales/
├── inventory/
├── expenses/
├── reports/
├── dashboard/
│
├── templates/
│   ├── accounts/
│   ├── dashboard/
│   ├── medicines/
│   ├── suppliers/
│   ├── customers/
│   ├── purchases/
│   ├── sales/
│   ├── inventory/
│   ├── expenses/
│   ├── reports/
│   └── includes/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
├── manage.py
├── requirements.txt
├── .gitignore
└── .env.example
```

---

## ⚙️ Installation & Setup

Follow these steps to run MediCare locally.

### 1. Clone Repository

```bash
git clone https://github.com/RohanJagtap431/MediCare.git
```

### 2. Navigate to Project Directory

```bash
cd MediCare
```

### 3. Create Virtual Environment

```bash
py -m venv venv
```

### 4. Activate Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DATABASE_URL=postgresql://username:password@host/database?sslmode=require

ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
```

**Important:** Replace the example database connection with your own PostgreSQL connection string.

Never upload your actual `.env` file or secret credentials to GitHub.

### 7. Apply Database Migrations

```bash
py manage.py migrate
```

### 8. Create Superuser

```bash
py manage.py createsuperuser
```

Follow the instructions to create your Admin account.

### 9. Run Development Server

```bash
py manage.py runserver
```

### 10. Open Application

```text
http://127.0.0.1:8000/
```

---

## 🗄️ Database

MediCare uses PostgreSQL for storing application data.

The project is configured to work with Neon PostgreSQL.

Main database entities include:

- User
- ShopProfile
- MedicineCategory
- Manufacturer
- Medicine
- MedicineBatch
- Supplier
- Customer
- Purchase
- PurchaseItem
- PurchasePayment
- Sale
- SaleItem
- SalePayment
- Expense
- ExpenseCategory

---

## 🌐 Deployment

The application is deployed using:

- **GitHub:** Source code repository.
- **Render:** Django application hosting.
- **Neon:** PostgreSQL database hosting.
- **WhiteNoise:** Static file handling.

Live Application:

https://medicare-viqr.onrender.com/

Production environment variables must be configured securely in the hosting dashboard.

---

## 🔐 Security Considerations

- Environment variables are used for sensitive configuration.
- `.env` is excluded through `.gitignore`.
- Django password validation is enabled.
- CSRF protection is enabled.
- Secure cookies and HTTPS settings are configured for production.
- Admin-only operations use permission checks.
- Database credentials must never be committed to the repository.

---

## 🧪 Testing

The application has undergone manual functional testing for the following workflows:

- Medicine category and manufacturer management.
- Medicine and batch creation.
- Supplier and customer management.
- Purchase creation and stock receiving.
- Duplicate stock receiving prevention.
- Partial and full purchase payments.
- Sales and billing.
- Automatic stock deduction.
- Partial and full sales payments.
- Eligible unpaid sale cancellation and stock restoration.
- Expiry management.
- Sales, purchase, and stock valuation reports.
- Expense management.
- Dashboard summary verification.

---

## 🔮 Future Improvements

- Advanced analytics and graphical reports.
- Barcode scanning for medicines.
- Prescription management.
- Automated low-stock notifications.
- Automated expiry notifications.
- PDF report generation.
- Enhanced audit logs.
- Automated database backup.
- Payment gateway integration.
- Advanced staff activity monitoring.

---

## 👨‍💻 Developer

**Rohan Jagtap**

Computer Science Student | Python & Django Backend Developer

**GitHub:** https://github.com/RohanJagtap431

---

## 📄 Disclaimer

MediCare is an educational and portfolio project developed to demonstrate medical store management workflows.

It is not independently certified for pharmaceutical, GST, prescription, or drug-licensing compliance. Before real-world commercial use, applicable legal, security, financial, and pharmaceutical requirements must be reviewed.

---

## ⭐ Support

If you find this project useful, consider giving the repository a star on GitHub.

**Built with Python, Django, and PostgreSQL.**
