import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QVBoxLayout, QWidget, QSystemTrayIcon, QLabel, QScrollArea, QHBoxLayout, QFrame, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QIcon
from threading import Thread
from app import create_app
import ctypes
import os

logging.basicConfig(level=logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screen_geometry = QApplication.desktop().screenGeometry()
        self.setWindowTitle('Chatbot')
        self.setGeometry(1000, 0, 800, self.screen_geometry.height() - 50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.95)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://127.0.0.1:5000'))
        self.browser.loadStarted.connect(self.on_load_started)
        self.browser.loadFinished.connect(self.on_load_finished)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(container)
        self.setCentralWidget(self.scroll_area)

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)

        # 슬라이딩 버튼 설정
        self.slide_button = QLabel('>', self)
        self.slide_button.setGeometry(10, 10, 30, 30)
        self.slide_button.setStyleSheet("""
            background-color: #007bff;
            color: white;
            border-radius: 15px;
            padding: 5px 10px;
            text-align: center;
        """)
        self.slide_button.setAlignment(Qt.AlignCenter)
        self.slide_button.mousePressEvent = self.toggle_window
        self.slide_button.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.slide_button.show()

        self.is_hidden = False

    def on_load_started(self):
        logging.debug('Page load started')

    def on_load_finished(self, ok):
        if ok:
            logging.debug('Page load finished successfully')
        else:
            logging.error('Failed to load page')

    def show_with_animation(self):
        logging.debug('Showing window with animation')
        self.setGeometry(1000, 0, 800, self.screen_geometry.height() - 50)
        start_pos = QPoint(self.screen_geometry.width(), 0)
        end_pos = QPoint(self.screen_geometry.width() - 800, 0)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.finished.connect(self.show_window)
        self.animation.start()
        self.show()
        self.slide_button.setText('>')

    def show_window(self):
        logging.debug('Window shown')
        self.move(QPoint(self.screen_geometry.width() - 800, 0))
        self.adjust_workspace(False)

    def hide_with_animation(self):
        logging.debug('Hiding window with animation')
        start_pos = QPoint(self.screen_geometry.width() - 800, 0)
        end_pos = QPoint(self.screen_geometry.width() - 30, 0)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.finished.connect(self.hide_window)
        self.animation.start()
        self.setGeometry(self.screen_geometry.width() - 30, 0, 800, 30)
        self.slide_button.setText('<')

    def hide_window(self):
        logging.debug('Window hidden')
        self.move(QPoint(self.screen_geometry.width() - 30, 0))
        self.adjust_workspace(True)

    def toggle_window(self, event=None):
        if self.is_hidden:
            self.show_with_animation()
        else:
            self.hide_with_animation()
        
        self.slide_button.show()
        self.is_hidden = not self.is_hidden

    def adjust_workspace(self, restore):
        import ctypes
        import ctypes.wintypes

        # Define constants
        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79
        SM_CYSCREEN = 1

        # Get screen dimensions
        cx = ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        cy = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

        # Get the work area excluding the taskbar
        work_area = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(work_area), 0)
        taskbar_height = cy - work_area.bottom

        if restore:
            work_area.left = 0
            work_area.top = 0
            work_area.right = cx
            work_area.bottom = cy - taskbar_height
        else:
            work_area.left = 0
            work_area.top = 0
            work_area.right = cx - 800
            work_area.bottom = cy - taskbar_height

        # Update system parameters
        ctypes.windll.user32.SystemParametersInfoW(0x002F, 0, ctypes.byref(work_area), 0)

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, app, window):
        super().__init__(QIcon('app/static/favicon.ico'), app)  # 경로 수정
        self.window = window

        self.setToolTip('Chatbot')
        menu = QMenu()
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_window)
        menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_icon_activated)

    def toggle_window(self):
        logging.debug('Toggling window visibility')
        self.window.toggle_window()

    def exit_app(self):
        logging.debug('Exiting application')
        QApplication.instance().quit()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            logging.debug('Tray icon clicked')
            self.toggle_window()

class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.main_window = MainWindow()
        self.tray_icon = SystemTrayApp(self, self.main_window)
        self.tray_icon.show()
        self.setQuitOnLastWindowClosed(False)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(None, "Admin Privileges Required", f"Failed to obtain admin privileges: {e}")
            sys.exit(1)

if __name__ == '__main__':
    run_as_admin()

    def run_flask():
        app = create_app()
        # Flask 설정 최적화
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['ENV'] = 'development'

        # 파일 업로드를 위한 디렉토리 생성
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        app.run(debug=False, use_reloader=False, threaded=False)  # debug 모드를 제거하여 성능 최적화

    try:
        logging.debug('Starting server thread')
        server_thread = Thread(target=run_flask)
        server_thread.start()

        logging.debug('Starting Qt application')
        app = App(sys.argv)
        app.main_window.show_with_animation()  # 애플리케이션 실행 시 메인 윈도우를 표시

        app.main_window.toggle_window()

        sys.exit(app.exec_())
    except Exception as e:
        logging.error('An error occurred: %s', e)
