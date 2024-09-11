import sys
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget, QAction, QMessageBox, QProgressBar, QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from urllib.parse import urlparse
from PyQt5.QtGui import QIcon, QPalette, QColor

# Allowed base domains or URL substrings
ALLOWED_URLS = [
    "intelligentcontacts.net",  # Allow all google subdomains and paths
    "capagent1.com",
]

def is_allowed_url(url):
    """ Check if the URL is allowed by matching its base domain or path against allowed substrings. """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Get the domain (e.g., 'www.google.com')
    
    # Check if any allowed URL is a substring of the domain or full URL
    for allowed in ALLOWED_URLS:
        if allowed in domain or allowed in url:
            return True
    return False

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restricted Browser with Blocked Websites")
        self.setWindowIcon(QIcon("browser_icon.png"))
        
        # Create a Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)  # Enable closable tabs
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        
        # Add Navigation bar
        self.navbar = QToolBar()
        self.navbar.setBackgroundRole(QPalette.ColorRole.Light)
        self.addToolBar(self.navbar)
        
        # Back button with icon
        back_btn = QAction(QIcon("icons/back.png"), "Back", self)
        back_btn.triggered.connect(self.go_back)
        self.navbar.addAction(back_btn)
        
        # Forward button with icon
        forward_btn = QAction(QIcon("icons/forward.png"), "Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        self.navbar.addAction(forward_btn)
        
        # Reload button with icon
        reload_btn = QAction(QIcon("icons/reload.png"), "Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(reload_btn)
        
        # Editable search bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url_from_search)
        self.navbar.addWidget(self.url_bar)
        
        # Add a button to allow new tabs with icon
        new_tab_btn = QAction(QIcon("icons/new_tab.png"), "New Tab", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        # Add home button with icon (go to default site)
        home_btn = QAction(QIcon("icons/home.png"), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)
        
        # Add a progress bar (for loading indication)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.navbar.addWidget(self.progress_bar)
        self.progress_bar.hide()  # Initially hide the progress bar
        
        # Set default tab with homepage
        self.add_new_tab(QUrl("https://cc.capagent1.com"), "Home")

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None or qurl is False:
            qurl = QUrl("https://cc.capagent1.com")
        print(qurl)
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Add close button (cross icon) to the tab
        self.add_close_button_to_tab(i, label)
        
        # Update URL when it changes
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl, browser))
        # Update progress bar for page loading
        browser.loadStarted.connect(self.show_loading)
        browser.loadProgress.connect(self.update_loading_progress)
        browser.loadFinished.connect(self.hide_loading)
        
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def load_url_from_search(self):
        ''' Load URL typed in the search bar '''
        qurl = QUrl(self.url_bar.text())
        self.tabs.currentWidget().setUrl(qurl)
        
    def update_url(self, qurl, browser):
        if not is_allowed_url(qurl.toString()):
            self.show_warning()  # Show a warning message for blocked sites
            QTimer.singleShot(500, lambda: browser.setUrl(QUrl("https://cc.capagent1.com")))  # Redirect to homepage
        else:
            self.url_bar.setText(qurl.toString())

    def add_close_button_to_tab(self, tab_index, tab_label):
        """ Adds a close (x) button to the tab. """
        tab_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label for tab text
        label = QLabel(tab_label)
        layout.addWidget(label)

        # Create close button
        close_button = QPushButton("x")
        close_button.setFixedSize(16, 16)
        close_button.clicked.connect(lambda: self.close_current_tab(tab_index))
        layout.addWidget(close_button)

        tab_widget.setLayout(layout)
        self.tabs.setTabText(tab_index, "")
        self.tabs.setTabEnabled(tab_index, True)
        # self.tabs.setTabOrder(tab_index, tab_widget)

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://cc.capagent1.com"))

    def go_back(self):
        self.tabs.currentWidget().back()

    def go_forward(self):
        self.tabs.currentWidget().forward()

    def reload_page(self):
        self.tabs.currentWidget().reload()

    def show_warning(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Blocked Website!")
        msg_box.setText("Access to this website is blocked.")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()

    def show_loading(self):
        ''' Show the progress bar when loading starts '''
        self.progress_bar.show()

    def hide_loading(self):
        ''' Hide the progress bar when loading finishes '''
        self.progress_bar.hide()

    def update_loading_progress(self, progress):
        ''' Update the progress bar value '''
        self.progress_bar.setValue(progress)

def main():
    app = QApplication(sys.argv)
    window = Browser()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
