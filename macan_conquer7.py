# Nama File: macan_conquer.py (Versi Profesional dengan Menu)
# Deskripsi: Tools untuk maintenance dan perbaikan Windows 10/11.
# Dibuat dengan Python dan PySide6.
#
# Changelog (Upgrade):
# - [UI] Layout diubah menjadi 2 kolom agar tidak terlalu memanjang ke bawah.
# - [FITUR] Ditambahkan QThread untuk semua proses panjang (sfc, dism, chkdsk, dll.)
#           untuk mencegah GUI 'freeze' atau 'not responding'.
# - [FITUR] Ditambahkan QProgressBar yang aktif selama proses sfc dan DISM.
# - [FITUR] Ditambahkan fungsi 'Save Log...' di menu File.
# - [FITUR] Ditambahkan System Info Dashboard (OS, CPU, RAM, Uptime).
# - [DEPENDENSI] Menambahkan 'psutil' untuk mengambil data System Info.
# - [PERBAIKAN] Layout System Information diringkas menjadi 2x2 dan warna font diubah.
#
# Cara Menjalankan:
# 1. Install PySide6 dan psutil: pip install pyside6 psutil
# 2. Pastikan file "toolbox.ico" dan file .exe lainnya ada di folder yang sama.
# 3. Jalankan script ini dengan hak Administrator.

import sys
import os
import ctypes
import subprocess
import shutil
import tempfile
import re
import platform
import psutil
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTextEdit, QMessageBox, QHBoxLayout, QLabel, QGridLayout, QGroupBox,
    QDialog, QScrollArea, QProgressBar, QFileDialog
)
from PySide6.QtCore import QProcess, Qt, QThread, QObject, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction

# --- Worker Thread untuk Proses Latar Belakang ---
class Worker(QObject):
    finished = Signal()
    output_ready = Signal(str)
    progress_updated = Signal(int)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.function(
                *self.args, **self.kwargs,
                progress_signal=self.progress_updated,
                output_signal=self.output_ready
            )
        except Exception as e:
            self.output_ready.emit(f"❌ Terjadi kesalahan fatal di worker thread: {e}")
        finally:
            self.finished.emit()

class MacanConquerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Conquer - Professional Windows Toolkit")
        # --- [DIUBAH] Ukuran window disesuaikan untuk layout 2 kolom ---
        self.setGeometry(100, 100, 850, 600)
        self.setWindowIcon(self.get_icon())

        self.thread = None
        self.worker = None
        self.is_running = False

        self.init_ui()
        self.add_log("Selamat datang di Macan Conquer! Aplikasi siap digunakan.")
        self.add_log("Pastikan Anda menjalankan sebagai Administrator untuk fungsionalitas penuh.")

    def init_ui(self):
        """Membangun semua elemen antarmuka pengguna."""
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

        # --- System Info Dashboard ---
        self.main_layout.addWidget(self.create_system_info_dashboard())

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.main_layout.addWidget(self.progress_bar)

        # --- [REFACTOR] Membuat layout 2 kolom untuk grup tombol ---
        self.button_widgets = []
        columns_layout = QHBoxLayout()
        left_column_layout = QVBoxLayout()
        right_column_layout = QVBoxLayout()

        # Menambahkan grup ke kolom kiri
        left_column_layout.addWidget(self.create_system_repair_group())
        left_column_layout.addWidget(self.create_cleanup_group())
        left_column_layout.addStretch() # Agar grup tidak meregang ke bawah

        # Menambahkan grup ke kolom kanan
        right_column_layout.addWidget(self.create_external_tools_group())
        right_column_layout.addWidget(self.create_advanced_boot_group())
        right_column_layout.addStretch() # Agar grup tidak meregang ke bawah

        columns_layout.addLayout(left_column_layout)
        columns_layout.addLayout(right_column_layout)

        self.main_layout.addLayout(columns_layout)

        # --- Output Console ---
        log_label = QLabel("Log Aktivitas:")
        log_label.setObjectName("GroupTitle")
        self.main_layout.addWidget(log_label)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setObjectName("OutputConsole")
        self.main_layout.addWidget(self.output_console)
        # --- AKHIR REFACTOR LAYOUT ---

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        save_log_action = QAction("Save Log...", self)
        save_log_action.triggered.connect(self._save_log_to_file)
        file_menu.addAction(save_log_action)
        file_menu.addSeparator()
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
        help_menu = menu_bar.addMenu("&Help")
        help_content_action = QAction("Help Content", self)
        help_content_action.triggered.connect(self._show_help_content)
        help_menu.addAction(help_content_action)
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def create_system_info_dashboard(self):
        group_box = QGroupBox("System Information")
        # --- [DIUBAH] Memberi nama objek unik untuk styling khusus ---
        group_box.setObjectName("SystemInfoDashboard")
        layout = QGridLayout()
        
        # --- [DIUBAH] Menggabungkan label dan nilai menjadi satu, dan mengubah teks awal ---
        self.os_label = QLabel("<b>OS:</b> Loading...")
        self.cpu_label = QLabel("<b>CPU:</b> Loading...")
        self.ram_label = QLabel("<b>RAM:</b> Loading...")
        self.uptime_label = QLabel("<b>Uptime:</b> Loading...")

        # --- [DIUBAH] Mengatur layout menjadi 2x2 agar lebih ringkas ---
        layout.addWidget(self.os_label, 0, 0)
        layout.addWidget(self.cpu_label, 0, 1)
        layout.addWidget(self.ram_label, 1, 0)
        layout.addWidget(self.uptime_label, 1, 1)
        
        group_box.setLayout(layout)
        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_system_info)
        self.info_timer.start(2000)
        self.update_system_info()
        return group_box

    def update_system_info(self):
        # --- [DIUBAH] Logika diubah untuk mengisi label yang sudah digabung ---
        # Info OS statis, hanya perlu di-set sekali
        if "Loading..." in self.os_label.text():
             self.os_label.setText(f"<b>OS:</b> {platform.system()} {platform.release()}")

        # Info dinamis, di-update setiap timer berjalan
        self.cpu_label.setText(f"<b>CPU:</b> {psutil.cpu_percent()}%")
        
        ram = psutil.virtual_memory()
        self.ram_label.setText(f"<b>RAM:</b> {ram.percent}% ({ram.used / (1024**3):.2f} / {ram.total / (1024**3):.2f} GB)")
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days, rem = divmod(uptime.total_seconds(), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        # Teks uptime dibuat lebih ringkas
        self.uptime_label.setText(f"<b>Uptime:</b> {int(days)}d {int(hours)}h {int(minutes)}m")


    def create_button(self, text, func):
        button = QPushButton(text)
        button.clicked.connect(func)
        self.button_widgets.append(button)
        return button

    # --- [REFACTOR] Fungsi grup sekarang me-return QGroupBox ---
    def create_system_repair_group(self):
        group_box = QGroupBox("Perbaikan Sistem & Integritas")
        group_box.setObjectName("FunctionGroup")
        layout = QGridLayout()
        layout.addWidget(self.create_button("System File Checker (sfc /scannow)", self.run_sfc), 0, 0)
        layout.addWidget(self.create_button("DISM Restore Health", self.run_dism), 0, 1)
        layout.addWidget(self.create_button("Scan Disk (chkdsk C:)", self.run_chkdsk), 1, 0)
        layout.addWidget(self.create_button("Defrag / Optimize Drive (C:)", self.run_defrag), 1, 1)
        group_box.setLayout(layout)
        return group_box

    def create_cleanup_group(self):
        group_box = QGroupBox("Pembersihan Sistem")
        group_box.setObjectName("FunctionGroup")
        layout = QGridLayout()
        layout.addWidget(self.create_button("Clear Temporary Files", self.clear_temp_files), 0, 0)
        layout.addWidget(self.create_button("Clear Windows Update Cache", self.clear_update_cache), 0, 1)
        layout.addWidget(self.create_button("Reset Icon Cache", self.reset_icon_cache), 1, 0)
        group_box.setLayout(layout)
        return group_box

    def create_external_tools_group(self):
        group_box = QGroupBox("Aplikasi Tambahan")
        group_box.setObjectName("FunctionGroup")
        layout = QHBoxLayout()
        layout.addWidget(self.create_button("Registry Cleaner", self.run_registry_cleaner))
        layout.addWidget(self.create_button("Startup Manager", self.run_startup_manager))
        layout.addWidget(self.create_button("Uninstall Manager", self.run_uninstall_manager))
        group_box.setLayout(layout)
        return group_box

    def create_advanced_boot_group(self):
        group_box = QGroupBox("Opsi Boot Lanjutan")
        group_box.setObjectName("FunctionGroup")
        layout = QHBoxLayout()
        layout.addWidget(self.create_button("Boot to Safe Mode (Minimal)", self.boot_to_safe_mode))
        layout.addWidget(self.create_button("Disable Safe Mode Boot", self.disable_safe_mode))
        group_box.setLayout(layout)
        return group_box

    # --- Sisa kode tidak berubah (fungsi log, task, worker, dll.) ---

    def _save_log_to_file(self):
        log_content = self.output_console.toPlainText()
        if not log_content.strip():
            QMessageBox.information(self, "Log Kosong", "Tidak ada aktivitas untuk disimpan.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan Log ke File",
            f"MacanConquer_Log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f: f.write(log_content)
                self.add_log(f"\n📝 Log berhasil disimpan ke: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan log: {e}")

    def _confirm_and_shutdown(self, command, message):
        reply = QMessageBox.question(self, "Konfirmasi", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try: subprocess.run(["shutdown", command, "/t", "0"], check=True)
            except Exception as e: QMessageBox.critical(self, "Error", f"Gagal menjalankan perintah: {e}")

    def _restart_windows(self): self._confirm_and_shutdown("/r", "Apakah Anda yakin ingin me-restart komputer sekarang?")
    def _shutdown_windows(self): self._confirm_and_shutdown("/s", "Apakah Anda yakin ingin mematikan komputer sekarang?")
    def _show_about_dialog(self): QMessageBox.about(self, "About Macan Conquer", "...")
    def _show_help_content(self): QMessageBox.information(self, "Help Content", "...")

    def get_executable_path(self, exe_name):
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
        path = os.path.join(base_path, exe_name)
        self.add_log(f"Mencari executable di: {path}")
        return path

    def launch_external_app(self, exe_name, app_friendly_name):
        if self.is_running:
            QMessageBox.warning(self, "Proses Berjalan", "Satu proses sudah berjalan, harap tunggu hingga selesai.")
            return
        exe_path = self.get_executable_path(exe_name)
        if not os.path.exists(exe_path):
            QMessageBox.critical(self, "Error: File Tidak Ditemukan", f"...")
            return
        try:
            self.add_log(f"🚀 Meluncurkan {app_friendly_name}...")
            subprocess.Popen([exe_path])
        except Exception as e:
            QMessageBox.critical(self, "Error Saat Meluncurkan", f"Gagal menjalankan {exe_name}.\n\nError: {e}")

    def run_registry_cleaner(self): self.launch_external_app("Little Registry Cleaner.exe", "Registry Cleaner")
    def run_startup_manager(self): self.launch_external_app("Little Startup Manager.exe", "Startup Manager")
    def run_uninstall_manager(self): self.launch_external_app("Little Uninstall Manager.exe", "Uninstall Manager")

    def get_icon_path(self, icon_name="toolbox.ico"):
        return os.path.join(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath("."), icon_name)

    def get_icon(self): return QIcon(self.get_icon_path())

    def set_controls_enabled(self, enabled):
        self.is_running = not enabled
        for button in self.button_widgets: button.setEnabled(enabled)

    def add_log(self, message):
        self.output_console.append(message)
        self.output_console.verticalScrollBar().setValue(self.output_console.verticalScrollBar().maximum())

    def start_task(self, function, *args, **kwargs):
        if self.is_running:
            QMessageBox.warning(self, "Proses Berjalan", "Satu proses sudah berjalan, harap tunggu hingga selesai.")
            return
        self.set_controls_enabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.thread = QThread()
        self.worker = Worker(function, *args, **kwargs)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.task_finished)
        self.worker.output_ready.connect(self.add_log)
        self.worker.progress_updated.connect(self.update_progress)
        self.thread.start()

    def task_finished(self):
        self.add_log("\n✅ === PROSES SELESAI === ✅\n")
        self.set_controls_enabled(True)
        self.progress_bar.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        self.thread = None
        self.worker = None

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"Proses berjalan... {value}%")

    def run_sfc(self): self.start_task(self._run_command_with_progress, "sfc", ["/scannow"], "sfc")
    def run_dism(self): self.start_task(self._run_command_with_progress, "DISM.exe", ["/Online", "/Cleanup-image", "/Restorehealth"], "dism")
    def run_chkdsk(self):
        QMessageBox.information(self, "Info Scan Disk", "...")
        self.start_task(self._run_command_with_progress, "chkdsk", ["C:"])
    def run_defrag(self): self.start_task(self._run_command_with_progress, "defrag", ["C:", "/O"])
    def clear_temp_files(self): self.start_task(self._clear_temp_action)

    def clear_update_cache(self):
        if QMessageBox.question(self, "Konfirmasi", "...", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.start_task(self._clear_update_cache_action)

    def reset_icon_cache(self):
        if QMessageBox.warning(self, "Konfirmasi Penting", "...", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.start_task(self._reset_icon_cache_action)

    def boot_to_safe_mode(self):
        if QMessageBox.warning(self, "Reboot ke Safe Mode", "...", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.start_task(self._run_command_with_progress, "bcdedit", ["/set", "{current}", "safeboot", "minimal"])
            QMessageBox.information(self, "Sukses", "Konfigurasi Safe Mode berhasil. Silakan restart komputer Anda.")

    def disable_safe_mode(self):
        if QMessageBox.question(self, "Nonaktifkan Safe Mode", "...", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.start_task(self._run_command_with_progress, "bcdedit", ["/deletevalue", "{current}", "safeboot"])
            QMessageBox.information(self, "Sukses", "Pengaturan Safe Mode telah dihapus. Komputer akan boot normal saat restart berikutnya.")

    def _run_command_with_progress(self, program, args, progress_type=None, **kwargs):
        output_signal = kwargs.get('output_signal')
        progress_signal = kwargs.get('progress_signal')
        output_signal.emit(f"🚀 Memulai: {program} {' '.join(args)}")
        process = subprocess.Popen([program] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            if clean_line:
                output_signal.emit(clean_line)
                if progress_type == 'sfc':
                    match = re.search(r'Verification (\d+)% complete.', clean_line)
                    if match: progress_signal.emit(int(match.group(1)))
                elif progress_type == 'dism':
                    match = re.search(r'\[=+>\s*\] (\d+\.\d+)%', clean_line)
                    if match: progress_signal.emit(int(float(match.group(1))))
        process.stdout.close()
        process.wait()

    def _clear_temp_action(self, **kwargs):
        output_signal = kwargs.get('output_signal')
        temp_dir = tempfile.gettempdir()
        deleted_count, failed_count = 0, 0
        output_signal.emit(f"Membersihkan direktori: {temp_dir}")
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                elif os.path.isdir(path): shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                output_signal.emit(f"Gagal menghapus {path}: {e}")
                failed_count += 1
        output_signal.emit(f"\nRingkasan: {deleted_count} item dihapus, {failed_count} item gagal.")

    def _clear_update_cache_action(self, **kwargs):
        output_signal = kwargs.get('output_signal')
        for cmd in [("net", "stop", "wuauserv"), ("net", "stop", "bits")]:
            output_signal.emit(f"Menjalankan: {' '.join(cmd)}")
            subprocess.run(cmd, shell=True, capture_output=True)
        cache_dir = r"C:\Windows\SoftwareDistribution\Download"
        output_signal.emit(f"Menghapus isi dari {cache_dir}...")
        deleted_count, failed_count = 0, 0
        try:
            for item in os.listdir(cache_dir):
                path = os.path.join(cache_dir, item)
                try:
                    if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
                    deleted_count += 1
                except Exception as e:
                    output_signal.emit(f"Gagal menghapus {path}: {e}")
                    failed_count += 1
        except Exception as e: output_signal.emit(f"Error mengakses {cache_dir}: {e}")
        output_signal.emit(f"Ringkasan: {deleted_count} item dihapus, {failed_count} gagal.")
        for cmd in [("net", "start", "wuauserv"), ("net", "start", "bits")]:
            output_signal.emit(f"Menjalankan: {' '.join(cmd)}")
            subprocess.run(cmd, shell=True, capture_output=True)

    def _reset_icon_cache_action(self, **kwargs):
        output_signal = kwargs.get('output_signal')
        db_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "IconCache.db")
        output_signal.emit("Mematikan Windows Explorer...")
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, shell=True)
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                output_signal.emit(f"Berhasil menghapus: {db_path}")
            else: output_signal.emit("File IconCache.db tidak ditemukan (mungkin sudah bersih).")
        except Exception as e: output_signal.emit(f"Gagal menghapus IconCache.db: {e}")
        output_signal.emit("Menjalankan kembali Windows Explorer...")
        subprocess.Popen("explorer.exe", shell=True)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def main():
    app_instance = QApplication.instance() or QApplication(sys.argv)
    if is_admin():
        app_instance.setStyleSheet("""
            QWidget { font-family: "Segoe UI", sans-serif; font-size: 10pt; }
            QMainWindow { background-color: #21252b; }
            QMenuBar { background-color: #282c34; color: #e6e6e6; }
            QMenuBar::item:selected { background-color: #4b5263; }
            QMenu { background-color: #282c34; color: #e6e6e6; border: 1px solid #3a4049; }
            QMenu::item:selected { background-color: #4b5263; }
            #TitleLabel { font-size: 20pt; font-weight: bold; color: #e6e6e6; }
            #SubtitleLabel { font-size: 11pt; color: #9da5b4; }
            
            /* --- [DIUBAH] Style ditambahkan khusus untuk dashboard info sistem --- */
            QGroupBox#SystemInfoDashboard {
                background-color: #282c34; border: 1px solid #3a4049;
                border-radius: 8px; margin-top: 1ex; padding: 10px;
            }
            QGroupBox#SystemInfoDashboard::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 2px 10px; background-color: #3a4049;
                border-radius: 4px; color: #61afef; font-weight: bold;
            }
            /* Ini bagian yang mengubah warna font di dalam box menjadi putih */
            QGroupBox#SystemInfoDashboard QLabel {
                color: #e6e6e6; 
            }
            
            QGroupBox#FunctionGroup {
                background-color: #282c34; border: 1px solid #3a4049;
                border-radius: 8px; margin-top: 1ex; padding: 10px;
            }
            QGroupBox#FunctionGroup::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 2px 10px; background-color: #3a4049;
                border-radius: 4px; color: #61afef; font-weight: bold;
            }
            #GroupTitle { color: #9da5b4; font-weight: bold; padding-left: 5px; }
            QPushButton {
                background-color: #4b5263; color: #e6e6e6; border: none;
                padding: 8px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #565f74; }
            QPushButton:pressed { background-color: #424855; }
            QPushButton:disabled { background-color: #3a4049; color: #787878; }
            #OutputConsole {
                background-color: #1c1f24; color: #abb2bf; font-family: "Consolas", monospace;
                border: 1px solid #3a4049; border-radius: 6px; font-size: 9pt;
            }
            QProgressBar {
                border: 1px solid #3a4049; border-radius: 5px; text-align: center;
                color: #e6e6e6; background-color: #282c34;
            }
            QProgressBar::chunk { background-color: #61afef; border-radius: 4px; }
            QScrollBar:vertical {
                border: none; background: #282c34; width: 10px; margin: 0;
            }
            QScrollBar::handle:vertical { background: #4b5263; min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
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
            QMessageBox.critical(None, "Gagal Mendapatkan Hak Admin", f"...")
        sys.exit(0)

if __name__ == "__main__":
    main()