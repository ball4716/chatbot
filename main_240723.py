import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QVBoxLayout, QWidget, QSystemTrayIcon, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QIcon
from threading import Thread
from app import create_app

logging.basicConfig(level=logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        screen_geometry = QApplication.desktop().screenGeometry()
        self.setWindowTitle('Chatbot')
        self.setGeometry(1000, 0, 800, screen_geometry.height() - 50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.95)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://127.0.0.1:5000'))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)

        # 슬라이딩 버튼 설정
        self.slide_button = QLabel('Toggle', self)
        self.slide_button.setGeometry(10, 10, 100, 30)
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

    def show_with_animation(self):
        logging.debug('Showing window with animation')
        screen_geometry = QApplication.desktop().screenGeometry()
        start_pos = QPoint(screen_geometry.width(), 0)
        end_pos = QPoint(screen_geometry.width() - 800, 0)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.finished.connect(self.show_window)
        self.animation.start()
        self.show()

    def show_window(self):
        logging.debug('Window shown')
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(QPoint(screen_geometry.width() - 800, 0))

    def hide_with_animation(self):
        logging.debug('Hiding window with animation')
        screen_geometry = QApplication.desktop().screenGeometry()
        start_pos = QPoint(screen_geometry.width() - 800, 0)
        end_pos = QPoint(screen_geometry.width(), 0)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.finished.connect(self.hide_window)
        self.animation.start()

    def hide_window(self):
        logging.debug('Window hidden')
        self.move(QPoint(QApplication.desktop().screenGeometry().width() - 100, 0))

    def toggle_window(self, event=None):
        if self.is_hidden:
            self.show_with_animation()
        else:
            self.hide_with_animation()
        self.is_hidden = not self.is_hidden

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, app, window):
        super().__init__(QIcon('app/static/icon.ico'), app)
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

if __name__ == '__main__':
    def run_flask():
        app = create_app()
        app.run(debug=True, use_reloader=False)

    try:
        logging.debug('Starting server thread')
        server_thread = Thread(target=run_flask)
        server_thread.start()

        logging.debug('Starting Qt application')
        app = App(sys.argv)
        app.main_window.show_with_animation()  # 애플리케이션 실행 시 메인 윈도우를 표시
        sys.exit(app.exec_())
    except Exception as e:
        logging.error('An error occurred: %s', e)
