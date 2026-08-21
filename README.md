<div align="center">


<img src="assets/logo.png" alt="CyberSafe Toolkit Logo" width="180">


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


It also provides quick access to frequently used tools.


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
AES-GCM Workflow
Input File
    │
    ▼
Generate / Load Key
    │
    ▼
Generate Random Nonce
    │
    ▼
AES-GCM Encryption
    │
    ├── Ciphertext
    └── Authentication Tag
    │
    ▼
Encrypted Output

During decryption, the authentication tag is verified before the plaintext is accepted.

🔒 Fernet Encryption

Fernet provides authenticated symmetric encryption through a higher-level interface.

Fernet combines:

AES encryption
HMAC-SHA256 authentication
Initialization Vector
Timestamp information
URL-safe encoded keys
Fernet Workflow
Plaintext
    │
    ▼
Fernet Key
    │
    ▼
Authenticated Encryption
    │
    ▼
Fernet Token

Fernet is useful when a simpler authenticated encryption interface is required.

🔑 Asymmetric Encryption

CyberSafe Toolkit supports RSA-2048 asymmetric cryptography.

RSA uses:

2048-bit key size
Public exponent: 65537
OAEP padding
SHA-256
MGF1 with SHA-256

RSA generates a key pair:

RSA Key Pair
     │
     ├── Public Key
     │
     └── Private Key

The public key can be shared, while the private key must remain protected.

🔐 RSA Hybrid Encryption

For large files, RSA is not used to encrypt the complete file directly.

Instead, CyberSafe Toolkit uses a hybrid encryption design.

Encryption Process
                    Random AES Key
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
          AES-GCM                 RSA-OAEP
              │                       │
              ▼                       ▼
       Encrypt File            Encrypt AES Key
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                  Encrypted Package

The AES key encrypts the actual data, while RSA protects the AES key.

RSA-OAEP

OAEP provides randomized padding for RSA encryption.

The design uses:

OAEP
MGF1
SHA-256
Randomized encoding

This prevents deterministic RSA encryption and provides stronger protection than raw RSA encryption.

#️⃣ Hashing & File Integrity

Hashing converts input data into a fixed-length digest.

Supported algorithms include:

Algorithm	Digest Size	Security Status
SHA-256	256-bit	Recommended
SHA-512	512-bit	Recommended
SHA-1	160-bit	Legacy
MD5	128-bit	Legacy / Weak
File Hashing

Large files are processed in chunks instead of loading the entire file into memory.

Typical processing:

File
 │
 ▼
Read Chunk
 │
 ▼
Update Hash
 │
 ▼
Read Next Chunk
 │
 ▼
Continue Until EOF
 │
 ▼
Final Digest

The implementation uses buffered chunks for efficient processing.

Integrity Verification

Integrity verification compares a calculated hash with an expected hash.

Current File Hash
        │
        ▼
      Compare
        │
   ┌────┴────┐
   │         │
 Match    Different
   │         │
   ▼         ▼
UNCHANGED  MODIFIED
🔑 Password Generator

The password generator uses Python's secrets module for cryptographically secure random generation.

Supported Options
Password length
Uppercase letters
Lowercase letters
Numbers
Symbols
Exclusion of ambiguous characters
Generation Algorithm
Select Character Categories
          │
          ▼
Ensure Required Character Types
          │
          ▼
Generate Remaining Characters
          │
          ▼
Secure Shuffle
          │
          ▼
Final Password

The generator uses an operating-system-provided cryptographically secure random source.

🧠 Password Strength Analyzer

The password analyzer evaluates password characteristics using a heuristic scoring system.

The score considers:

Password length
Character variety
Repeated characters
Sequential patterns
Common-password patterns
Character Variety

The analyzer can evaluate:

Lowercase characters
Uppercase characters
Numbers
Symbols
Strength Categories
80 - 100   STRONG
60 - 79    GOOD
40 - 59    MODERATE
20 - 39    WEAK
0  - 19    VERY WEAK

The analyzer also provides recommendations such as:

Increase password length
Add additional character types
Avoid common words
Avoid repeated characters
Avoid sequential patterns

This is a heuristic educational score. It is not a password-cracking-time estimator.

🌐 TCP Port Scanner

CyberSafe Toolkit provides a TCP Connect port scanner.

The scanner uses the operating system's TCP connection mechanism to determine whether a port is accepting connections.

Scanning Algorithm
Target IP / Host
      │
      ▼
Select Port
      │
      ▼
Create TCP Socket
      │
      ▼
Set Timeout
      │
      ▼
connect_ex()
      │
      ├──────────────┐
      │              │
   Success         Failure
      │              │
      ▼              ▼
   OPEN       CLOSED / FILTERED
Port Range

