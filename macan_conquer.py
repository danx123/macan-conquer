# Nama File: macan_conquer.py (Versi Perbaikan)
# Deskripsi: Tools untuk maintenance dan perbaikan Windows 10/11.
# Dibuat dengan Python dan PySide6.
#
# Cara Menjalankan:
# 1. Install PySide6: pip install pyside6
# 2. Jalankan script ini dengan hak Administrator.
#    (Klik kanan file -> Run as administrator)

import sys
import os
import ctypes
import subprocess
import shutil
import tempfile

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QWidget, QTextEdit, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

# --- [ SEMUA KELAS MacanConquerApp DARI KODE SEBELUMNYA TETAP SAMA ] ---
# --- [ Cukup salin bagian di bawah ini untuk menggantikan bagian main() ] ---

class MacanConquerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Conquer - Windows Fix Tool")
        self.setFixedSize(600, 700)
        self.setWindowIcon(self.get_icon())

        self.process = None
        self.is_running = False

        # --- UI Setup ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Header
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        pixmap = QPixmap(self.get_icon_path())
        logo_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_label = QLabel("Macan Conquer")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # Output Console
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setFont(QFont("Consolas", 10))
        self.output_console.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        # Tombol-tombol
        self.buttons = {
            "Defrag / Optimize Drive (C:)": self.run_defrag,
            "Scan Disk (chkdsk C:)": self.run_chkdsk,
            "System File Checker (sfc /scannow)": self.run_sfc,
            "DISM Restore Health": self.run_dism,
            "Clear Temporary Files": self.clear_temp_files,
            "Clear Windows Update Cache": self.clear_update_cache,
            "Reset Icon Cache": self.reset_icon_cache,
            "Boot to Safe Mode (Minimal)": self.boot_to_safe_mode,
            "Disable Safe Mode Boot": self.disable_safe_mode,
        }

        self.button_widgets = []
        for text, func in self.buttons.items():
            button = QPushButton(text)
            button.setFont(QFont("Segoe UI", 10))
            button.clicked.connect(func)
            self.layout.addWidget(button)
            self.button_widgets.append(button)

        self.layout.addWidget(QLabel("Output Log:"))
        self.layout.addWidget(self.output_console)
        self.add_log("Selamat datang di Macan Conquer! Jalankan sebagai Administrator.")

    def get_icon_path(self):
        # Menyimpan icon sementara saat script berjalan
        import base64
        icon_data = base64.b64decode(
            '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')
        
        path = os.path.join(tempfile.gettempdir(), "macan_icon.png")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(icon_data)
        return path

    def get_icon(self):
        return QIcon(self.get_icon_path())

    def set_controls_enabled(self, enabled):
        """Mengaktifkan atau menonaktifkan semua tombol."""
        self.is_running = not enabled
        for button in self.button_widgets:
            button.setEnabled(enabled)

    def add_log(self, message):
        """Menambahkan pesan ke console output."""
        self.output_console.append(message)
        self.output_console.verticalScrollBar().setValue(
            self.output_console.verticalScrollBar().maximum()
        )

    def process_finished(self):
        """Dipanggil saat proses selesai."""
        self.add_log("\n✅ === PROSES SELESAI === ✅\n")
        self.set_controls_enabled(True)
        self.process = None

    def handle_stdout(self):
        """Membaca output standar dari proses."""
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.add_log(data.strip())

    def handle_stderr(self):
        """Membaca output error dari proses."""
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        self.add_log(f"ERROR: {data.strip()}")

    def run_command(self, program, args):
        """Template untuk menjalankan perintah eksternal."""
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

    # --- Fungsi Tombol ---

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
        deleted_count = 0
        failed_count = 0
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                    self.add_log(f"Deleted file: {path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    self.add_log(f"Deleted folder: {path}")
                deleted_count += 1
            except Exception as e:
                self.add_log(f"Gagal menghapus {path}: {e}")
                failed_count += 1
        self.add_log(f"\nRingkasan: {deleted_count} item dihapus, {failed_count} item gagal dihapus.")

    def clear_update_cache(self):
        reply = QMessageBox.question(self, "Konfirmasi",
                                     "Ini akan menghentikan service Windows Update, menghapus cache, lalu menyalakannya lagi.\nLanjutkan?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_python_task(self._clear_update_cache_action, "Clear Windows Update Cache")

    def _clear_update_cache_action(self):
        commands = [
            ("net", "stop", "wuauserv"),
            ("net", "stop", "bits")
        ]
        for cmd in commands:
            self.add_log(f"Menjalankan: {' '.join(cmd)}")
            subprocess.run(cmd, shell=True, capture_output=True)
        
        cache_dir = r"C:\Windows\SoftwareDistribution\Download"
        self.add_log(f"Menghapus isi dari {cache_dir}...")
        
        deleted_count = 0
        failed_count = 0
        for item in os.listdir(cache_dir):
            path = os.path.join(cache_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                self.add_log(f"Gagal menghapus {path}: {e}")
                failed_count += 1
        self.add_log(f"Ringkasan: {deleted_count} item dihapus, {failed_count} gagal.")

        commands = [
            ("net", "start", "wuauserv"),
            ("net", "start", "bits")
        ]
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
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True)
        
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                self.add_log(f"Berhasil menghapus: {db_path}")
            else:
                self.add_log("File IconCache.db tidak ditemukan (mungkin sudah bersih).")
        except Exception as e:
            self.add_log(f"Gagal menghapus IconCache.db: {e}")
        
        self.add_log("Menjalankan kembali Windows Explorer...")
        subprocess.Popen("explorer.exe")

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
    """Mengecek apakah script dijalankan dengan hak Administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Cek jika aplikasi sudah dibuat (untuk menghindari error saat import)
    app_instance = QApplication.instance()
    if not app_instance:
        app_instance = QApplication(sys.argv)

    if is_admin():
        # Apply a simple dark theme
        app_instance.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                color: #f0f0f0;
                font-family: Segoe UI;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: 1px solid #6a6a6a;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #7a7a7a;
            }
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                font-size: 11pt;
            }
        """)
        window = MacanConquerApp()
        window.show()
        sys.exit(app_instance.exec())
    else:
        # ================== PERBAIKAN DI SINI ==================
        # Tampilkan pesan notifikasi sebelum meminta UAC
        msg = "Aplikasi ini memerlukan hak Administrator untuk berfungsi dengan benar.\n\nKlik 'OK', lalu klik 'Yes' pada jendela UAC yang muncul."
        QMessageBox.information(None, "Memerlukan Hak Admin", msg)
        
        # Mencoba menjalankan ulang script dengan hak admin
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            # Jika gagal, tampilkan error
            error_msg = f"Gagal menjalankan sebagai Administrator.\n\nError: {e}\n\nCoba klik kanan file dan pilih 'Run as administrator'."
            QMessageBox.critical(None, "Gagal Mendapatkan Hak Admin", error_msg)
        
        # Keluar dari script saat ini
        sys.exit(0)


if __name__ == "__main__":
    main()