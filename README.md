# 🛡️ CyberSafe Toolkit v2.1

<div align="center">

![CyberSafe Toolkit](assets/logo.png)

**A Comprehensive Cybersecurity Desktop Application**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-cyan.svg)](https://github.com/yourusername/cybersafe-toolkit/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-orange.svg)]()
[![GitHub stars](https://img.shields.io/github/stars/yourusername/cybersafe-toolkit?style=social)]()

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Security Features](#-security-features)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)
- [Disclaimer](#-disclaimer)

---

## 📖 Overview

CyberSafe Toolkit is a **comprehensive cybersecurity desktop application** that consolidates essential security tools into a single, unified interface. Built with Python and CustomTkinter, it provides enterprise-grade security features with an intuitive dark-themed UI.

### 🎯 Purpose

| Goal | Description |
|------|-------------|
| **Education** | Teach fundamental cybersecurity concepts |
| **Practicality** | Provide real-world security tools |
| **Integration** | Combine multiple utilities in one app |
| **Accessibility** | Easy-to-use interface for all levels |

### 👥 Target Audience

- 🎓 Cybersecurity Students
- 💼 IT Professionals
- 🔬 Security Researchers
- 📚 Educators & Trainers

---

## ✨ Features

### 🔐 Encryption

| Feature | Algorithm | Description |
|---------|-----------|-------------|
| **Symmetric** | AES-256-GCM | Authenticated encryption |
| **Symmetric** | Fernet | Simple encryption with HMAC |
| **Asymmetric** | RSA-2048 | Public/private key encryption |
| **Hybrid** | AES+RSA | Large file encryption |

### 🔒 Hashing & Integrity

| Algorithm | Output Size | Use Case |
|-----------|-------------|----------|
| SHA-256 | 256 bits | File integrity |
| SHA-512 | 512 bits | High security |
| MD5 | 128 bits | Legacy compatibility |
| SHA-1 | 160 bits | Quick verification |

### 📝 Password Tools

- **Generator**: Cryptographically secure passwords (4-128 chars)
- **Analyzer**: Multi-factor strength scoring
- **Character Sets**: Uppercase, lowercase, digits, symbols
- **Ambiguous Exclusion**: Remove confusing characters

### 🌐 Network Tools

- **Port Scanner**: TCP connect scanning (1-65535)
- **Service Detection**: 20+ common services
- **Network Discovery**: Ping sweep + ARP
- **Real-time Progress**: Live scan updates

### 🚫 File Quarantine

- **Isolation**: Copy suspicious files to secure location
- **Tracking**: Database records with reasons
- **Metadata**: Preserved via `shutil.copy2`

### 📄 Reports

| Format | Best For |
|--------|----------|
| TXT | Quick viewing |
| PDF | Professional documents |
| CSV | Data analysis |

---

## 📸 Screenshots

### Dashboard


text

### Sidebar Navigation


text

---

## 🚀 Installation

### Prerequisites

bash
# Check Python version (3.8+)
python --version

# Update pip
python -m pip install --upgrade pip
Step-by-Step Installation
bash
# 1. Clone the repository
git clone https://github.com/yourusername/cybersafe-toolkit.git
cd cybersafe-toolkit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place assets (optional)
# - assets/logo.png (500x500 recommended)
# - assets/icon.ico (32x32 or 64x64)

# 4. Run the application
python main.py
Dependencies
Package	Version	Purpose
customtkinter	5.2.2	GUI framework
cryptography	42.0.5	Encryption
Pillow	10.2.0	Image processing
reportlab	4.1.0	PDF generation
💻 Usage
Quick Start
Launch the application

Select a module from sidebar

Follow on-screen instructions

View results in real-time

Common Operations
Encrypt a File
text
1. Click "Symmetric Encryption"

2. Select encryption method (AES-GCM/Fernet)

3. Generate or enter key

4. Select file

5. Click "Encrypt File"

Scan Network

text

1. Click "Port Scanner"

2. Enter target IP

3. Set port range

4. Click "Start Scan"

5. View results

Generate Password

text

1. Click "Password Generator"

2. Set length and options

3. Click "Generate Password"

4. Copy to clipboard

📁 Project Structure

text
cybersafe-toolkit/
│
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md                # Documentation
├── LICENSE                  # License file
│
├── core/
│   ├── __init__.py
│   ├── app.py               # Main application class
│   ├── config.py            # Configuration management
│   ├── database.py          # Database (Singleton)
│   ├── encryption.py        # Encryption algorithms
│   └── logger.py            # Logging system
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py           # Navigation sidebar
│   ├── dashboard.py         # Dashboard page
│   ├── components.py        # Reusable components
│   └── windows.py           # Message windows
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py           # Helper functions
│   ├── validators.py        # Input validation
│   └── security.py          # Security utilities
│
├── config/
│   └── settings.json        # App settings
│
├── assets/
│   ├── logo.png             # Application logo
│   └── icon.ico             # Application icon
│
└── data/                    # Runtime data (auto-created)
    ├── database/
    ├── quarantine/
    ├── reports/
    └── logs/
🛠️ Technologies

Core Stack

Technology	Version	Usage

Python	3.8+	Primary language

CustomTkinter	5.2.2	Modern GUI

SQLite	Built-in	Database

Cryptography	42.0.5	Security

Design Patterns

Pattern	Implementation

Singleton	Database, Logger

Modular	Separate files per feature

Observer	UI updates

Factory	Encryption creation

Architecture

text
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (CustomTkinter GUI)              │
├─────────────────────────────────────┤
│         Business Logic Layer        │
│    (Core Modules)                   │
├─────────────────────────────────────┤
│         Data Access Layer           │
│    (SQLite Database)                │
└─────────────────────────────────────┘
🔒 Security Features

Cryptographic Standards

Feature	Algorithm	Key Size

Symmetric Encryption	AES-256-GCM	256 bits

Simple Encryption	Fernet	128+128 bits

Asymmetric	RSA-2048	2048 bits

Hashing	SHA-256/512	256/512 bits

Padding	OAEP-SHA256	-

Secure Random Generation

All random values use secrets module:

Encryption keys

Nonces

Passwords

Initialization vectors

Best Practices
✅ No plaintext key storage

✅ Authenticated encryption

✅ Input validation

✅ Error handling

✅ Secure file operations

🤝 Contributing
How to Contribute
Fork the repository

Create a feature branch

bash
git checkout -b feature/AmazingFeature
Commit your changes

bash
git commit -m 'Add some AmazingFeature'
Push to the branch

bash
git push origin feature/AmazingFeature
Open a Pull Request

Code Style
Follow PEP 8

Use type hints

Document all functions

Write meaningful commit messages

📄 License
This project is for educational purposes only.

text
EDUCATIONAL USE LICENSE

Permission is granted to use this software for educational purposes.
Commercial use is prohibited without explicit permission.

THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.

⚠️ Disclaimer
IMPORTANT: This software is intended for educational and authorized testing purposes only.

You must NOT use this software to:

Access systems without authorization

Perform illegal activities

Compromise security of others

Violate any laws or regulations

Always ensure you have:

✅ Written permission before testing

✅ Authorization from system owners

✅ Compliance with local laws

📞 Contact
Channel	Details
📧 Email	diaamaherelokda@gmail.com

💬 GitHub	github.com/DiaaElokda

🌐 Website	(https://diaaelokda.github.io/Portfolio/)

⭐ Support
If you find this project useful, please:

⭐ Star the repository

🔄 Share with others

🐛 Report issues

💡 Suggest improvements

<div align="center">
Made with ❤️ by CyberSafe Team

© 2026 CyberSafe Toolkit v2.1 - All Rights Reserved

</div>
