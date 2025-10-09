# 🦁 Macan Conquer - Professional Windows Toolkit

Macan Conquer is a professional toolkit for maintenance, diagnostics, and repair of Windows 10/11 operating systems.

Developed with Python and PySide6, it features a modern interface with Administrator-level functionality.

---

## ✨ Key Features

### 🧩 System Repair & Integrity
- **System File Checker (sfc /scannow)** — Scans and restores corrupted Windows system files.
- **DISM Restore Health** — Repairs a Windows system image using Deployment Image Servicing and Management.
- **Scan Disk (chkdsk C:)** — Checks for file system errors on the primary drive.
- **Defrag / Optimize Drive (C:)** — Optimizes storage performance (HDD/SSD).

### 🧹 System Cleanup
- **Clear Temporary Files** — Delete user temporary files (%TEMP%).
- **Clear Windows Update Cache** — Clear corrupted Windows Update cache.
- **Reset Icon Cache** — Fix corrupted or missing icons.

### ⚙️ Additional Applications
Run included external utilities:
- **Little Registry Cleaner.exe** — Clean invalid registry entries.
- **Little Startup Manager.exe** — Manage programs that run at startup.
- **Little Uninstall Manager.exe** — Uninstall applications with full control.

### 🔒 Advanced Boot Options
- **Boot to Safe Mode (Minimal)** — Set the system to boot into Safe Mode on restart.
- **Disable Safe Mode Boot** — Return the boot configuration to normal mode.

---

## 🖥️ Interface
The application displays:
- Header with application logo and name
- Function groups in a card-style layout
- Console log for each system activity
- Menu bar with File, Help, and About options

---

## 📸 Screenshot
<img width="487" height="698" alt="Screenshot 2025-10-09 135312" src="https://github.com/user-attachments/assets/089c835f-7aa7-47e3-99ae-1e3d5925d2dc" />
<img width="520" height="710" alt="Screenshot 2025-10-09 141017" src="https://github.com/user-attachments/assets/e4fda4a0-7ca1-4d20-9800-9a64f92f2bcb" />
<img width="598" height="529" alt="Screenshot 2025-10-09 141000" src="https://github.com/user-attachments/assets/a5b9f6a6-97cf-4700-9ec8-1becfb243fb4" />




## 🧠 Technologies Used
- Python 3.9+
- PySide6 (Qt for Python)
- ctypes, subprocess, shutil, tempfile

---

🧰 License
© 2025 — Danx Exodus
Part of the Macan Angkasa ecosystem
License: MIT & Independent Software License (Macan Angkasa Ecosystem)

📘 Important Note
This application must be run as an Administrator to function properly.
Use with full responsibility as some functions access sensitive Windows system components.

🧾 About
Macan Conquer is developed by Danx Exodus as part of the Macan Angkasa ecosystem,
which focuses on developing professional system software and tools for Windows.