The scanner can scan ports from:

1 - 65535
Timeout

The scanning process uses a short connection timeout to reduce delays when scanning multiple ports.

Common Services

The scanner can identify common services such as:

Port	Service
21	FTP
22	SSH
23	Telnet
25	SMTP
53	DNS
80	HTTP
110	POP3
135	MS RPC
139	NetBIOS
143	IMAP
443	HTTPS
445	SMB
993	IMAPS
995	POP3S
1723	PPTP
3306	MySQL
3389	RDP
5432	PostgreSQL
5900	VNC
8080	HTTP Proxy

Responsible Use: Only scan systems and networks that you own or have explicit permission to assess.

📡 Network Discovery

Network discovery identifies active hosts within an IPv4 network.

The application supports CIDR network notation.

Example:

192.168.1.0/24
Discovery Process
CIDR Network
     │
     ▼
Parse Network
     │
     ▼
Generate Host Addresses
     │
     ▼
Ping Sweep
     │
     ▼
Active Hosts
     │
     ▼
ARP Table Lookup
     │
     ▼
IP + MAC Information
Ping Sweep

On Windows, the application can use:

ping -n 1 -w 300 IP

On Linux:

ping -c 1 -W 1 IP
ARP Discovery

The application can inspect the local ARP table using the operating system's ARP information.

This can provide:

IP address
MAC address

Hosts that block ICMP traffic may not be detected by ping-based discovery.

🗃️ File Quarantine

The quarantine feature allows the user to select a suspicious file and store a quarantine copy.

Quarantine Workflow
Select File
     │
     ▼
Enter Reason
     │
     ▼
Generate Timestamped Name
     │
     ▼
Create Quarantine Copy
     │
     ▼
Record Information in SQLite

The stored information can include:

Original file path
Quarantine path
Reason
Timestamp

The application can preserve file metadata when creating the quarantine copy.

A quarantine copy should not be considered complete malware isolation unless the original file is also removed or execution is otherwise prevented.

📊 Security Reports

CyberSafe Toolkit can generate reports in multiple formats.

TXT

Text reports provide readable operation information including:

Timestamp
Operation
Target
Result
Status
PDF

PDF reports provide a structured presentation suitable for documentation and printing.

The PDF generator uses ReportLab.

CSV

CSV reports are useful for:

Data analysis
Spreadsheet processing
Filtering
External reporting
📝 Operation History

CyberSafe Toolkit records security-related operations locally.

The history system can store:

Operation
Target
Result
Status
Timestamp

Users can search and filter historical records.

Filtering

Filtering can be performed based on:

Operation
Target
Result

Search operations are designed to be case-insensitive.

🗄️ Database Architecture

CyberSafe Toolkit uses SQLite for local persistence.

The documented database structure includes tables for:

Security Records
security_records
├── id
├── operation
├── target
├── result
├── timestamp
└── status
Hash Records
hash_records
├── id
├── file_path
├── file_name
├── sha256_hash
└── created_at
Scan History
scan_history
├── id
├── target
├── scan_type
├── open_ports
├── services
└── timestamp
Quarantine
quarantine
├── id
├── original_path
├── quarantined_path
├── reason
└── timestamp
🏗️ Application Architecture

CyberSafe Toolkit follows a layered desktop application architecture.

┌───────────────────────────────────────────┐
│             Presentation Layer            │
│                                           │
│              CustomTkinter                │
│              Desktop GUI                  │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│             Application Logic             │
│                                           │
│ Encryption | Hashing | Passwords          │
│ Network Scanning | Quarantine | Reports   │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│              Data Persistence             │
│                                           │
│                  SQLite                   │
└───────────────────────────────────────────┘
🧵 Threading & Responsiveness

Long-running operations such as:

Port scanning
Network discovery
File processing
Report generation

can be executed away from the main UI event loop.

The purpose is to keep the interface responsive while background operations are running.

The GUI remains responsible for:

Rendering
User interaction
Status updates
Displaying results
🎨 User Interface Design

CyberSafe Toolkit uses a dark cybersecurity-inspired visual design.

Main Colors
Purpose	Color
Background	#0d1117
Surface	#161b22
Elevated Surface	#1c2128
Primary Accent	#00d4ff
Success	#00ff88
Danger	#ff4757
Warning	#ffd700
Primary Text	#ffffff
Secondary Text	#c9d1d9
Muted Text	#8b949e

The interface includes a responsive sidebar, scrollable content areas, status indicators, and custom notifications.

🔔 Notifications & Message Boxes

The application provides custom notification dialogs for common events.

Examples include:

Operation completed
Encryption successful
Key generated
Invalid key
Missing file
Scan completed
Operation failed

Notifications are designed to provide immediate feedback without requiring the user to inspect logs.

