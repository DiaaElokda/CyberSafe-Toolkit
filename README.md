import pypandoc, os

readme = r'''<div align="center">

<img src="assets/logo.png" alt="CyberSafe Toolkit Logo" width="180">

# 🛡️ CyberSafe Toolkit v2.0

### Desktop Cybersecurity Toolkit

A practical cybersecurity toolkit built with Python and CustomTkinter, combining encryption, hashing, password security, network scanning, file quarantine, security reports, and operation history in one desktop application.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6feb)](https://github.com/TomSchimansky/CustomTkinter)
[![Cryptography](https://img.shields.io/badge/Cryptography-AES%20%7C%20RSA%20%7C%20Fernet-00d4ff)](https://cryptography.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Version](https://img.shields.io/badge/Version-2.0.0-success)](https://github.com/DiaaElokda/CyberSafe-Toolkit/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

# 📖 Overview

**CyberSafe Toolkit** is a desktop cybersecurity application designed to provide a collection of practical security utilities through a single, easy-to-use graphical interface.

The project combines cryptographic tools, password security utilities, network assessment features, file quarantine, integrity verification, security reports, and operation history.

It was developed as a practical cybersecurity project to demonstrate the implementation and integration of common defensive security techniques.

---

# ✨ Features

## 🔐 Cryptography

- AES-GCM symmetric encryption
- Fernet authenticated encryption
- RSA-2048 asymmetric encryption
- Hybrid RSA + AES-GCM encryption
- RSA-OAEP with SHA-256
- Secure random key generation
- File encryption and decryption workflows

## #️⃣ Hashing & File Integrity

- SHA-256
- SHA-512
- SHA-1
- MD5
- File hashing
- File integrity comparison
- Large-file processing using chunks
- Hash verification

> **Security Note:** MD5 and SHA-1 are included mainly for compatibility and educational purposes. They should not be used for new security-critical applications.

## 🔑 Password Security

- Cryptographically secure password generation
- Configurable password length
- Uppercase characters
- Lowercase characters
- Numbers
- Symbols
- Ambiguous-character exclusion
- Password strength analysis
- Security recommendations

## 🌐 Network Security

- TCP Connect port scanner
- Port range scanning
- Common service identification
- IPv4 network discovery
- ICMP ping sweep
- ARP table discovery
- Background scanning
- Real-time scan progress

## 🗃️ File Quarantine

- Select suspicious files
- Store quarantine copies
- Record quarantine reason
- Track original and quarantine paths
- Timestamped quarantine records

> Quarantine functionality should not be considered a complete malware containment solution unless the original file is actually removed or otherwise prevented from execution.

## 📊 Security Reports

Generate security reports in:

- TXT
- PDF
- CSV

Reports can contain operation details, targets, results, timestamps, and security status.

## 📝 Operation History

CyberSafe Toolkit maintains local operation records using SQLite.

The history system supports:

- Operation tracking
- Target tracking
- Results
- Status
- Timestamps
- Search
- Filtering

## 🗄️ Local Data Storage

The application uses SQLite to maintain local security-related records, including:

- Security operations
- Hash records
- Network scan history
- Quarantine records

---

# 🖥️ User Interface

CyberSafe Toolkit uses a modern dark-themed graphical interface based on CustomTkinter.

The interface contains:

- Navigation sidebar
- Application logo
- Application title and version
- Main content area
- Dashboard
- Security tools
- Status bar
- Notifications
- Scrollable content areas
- Team information

---

# 📊 Dashboard

The Dashboard provides a quick overview of application activity.

It can display security statistics such as:

- Total Operations
- Quarantined Files
- Open Ports Found

### Quick Actions

- Encrypt File
- Generate Password
- Scan Network
- Generate Report
- Generate RSA Keys
- Hash File

The dashboard also provides security tips and general recommendations.

---

# 🔐 Symmetric Encryption

CyberSafe Toolkit provides symmetric encryption using modern authenticated encryption techniques.

## AES-GCM

AES-GCM provides:

- Confidentiality
- Integrity
- Authentication

The intended configuration uses:

- AES
- 256-bit key
- 12-byte nonce
- 128-bit authentication tag

The encrypted data can be represented as:

```text
Nonce + Authentication Tag + Ciphertext
