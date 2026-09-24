# KYC Document Expiry Monitor for Bank Branches

## 📌 Project Overview

The **KYC Document Expiry Monitor** is a Python-based web application designed to help bank branches monitor customer KYC documents and identify documents that are expired or approaching expiry.

The system helps bank staff track customer KYC status, identify pending re-KYC cases, and generate branch-wise reports.

## 🎯 Objectives

* Monitor customer KYC document expiry dates.
* Identify expired and soon-to-expire documents.
* Maintain customer KYC information securely.
* Schedule re-KYC activities.
* Generate branch-wise KYC reports.
* Provide a simple dashboard for bank staff.

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Database

* MySQL

### Development Tools

* Visual Studio Code
* Git
* GitHub

## ⭐ Main Features

* 🔐 User Login
* 👤 Customer Management
* 📄 KYC Document Management
* 📅 KYC Expiry Date Monitoring
* ⚠️ Expiry Alerts
* 🔄 Re-KYC Status Tracking
* 📊 Dashboard
* 📑 Reports
* 🏦 Branch-wise Customer Reports
* 🔍 Customer Search
* 📱 Responsive Web Interface

## 🏗️ System Workflow

```text
Customer Data
     ↓
Data Validation
     ↓
Date Format Conversion
     ↓
KYC Expiry Calculation
     ↓
Expiry Detection
     ↓
KYC Status Update
     ↓
Re-KYC Scheduling
     ↓
Branch-wise Reports
     ↓
Bank Staff / Admin
```

## 📂 Project Structure

```text
KYC-Monitor/
│
├── app.py
├── database.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── customers.html
│   ├── add_customer.html
│   ├── customer_details.html
│   └── reports.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

## 🗄️ Database

The application uses **MySQL** to store customer and KYC information.

Example database:

```text
Database Name: kyc_monitor
```

Important data may include:

* Customer ID
* Customer Name
* Account Number
* Branch
* Date of Birth
* KYC Document Type
* KYC Issue Date
* KYC Expiry Date
* KYC Status
* Re-KYC Date

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/kyc-monitor.git
```

### 2. Open the Project

```bash
cd kyc-monitor
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

For Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
venv\Scripts\Activate.ps1
```

### 5. Install Required Packages

```bash
pip install -r requirements.txt
```

## 🗃️ MySQL Configuration

Create the database in MySQL:

```sql
CREATE DATABASE kyc_monitor;
```

Update the MySQL connection details in your Python database configuration file.

Example:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "kyc_monitor"
```

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

You should see:

```text
Serving Flask app 'app'
Debug mode: on
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

## 📊 Reports

The reports page can be accessed using:

```text
http://127.0.0.1:5000/reports
```

The reports section helps bank staff view KYC information and monitor customer records based on their KYC status.

## 🔐 Security

The project includes a login system to restrict access to authorized users.

For a production system, additional security features such as:

* Password hashing
* Role-based access control
* Secure database credentials
* HTTPS
* Session security
* Audit logs

can be implemented.

## 🚀 Future Enhancements

* 📱 SMS alerts for customers
* 📧 Email notifications
* 🔔 Automatic expiry reminders
* 📊 Advanced analytics dashboard
* 📄 Secure document upload
* 👥 Role-based login
* ☁️ Cloud database integration
* 📈 KYC trend analysis
* 🤖 Automatic re-KYC scheduling

## 📸 Project Pages

The application contains pages such as:

* Login
* Dashboard
* Customer Details
* Add Customer
* KYC Monitoring
* Reports

## 👨‍💻 Project Purpose

This project was developed as an academic/learning project to demonstrate how **Python, Flask, MySQL, HTML, CSS, and JavaScript** can be combined to develop a real-world banking compliance application.

## 📄 Conclusion

The **KYC Document Expiry Monitor** provides a simple digital solution for monitoring KYC document expiry and managing re-KYC activities. It reduces manual tracking and helps bank staff identify customers who require KYC updates.

---

### 👩‍💻 Developed By

**Syamala Katta**

**Project:** KYC Document Expiry Monitor for Bank Branches

**Technology:** Python | Flask | MySQL | HTML | CSS | JavaScript
