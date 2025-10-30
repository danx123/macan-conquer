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
<img width="1080" height="1920" alt="post-github-macan-conquer" src="https://github.com/user-attachments/assets/78c450aa-dea6-4e50-b8ca-2d9b6a10d35c" />

---
📝 Changelog v3.5.0

🚀 New Features & Capabilities
Introduced "Advanced System Tweaks" Module
A new functional group has been added, providing direct access to common performance and service tweaks:

- Disable Superfetch/SysMain: Implemented a function to safely stop and disable the SysMain (formerly Superfetch) service to mitigate high disk/RAM usage on specific systems.
- Disable Windows Search: Provides a function to stop and disable the WSearch (Windows Search) service, addressing indexing issues that cause constant CPU/disk utilization.
- Cleanup Driver Store (DISM /ResetBase): Integrated an advanced DISM function (/StartComponentCleanup /ResetBase) to purge superseded drivers and components from the Component Store (WinSxS), which can result in significant disk space recovery.

✨ UI/UX Enhancements
- Upgraded System Information Dashboard
The "System Information" dialog has been overhauled for superior data visualization:
Dynamic Progress Bars: Static text labels for CPU, RAM, and Disk (C:) utilization have been replaced with real-time, dynamic QProgressBar widgets.
Enhanced Data Readability: The RAM and Disk progress bars now display rich contextual information, such as (Used / Total GB), in addition to the percentage value.
Visual Consistency: The new progress bar styling has been fully integrated into the application's dark theme for a seamless and professional appearance.

- M-zS Documentation & Miscellaneous
Updated Help Content: The internal documentation ("Help Content") has been revised to reflect the addition of the "Advanced System Tweaks" module, including descriptions and warnings for each new function.
Dependency Management: The QProgressBar import was added to support the new dashboard UI.
Code Refactoring: The update logic within the SystemInfoDialog was refactored to populate the QProgressBar data structures instead of the previous QLabel text.

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
