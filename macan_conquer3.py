# Nama File: macan_conquer.py (Versi Profesional dengan Menu)
# Deskripsi: Tools untuk maintenance dan perbaikan Windows 10/11.
# Dibuat dengan Python dan PySide6.
#
# Cara Menjalankan:
# 1. Install PySide6: pip install pyside6
# 2. Pastikan file "Little Registry Cleaner.exe", "Little Startup Manager.exe",
#    dan "Little Uninstall Manager.exe" berada di folder yang sama dengan script ini
#    saat menjalankan sebagai .py, atau di direktori root saat mem-bundle dengan PyInstaller.
# 3. Jalankan script ini dengan hak Administrator.
#    (Klik kanan file -> Run as administrator)

import sys
import os
import ctypes
import subprocess
import shutil
import tempfile

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QTextEdit, QMessageBox, QHBoxLayout, QLabel, QGridLayout, QGroupBox,
    QDialog, QScrollArea # Tambahan untuk dialog help
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction # Tambahan untuk menu action

class MacanConquerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Conquer - Professional Windows Toolkit")
        self.setGeometry(100, 100, 450, 400)
        #self.setMinimumSize(700, 750)
        self.setWindowIcon(self.get_icon())

        self.process = None
        self.is_running = False
        
        self.init_ui()
        self.add_log("Selamat datang di Macan Conquer! Aplikasi siap digunakan.")
        self.add_log("Pastikan Anda menjalankan sebagai Administrator untuk fungsionalitas penuh.")

    def init_ui(self):
        """Membangun semua elemen antarmuka pengguna."""
        
        # --- [BARU] Membuat Menu Bar ---
        self._create_menu_bar()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)

        # --- Header ---
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        pixmap = QPixmap(self.get_icon_path())
        logo_label.setPixmap(pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_container = QVBoxLayout()
        title_label = QLabel("Macan Conquer")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel("Professional Windows Toolkit")
        subtitle_label.setObjectName("SubtitleLabel")
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        title_container.setSpacing(0)

        header_layout.addWidget(logo_label)
        header_layout.addSpacing(10)
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # --- Grup Tombol ---
        self.button_widgets = []
        self.create_system_repair_group()
        self.create_cleanup_group()
        self.create_external_tools_group()
        self.create_advanced_boot_group()

        # --- Output Console ---
        log_label = QLabel("Log Aktivitas:")
        log_label.setObjectName("GroupTitle")
        self.main_layout.addWidget(log_label)
        
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setObjectName("OutputConsole")
        self.main_layout.addWidget(self.output_console)

    def _create_menu_bar(self):
        """Membuat File Menu dan Help Menu."""
        menu_bar = self.menuBar()

        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")

        restart_action = QAction("Restart Windows", self)
        restart_action.triggered.connect(self._restart_windows)
        file_menu.addAction(restart_action)

        shutdown_action = QAction("Shutdown Windows", self)
        shutdown_action.triggered.connect(self._shutdown_windows)
        file_menu.addAction(shutdown_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Help Menu ---
        help_menu = menu_bar.addMenu("&Help")

        help_content_action = QAction("Help Content", self)
        help_content_action.triggered.connect(self._show_help_content)
        help_menu.addAction(help_content_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
        
    def create_button(self, text, func):
        """Helper untuk membuat dan menyimpan tombol."""
        button = QPushButton(text)
        button.clicked.connect(func)
        self.button_widgets.append(button)
        return button

    def create_system_repair_group(self):
        group_box = QGroupBox("Perbaikan Sistem & Integritas")
        group_box.setObjectName("FunctionGroup")
        layout = QGridLayout()
        layout.addWidget(self.create_button("System File Checker (sfc /scannow)", self.run_sfc), 0, 0)
        layout.addWidget(self.create_button("DISM Restore Health", self.run_dism), 0, 1)
        layout.addWidget(self.create_button("Scan Disk (chkdsk C:)", self.run_chkdsk), 1, 0)
        layout.addWidget(self.create_button("Defrag / Optimize Drive (C:)", self.run_defrag), 1, 1)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def create_cleanup_group(self):
        group_box = QGroupBox("Pembersihan Sistem")
        group_box.setObjectName("FunctionGroup")
        layout = QGridLayout()
        layout.addWidget(self.create_button("Clear Temporary Files", self.clear_temp_files), 0, 0)
        layout.addWidget(self.create_button("Clear Windows Update Cache", self.clear_update_cache), 0, 1)
        layout.addWidget(self.create_button("Reset Icon Cache", self.reset_icon_cache), 1, 0)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)
        
    def create_external_tools_group(self):
        group_box = QGroupBox("Aplikasi Tambahan")
        group_box.setObjectName("FunctionGroup")
        layout = QHBoxLayout()
        layout.addWidget(self.create_button("Registry Cleaner", self.run_registry_cleaner))
        layout.addWidget(self.create_button("Startup Manager", self.run_startup_manager))
        layout.addWidget(self.create_button("Uninstall Manager", self.run_uninstall_manager))
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def create_advanced_boot_group(self):
        group_box = QGroupBox("Opsi Boot Lanjutan")
        group_box.setObjectName("FunctionGroup")
        layout = QHBoxLayout()
        layout.addWidget(self.create_button("Boot to Safe Mode (Minimal)", self.boot_to_safe_mode))
        layout.addWidget(self.create_button("Disable Safe Mode Boot", self.disable_safe_mode))
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    # --- [ FUNGSI BARU UNTUK MENU ACTION ] ---
    def _confirm_and_shutdown(self, command, message):
        reply = QMessageBox.question(self, "Konfirmasi",
                                     message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                subprocess.run(["shutdown", command, "/t", "0"], check=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menjalankan perintah: {e}")

    def _restart_windows(self):
        self._confirm_and_shutdown("/r", "Apakah Anda yakin ingin me-restart komputer sekarang?")

    def _shutdown_windows(self):
        self._confirm_and_shutdown("/s", "Apakah Anda yakin ingin mematikan komputer sekarang?")

    def _show_about_dialog(self):
        about_text = """
<b>Macan Conquer - Professional Windows Toolkit</b>

Macan Conquer adalah Toolkit Windows profesional yang dirancang untuk mempermudah dan mempercepat proses maintenance (pemeliharaan), diagnosa, dan perbaikan pada sistem operasi Windows 10 dan Windows 11.

Aplikasi ini dikembangkan menggunakan Python dan framework PySide6, menjamin antarmuka yang modern, stabil, dan mudah digunakan, sambil tetap menyediakan fungsionalitas tingkat Administrator yang kuat.

<b>Peringatan:</b> Karena fungsionalitasnya yang mendalam dan melibatkan komponen sistem kritis, Macan Conquer wajib dijalankan dengan hak akses Administrator.

© 2025 - Danx Exodus - Macan Angkasa
        """
        QMessageBox.about(self, "About Macan Conquer", about_text)

    def _show_help_content(self):
        help_content = """
Panduan Penggunaan Macan Conquer - Professional Windows Toolkit
============================================================
Macan Conquer adalah alat bantu komprehensif untuk memelihara dan memperbaiki sistem operasi Windows 10/11. Untuk fungsionalitas penuh, pastikan Anda menjalankan aplikasi ini sebagai Administrator.

I. Grup: Perbaikan Sistem & Integritas
---------------------------------------------
Fungsi-fungsi ini sangat penting untuk memeriksa dan memperbaiki kerusakan file sistem Windows dan kondisi disk.

- System File Checker (sfc /scannow):
  Memindai dan memulihkan file sistem Windows yang hilang atau rusak. Ini adalah langkah pertama dalam perbaikan sistem.

- DISM Restore Health:
  Menggunakan Deployment Image Servicing and Management (DISM) untuk memperbaiki kerusakan pada image sistem Windows. Ini seringkali diperlukan jika sfc /scannow gagal.

- Scan Disk (chkdsk C:):
  Memindai disk C: Anda untuk kesalahan sistem file (hanya mode read-only). Untuk perbaikan penuh, Anda perlu menjalankan chkdsk C: /f /r secara manual di CMD Admin (memerlukan restart).

- Defrag / Optimize Drive (C:):
  Mengoptimalkan drive C: (Defrag untuk HDD, TRIM untuk SSD) untuk meningkatkan kecepatan akses data.

II. Grup: Pembersihan Sistem
----------------------------------
Fungsi-fungsi ini membantu mengosongkan ruang disk dan menyelesaikan masalah visual atau cache yang mengganggu.

- Clear Temporary Files:
  Menghapus semua file dan folder di direktori Temp pengguna (%TEMP%) untuk membersihkan file sampah.

- Clear Windows Update Cache:
  Memperbaiki masalah di mana Windows Update macet atau gagal mengunduh dengan membersihkan cache-nya.

- Reset Icon Cache:
  Menyelesaikan masalah ikon yang salah tampil, rusak, atau tidak muncul dengan benar di Windows.

III. Grup: Aplikasi Tambahan
-----------------------------------
Tombol-tombol ini berfungsi sebagai launcher cepat untuk menjalankan aplikasi eksternal. PENTING: File EXE aplikasi tambahan tersebut harus berada di folder yang sama dengan Macan Conquer.

- Registry Cleaner (Little Registry Cleaner.exe):
  Membantu membersihkan entry registri yang tidak valid.

- Startup Manager (Little Startup Manager.exe):
  Memudahkan Anda mengelola program yang berjalan saat Windows mulai.

- Uninstall Manager (Little Uninstall Manager.exe):
  Menyediakan kontrol yang lebih baik dalam menghapus instalasi program.

IV. Grup: Opsi Boot Lanjutan
-------------------------------------
Fungsi ini digunakan untuk mengatur konfigurasi boot sistem secara permanen (hingga diubah kembali).

- Boot to Safe Mode (Minimal):
  Mengatur Windows agar me-reboot ke Safe Mode saat berikutnya Anda menyalakan ulang komputer. Berguna untuk troubleshooting.

- Disable Safe Mode Boot:
  Menghapus pengaturan Safe Mode agar komputer Anda boot kembali ke mode normal. Harus dijalankan setelah selesai menggunakan Safe Mode.
        """
        
        # Buat dialog baru
        dialog = QDialog(self)
        dialog.setWindowTitle("Help Content - Macan Conquer")
        dialog.setGeometry(200, 200, 600, 500)
        
        # Layout untuk dialog
        layout = QVBoxLayout(dialog)
        
        # Text area yang bisa di-scroll
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(help_content)
        
        # Tombol OK
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        
        layout.addWidget(text_edit)
        layout.addWidget(ok_button)
        
        dialog.setLayout(layout)
        dialog.exec()

    # --- [ SEMUA FUNGSI LOGIC DARI KODE SEBELUMNYA TETAP SAMA ] ---
    def get_executable_path(self, exe_name):
        """Mendapatkan path absolut ke aplikasi eksternal.
        Mendukung mode script biasa dan mode bundle PyInstaller (_MEIPASS)."""
        if hasattr(sys, '_MEIPASS'):
            # Berjalan dalam bundle PyInstaller
            base_path = sys._MEIPASS
        else:
            # Berjalan sebagai script .py biasa
            base_path = os.path.abspath(".")
        
        path = os.path.join(base_path, exe_name)
        self.add_log(f"Mencari executable di: {path}")
        return path

    def launch_external_app(self, exe_name, app_friendly_name):
        """Template untuk meluncurkan aplikasi eksternal tanpa menangkap output."""
        if self.is_running:
            QMessageBox.warning(self, "Proses Berjalan", "Satu proses sudah berjalan, harap tunggu hingga selesai.")
            return

        exe_path = self.get_executable_path(exe_name)

        if not os.path.exists(exe_path):
            error_msg = f"Aplikasi tidak ditemukan!\n\nPastikan '{exe_name}' berada di lokasi yang benar:\n{os.path.dirname(exe_path)}"
            QMessageBox.critical(self, "Error: File Tidak Ditemukan", error_msg)
            self.add_log(f"❌ Gagal: {exe_name} tidak ditemukan.")
            return

        try:
            self.add_log(f"🚀 Meluncurkan {app_friendly_name}...")
            # Menggunakan Popen agar tidak memblokir aplikasi utama
            subprocess.Popen([exe_path])
        except Exception as e:
            QMessageBox.critical(self, "Error Saat Meluncurkan", f"Gagal menjalankan {exe_name}.\n\nError: {e}")
            self.add_log(f"❌ Error saat meluncurkan {app_friendly_name}: {e}")

    def run_registry_cleaner(self):
        self.launch_external_app("Little Registry Cleaner.exe", "Registry Cleaner")

    def run_startup_manager(self):
        self.launch_external_app("Little Startup Manager.exe", "Startup Manager")

    def run_uninstall_manager(self):
        self.launch_external_app("Little Uninstall Manager.exe", "Uninstall Manager")

    def get_icon_path(self):
        import base64
        icon_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAbUSURBVHhe7Zt7bBzFFcdfn9k3u7u2hJBsSEgcSAhJgBAgBRoJqKgPQVSl8CFUEfBFigqlatGqVUJU6YOqRFpEUaW0iBDQAkERRQkN4oDEBQQhB4QcEGLbjpM4juNjf9zZu3v2zO7sO/t2E8n+0M7OzPfN+c2bN/NmJicnI+dcuXLlT5cuXerTp0/L5XKxWq38/f39ycnJWFhYCIVCgf7+/qWlpW1pabGwsFAmkzGbzVksFo1G49WrV3fv3l1dXV1fX1+r1Wq32zEYDKFQyNvb29bW1urq6ubm5iYmJjo6OvLz89PX19ff3x+LxWxtbTUajbW1tVwu18nJycnJSWVlZaFQWFtb29PTY7PZuFwulUq1t7cXCoVGR0eZm5uTy+Xy+Xy1Wi2RSFRWVtZyuSQSiWZmZqampmpqahgMho2Njbe3t4ODg0KhkM1mI5PJqampxWLx9u3bmUwmc3NzLBYLa2trm81mfX19gUDAYDDs7Ox0d3dnMpk2Njba7XauXr0ajUb/7t27Xq/X7/evX7+eTCbL5fL+/v6BgYGmpqZMJjM/Pz87OzszM7OwsLB169ahUOjc3NzW1taysrJUKpVerxeJRHp7e7u7u+VyueDgYCaT2djYGB8f7+/vr6ur6+joMBqNXV1deXl5LS0tmUymWq2enJyUSqXNzc0Gg2FhYaG7u3t4eDg4OPj+/v7u3bvr6+tLpVImp+bm5uLiYm9v7/b29kKhODg46O3tZTAYKpXK8vJyc3OzVquVy+WKxWJ3d3d5eXlubm5ubm54ePjVq1f5+fmuri4ej+fkyZMOh8NmsxUKhU6n0+l0Ojs7m5ub5XJ5X1+fxWKx2+08Hg+TyWQymaioKE9Pz/v37wcHB8u9RkdH6+vrhUKhwWC4urrK5XJjY2NTU1ODg4MOh+Po6Ghubq6pqbGwsLC0tBQKhaGhof7+fn9/fw6H4+joiMvl8ng8er2+srKSz+fLZDKdTqenp6elpWVmZubm5qanp8vl8sbGRjabnZuby2aze3t7nU6n3W5vb28/Pz+xWMxhMOzt7XV0dHh4eHh5ednatWvr6+vL5fL+/n6VSlVXV8vlcr1eL5fLKysrKysrPT09Ho9nZ2fncDjx8fGFhYUNDQ2DwWBubn55eTkxMbGwsLC4uNiY6eLi4urqSqFQWFpaGhwc7OzsLC0tNTY2dnV1hUJhoVDY0tJiMpk6nU6v1+/u7h4cHLS0tPT29nZ1ddXpdNvb24eHhy0tLWaz2Ww2q1QqDocDwO8jFotdXV2tqalhs9nNzc0+n29mZsZgMHR0dDabzXK5/H5/c3OzTCa7uLjIZDIhISH9/f1GR0fn5+dVVVWVlZXNzc3Nzc1tbm6WymQyNTXV6/WKxeKtrS0ymaytrc3Pz/f396enp8disUajcblcmUxmaGjIYDAYDIaHhwcXF5fL5YqLixsaGuRy+ejoaCKRaGNjU11dXV1dzWaz4+PjQ0NDXV1dPz8/Pz8/MzMzPT3dZDIZDAYOh2NraysUCgcHBycnJ8fHx3V1dXa7/dGjR8e8b/X19bNnz3Z1dfV4PBaLxdLS0iNHjvz73/+urKxkMpl8Pl9aWlpZWcnooKCgwMDAxMREsVhsNpu1Wi2VSkUi0fLy8vj4eDgcDofDER4eVlZWxsbGhoaGVlZW8vPzo6KiOjs7MzMzxWLxgQMHGBgY0Gg0oVB49uzZR48esVgsHo+Xy+WjoyNPT08+n//48eOuri4SiURPT4+jHxsbm5qaunDhwsKFC0NDQzdu3Lh9+3ZpaamtrS2Xy7W1tUVFRbW2tra0tPTy5cuhoaFCoXDs2LHDhw9PT0/XarXz8/MjIyPz8/NDQ0PDw8ODg4MHDx6MjIwMDg6urKxsbGxsbm4eHh52dXVNTU2Dg4MdHR0qlSoUCsPDw6WlpXV1dVVVVS0tLb29vQ0NDUVFRbW2tmZnZ0dFRTU2Nqanp7OysmpqahrK5uZma2vr0aNHx48fDw8P5/V1dnZu377d0dExMTGRl5f35MkTf0RGRnp7ezs6OnK5XC6XKyYmJigoKBgMBqPRGB8fHxoaGhsbi4qKCg0Nra2tjY+PZzKZHo/n7e3t7++vrKwkEolEIlFdXV1VVVVXVw8NDdXU1Eil0oqKCgaDIZPJhoaGGhoaGhoaWl1dDQkJycnJqa2tra+vb21tra2tzc/PP3r0KDExMSEhITQ0tLa2lpWVlZOTk52dzefzPT09mUwmk8kMDQ3V1tZmZmbC4fDdu3dzc3MLCwt1dXWDg4OZmZlCodDY2Hjw4MGJiYnp6em5ublRUVHh4eHFxcVVVVWtra1hYWEymSwUCq1WSyQSXq9nbW1tbm52dnbW1taUSqUoRkdHLS0tdXp4eNjV1RULFy4sKCgoKCiIjIyMiYkJCgrKycmxsbHJy8ubmpra2tqKi4urq6vR0dH9/f2Tk5P19fX5+fl+fn4oPDIyMjIyUhRzcnLy8/NFRUVZWVn5+fkxMTFGoxGLxTY3N1s6MzMz1Go1n88nEokKhSIUCuVyecXFxdHR0dHR0dXV1dLS0qKiIl9fX3t7ew6H4+fn5+HhoaOj4+Hh4e/vr6ury2QyNTU1Wq12YGCgVqsVCoWuri69Xu/o6OjW5vP5NTU1ra2tra2tjY2NRUVFJSUlVVVVZWVkJCYmJCYmpqSkjEYjo6OjpaWlrq4ulUq1WCwxMfGgQYNUKlVeXl5SUpKampqbm2tra3t6emSz2Ww2KxQKOzu7ycnJnJycnJwciqIcHByamppWVlYej+ft7e3v76+rq8vl8kZGRlVVVWNjY0FBQWVlZWlpqVAo7OzsZGZm5uTkJCQklJeX5+Tk5OTkJCQkpKamRkdHx8TEhIeHx8bGmpubW1paCgoKCgoKKioquFwuHo8nfDwej+fs2bP9/f3x8fH9/f3e3l4ul2tjY6OlpSUuLi4sLMzg4GB7e3t6evrQoUNDQ0NDQkKioiKlpKSkpKSkpKSsrCxqNBqLxTIajTqdTqfT+/r6Ojs7hUIheW9vb3d3Vyn8B2r+C00u0Wp8AAAAAElFTkSuQmCC')
        
        path = os.path.join(tempfile.gettempdir(), "macan_icon.png")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(icon_data)
        return path

    def get_icon(self):
        return QIcon(self.get_icon_path())

    def set_controls_enabled(self, enabled):
        self.is_running = not enabled
        for button in self.button_widgets:
            button.setEnabled(enabled)

    def add_log(self, message):
        self.output_console.append(message)
        self.output_console.verticalScrollBar().setValue(
            self.output_console.verticalScrollBar().maximum()
        )

    def process_finished(self):
        self.add_log("\n✅ === PROSES SELESAI === ✅\n")
        self.set_controls_enabled(True)
        self.process = None

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.add_log(data.strip())

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        self.add_log(f"ERROR: {data.strip()}")

    def run_command(self, program, args):
        if self.is_running:
            QMessageBox.warning(self, "Proses Berjalan", "Satu proses sudah berjalan, harap tunggu hingga selesai.")
            return

        self.add_log(f"🚀 Memulai: {program} {' '.join(args)}")
        self.set_controls_enabled(False)

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.start(program, args)

    def run_defrag(self):
        self.run_command("defrag", ["C:", "/O"])

    def run_chkdsk(self):
        QMessageBox.information(self, "Info Scan Disk", 
                                "Scan Disk (chkdsk) akan berjalan dalam mode 'read-only'.\n"
                                "Ini tidak akan memperbaiki error tapi akan melaporkannya.\n"
                                "Untuk perbaikan penuh (memerlukan restart), jalankan 'chkdsk C: /f /r' di Command Prompt (Admin).")
        self.run_command("chkdsk", ["C:"])

    def run_sfc(self):
        self.run_command("sfc", ["/scannow"])

    def run_dism(self):
        self.run_command("DISM.exe", ["/Online", "/Cleanup-image", "/Restorehealth"])

    def execute_python_task(self, task_function, task_name):
        if self.is_running:
            QMessageBox.warning(self, "Proses Berjalan", "Harap tunggu proses lain selesai.")
            return
        
        self.set_controls_enabled(False)
        self.add_log(f"🚀 Memulai: {task_name}...")
        try:
            task_function()
        except Exception as e:
            self.add_log(f"❌ Error saat menjalankan {task_name}: {e}")
        finally:
            self.add_log(f"\n✅ === {task_name} SELESAI === ✅\n")
            self.set_controls_enabled(True)

    def clear_temp_files(self):
        self.execute_python_task(self._clear_temp_action, "Clear Temporary Files")

    def _clear_temp_action(self):
        temp_dir = tempfile.gettempdir()
        deleted_count, failed_count = 0, 0
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                elif os.path.isdir(path): shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                self.add_log(f"Gagal menghapus {path}: {e}")
                failed_count += 1
        self.add_log(f"\nRingkasan: {deleted_count} item dihapus, {failed_count} item gagal.")

    def clear_update_cache(self):
        reply = QMessageBox.question(self, "Konfirmasi",
                                     "Ini akan menghentikan service Windows Update, menghapus cache, lalu menyalakannya lagi.\nLanjutkan?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_python_task(self._clear_update_cache_action, "Clear Windows Update Cache")

    def _clear_update_cache_action(self):
        commands = [("net", "stop", "wuauserv"), ("net", "stop", "bits")]
        for cmd in commands:
            self.add_log(f"Menjalankan: {' '.join(cmd)}")
            subprocess.run(cmd, shell=True, capture_output=True)
        
        cache_dir = r"C:\Windows\SoftwareDistribution\Download"
        self.add_log(f"Menghapus isi dari {cache_dir}...")
        deleted_count, failed_count = 0, 0
        for item in os.listdir(cache_dir):
            path = os.path.join(cache_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                elif os.path.isdir(path): shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                self.add_log(f"Gagal menghapus {path}: {e}")
                failed_count += 1
        self.add_log(f"Ringkasan: {deleted_count} item dihapus, {failed_count} gagal.")

        commands = [("net", "start", "wuauserv"), ("net", "start", "bits")]
        for cmd in commands:
            self.add_log(f"Menjalankan: {' '.join(cmd)}")
            subprocess.run(cmd, shell=True, capture_output=True)

    def reset_icon_cache(self):
        reply = QMessageBox.warning(self, "Konfirmasi Penting",
                                    "Ini akan mematikan paksa Windows Explorer (taskbar dan ikon akan hilang sejenak) untuk mereset cache ikon.\nIni aman dilakukan. Lanjutkan?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_python_task(self._reset_icon_cache_action, "Reset Icon Cache")

    def _reset_icon_cache_action(self):
        db_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "IconCache.db")
        self.add_log("Mematikan Windows Explorer...")
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, shell=True)
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                self.add_log(f"Berhasil menghapus: {db_path}")
            else:
                self.add_log("File IconCache.db tidak ditemukan (mungkin sudah bersih).")
        except Exception as e:
            self.add_log(f"Gagal menghapus IconCache.db: {e}")
        self.add_log("Menjalankan kembali Windows Explorer...")
        subprocess.Popen("explorer.exe", shell=True)

    def boot_to_safe_mode(self):
        reply = QMessageBox.warning(self, "Reboot ke Safe Mode",
                                    "Komputer akan diatur untuk boot ke Safe Mode saat restart berikutnya.\nPastikan Anda tahu cara menonaktifkannya jika diperlukan.\nLanjutkan?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.run_command("bcdedit", ["/set", "{current}", "safeboot", "minimal"])
            QMessageBox.information(self, "Sukses", "Konfigurasi Safe Mode berhasil. Silakan restart komputer Anda.")

    def disable_safe_mode(self):
        reply = QMessageBox.question(self, "Nonaktifkan Safe Mode",
                                     "Ini akan menghapus pengaturan boot ke Safe Mode. Lakukan ini jika Anda sudah selesai dengan Safe Mode atau terjebak di dalamnya.\nLanjutkan?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.run_command("bcdedit", ["/deletevalue", "{current}", "safeboot"])
            QMessageBox.information(self, "Sukses", "Pengaturan Safe Mode telah dihapus. Komputer akan boot normal saat restart berikutnya.")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    app_instance = QApplication.instance()
    if not app_instance:
        app_instance = QApplication(sys.argv)

    if is_admin():
        # --- STYLESHEET BARU YANG LEBIH ESTETIS ---
        app_instance.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", "Helvetica Neue", "Arial", sans-serif;
                font-size: 10pt;
            }
            QMainWindow {
                background-color: #21252b;
            }
            QMenuBar {
                background-color: #282c34;
                color: #e6e6e6;
                border-bottom: 1px solid #3a4049;
            }
            QMenuBar::item {
                background-color: #282c34;
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4b5263;
            }
            QMenu {
                background-color: #282c34;
                color: #e6e6e6;
                border: 1px solid #3a4049;
            }
            QMenu::item:selected {
                background-color: #4b5263;
            }
            #TitleLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #e6e6e6;
            }
            #SubtitleLabel {
                font-size: 11pt;
                color: #9da5b4;
            }
            QGroupBox#FunctionGroup {
                background-color: #282c34;
                border: 1px solid #3a4049;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox#FunctionGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                background-color: #3a4049;
                border-radius: 4px;
                color: #61afef; /* Biru terang sebagai aksen */
                font-weight: bold;
            }
            #GroupTitle {
                font-size: 11pt;
                color: #9da5b4;
                font-weight: bold;
                padding-left: 5px;
            }
            QPushButton {
                background-color: #4b5263;
                color: #e6e6e6;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #565f74;
            }
            QPushButton:pressed {
                background-color: #424855;
            }
            QPushButton:disabled {
                background-color: #3a4049;
                color: #787878;
            }
            #OutputConsole {
                background-color: #1c1f24;
                color: #abb2bf;
                font-family: "Consolas", "Courier New", monospace;
                border: 1px solid #3a4049;
                border-radius: 6px;
                font-size: 9pt;
            }
            QScrollBar:vertical {
                border: none;
                background: #282c34;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4b5263;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        window = MacanConquerApp()
        window.show()
        sys.exit(app_instance.exec())
    else:
        msg = "Aplikasi ini memerlukan hak Administrator untuk berfungsi dengan benar.\n\nKlik 'OK', lalu klik 'Yes' pada jendela UAC yang muncul."
        QMessageBox.information(None, "Memerlukan Hak Admin", msg)
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            error_msg = f"Gagal menjalankan sebagai Administrator.\n\nError: {e}\n\nCoba klik kanan file dan pilih 'Run as administrator'."
            QMessageBox.critical(None, "Gagal Mendapatkan Hak Admin", error_msg)
        sys.exit(0)

if __name__ == "__main__":
    main()