🖼️ Logo & Icon System

The project includes:

assets/
├── logo.png
└── icon.ico

The logo can be used throughout the interface, including:

Sidebar
Header
Notifications
Application branding

The icon is used for the application and Windows executable.

📱 Responsive Interface

The interface adapts to different window sizes through:

Responsive sidebar sizing
Scrollable content
Dynamic layout management
Minimum and maximum interface dimensions

This allows the application to remain usable across different desktop resolutions.

👥 Team Page

CyberSafe Toolkit includes a dedicated project/team section.

The team page can present:

Team members
Roles
Descriptions
Skills
Project information

This section is intended to present the project team and development information.

💾 Backup & Restore

Backup and restore functionality should be documented according to the exact implementation available in the current build.

If enabled in a future version, the recommended backup scope includes:

SQLite database
Configuration
Security history
Hash records
Scan history
Quarantine metadata

A secure backup design should also consider:

Backup integrity
Access control
Encryption
Backup versioning
Restore validation

The exact backup behavior should not be assumed unless it is implemented and enabled in the current release.

⚙️ Technology Stack
Technology	Purpose
Python 3.8+	Core programming language
CustomTkinter 5.2.2	Graphical User Interface
cryptography 42.0.5	Cryptographic operations
Pillow 10.2.0	Image processing
ReportLab 4.1.0	PDF reports
SQLite	Local database
hashlib	Hashing
secrets	Secure random generation
socket	TCP networking
ipaddress	Network processing
subprocess	System commands
threading	Background operations
shutil	File operations
💻 System Requirements
Windows

Supported:

Windows 10
Windows 11
Linux

Compatible Linux distributions may run the Python version of the application if the required dependencies are installed.

Python
Python 3.8+
📦 Installation
Clone the Repository
git clone https://github.com/DiaaElokda/CyberSafe-Toolkit.git

Navigate into the project:

cd CyberSafe-Toolkit

Install dependencies:

pip install -r requirements.txt

Run the application:

python main.py
🪟 Windows Executable

A compiled Windows executable can be distributed through GitHub Releases.

Users can download the latest release without installing Python.

Release Page

https://github.com/DiaaElokda/CyberSafe-Toolkit/releases

📸 Screenshots
Dashboard

Symmetric Encryption

Asymmetric Encryption

Hashing

Password Generator

📚 Documentation

For the complete technical documentation, including detailed algorithms, workflows, database structure, security considerations, limitations, and feature explanations:

👉 Read the Full Documentation

🔬 Security Considerations

CyberSafe Toolkit is designed as a practical cybersecurity learning and assessment project.

Security considerations include:

Use of cryptographically secure random generation
Authenticated encryption
RSA-OAEP padding
Hash-based integrity verification
Local operation logging
Input validation
Network scan authorization
Error handling

However, security depends on correct implementation, configuration, key management, and responsible usage.

⚠️ Limitations

CyberSafe Toolkit is an educational and practical cybersecurity toolkit. It should not be considered a replacement for enterprise-grade security products.

Known limitations include:

TCP Connect scanning is not equivalent to advanced stealth scanning.
ICMP-based discovery may miss hosts that block ping.
Password strength scoring is heuristic.
MD5 and SHA-1 are legacy algorithms.
File quarantine behavior depends on the implemented file-handling workflow.
Cryptographic security depends on proper key management.
Local SQLite storage should not be treated as a replacement for enterprise security logging.
Network scan results depend on network configuration and firewall behavior.
🚀 Future Improvements

Potential future improvements include:

Advanced network scanning
Improved host discovery
Additional cryptographic algorithms
Secure key management
Enhanced quarantine isolation
Backup and restore
Improved reporting
More detailed logging
Automated security checks
Multi-user support
Improved cross-platform support
Improved executable packaging
Digital signature for releases
🛡️ Responsible Use

CyberSafe Toolkit includes security assessment functionality such as port scanning and network discovery.

Use these features only against:

Systems you own
Personal lab environments
Authorized penetration-testing targets
Networks where you have explicit permission to perform security testing

Unauthorized scanning, testing, or access may violate laws, policies, or terms of service.

This project is intended for:

Educational, Defensive, and Authorized Security Testing Purposes.

👨‍💻 Author
Diaa Elokda

Cybersecurity Student & IT Support / Networking Enthusiast

GitHub:

https://github.com/DiaaElokda

Project:

https://github.com/DiaaElokda/CyberSafe-Toolkit

📄 License

This project is licensed under the MIT License.

See the LICENSE file for more information.

<div align="center">
🛡️ CyberSafe Toolkit v2.0.0

Built for Cybersecurity Education & Authorized Security Testing

⭐ If you find this project useful, consider giving it a star.

</div> ```
