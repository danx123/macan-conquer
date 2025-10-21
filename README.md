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
<img width="852" height="632" alt="Screenshot 2025-10-22 020535" src="https://github.com/user-attachments/assets/1c1cf200-f977-40e4-afaf-6a4dd4e0f9d1" />
<img width="1080" height="1920" alt="macan-conquer-v3" src="https://github.com/user-attachments/assets/fbf2b3c4-fd74-4922-9142-bd7a4e402061" />



---
📝 Changelog v3.0.0
- System Information (Enhanced): The "System Information" dialog now also displays real-time disk (C:) usage, in addition to OS, CPU, RAM, and Uptime.

- New Group: Network Repair: Added a new group specifically for fixing network problems.

- Flush DNS Cache: Clears the DNS cache (very useful if a website is inaccessible).

- Reset TCP/IP: Resets the TCP/IP stack to default settings.

- Reset Winsock: Fixes connectivity issues caused by Winsock catalog corruption.

- New Group: Advanced Tools & Shortcuts: Renamed and expanded "Advanced Boot" group:

Reboot to Advanced Options: Restarts the computer directly to the advanced startup menu (recovery mode).

- Event Viewer: Shortcut to open Event Viewer.

- Device Manager: Shortcut to open Device Manager.

- Services: Shortcut to open the Services console.

- Additional Features:
Disk Cleanup: Added a shortcut to open Windows' built-in Disk Cleanup in the "System Cleanup" group.
File Menu (Enhanced): Added "Log Off" and "Hibernate" options to the File menu, in addition to Restart and Shutdown.

---


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
