# Alexander Hess
# CS370

# PackageTrack

# The purpose of this application is to provide the user with a self-updating order tracker
# It will track and update packages shipped by USPS, UPS, and FedEx.
# At the moment, user will still have to enter Carrier and Tracking number manually.

# Imports

# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# Text to speech
import pyttsx3
# Database
import database
# System
import sys
# Classes
import classes

speaker = pyttsx3.init()

delivered = classes.DeliveredPackages()


def conduct_update():
    db = database.SqlConnect()
    db.connect()

    packages = db.get_orders()

    usps = classes.USPS()

    # Go through packages
    for package in packages:
        # If package has not already been delivered and user notified
        if package[4] != 1:
            if package[1] == "USPS":
                try:
                    usps.tracking = package[2]
                    track = usps.track_package()
                    status = track['TrackResponse']['TrackInfo']['TrackSummary']['Event']

                    db.update_status(status, package[2])

                    if status.lower().find("delivered") is not -1:
                        delivered.add(package)
                except KeyError:
                    # KeyError is likely to occur if TrackSummary isn't populated
                    # This is because the tracking number has been added prior to package
                    # entering USPS' system.
                    continue
            elif package[1] == "UPS":
                ups = classes.UPS(package[2])

                status = ups.track()

                db.update_status(status, package[2])

                if status.lower().find("delivered") is not -1:
                    delivered.add(package)
            elif package[1] == "FedEx":
                fedex = classes.FedEx(package[2])

                status = fedex.track()

                db.update_status(status, package[2])

                if status.lower().find("delivered") is not -1:
                    delivered.add(package)

    if delivered.length() > 0:
        notify = Notify()
        notify.exec_()


######################
# Add Package Window #
######################
class AddPackage(QDialog):
    def __init__(self, parent=None):
        super(AddPackage, self).__init__(parent)

        self.setWindowTitle("Add a package")
        self.setMinimumHeight(200)
        self.setMinimumWidth(500)

        # Set layout
        self.layout = QGridLayout()

        # Database
        self.db = database.SqlConnect()
        self.db.connect()

        # Carrier Selector
        self.carrier = QComboBox()
        self.carrier.addItem("USPS")
        self.carrier.addItem("UPS")
        self.carrier.addItem("FedEx")

        # Tracking Number
        self.tracking = QLineEdit()

        # Submit Button
        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.add_to_database)

        # Status Message
        self.status = QLabel()

        # Close Button
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.close)

        # Add to layout
        self.layout.addWidget(self.carrier, 0, 0, 1, 1)
        self.layout.addWidget(self.tracking, 0, 1, 1, 3)
        self.layout.addWidget(self.addButton, 0, 7, 1, 1)
        self.layout.addWidget(self.status, 1, 0)
        self.layout.addWidget(self.closeButton, 1, 7)

        self.setLayout(self.layout)

    def add_to_database(self):
        if len(self.tracking.text()) > 0:
            self.db.add_package(self.carrier.currentText(), self.tracking.text())
            self.status.setText("Added package successfully!")

            # Speak success
            speaker.say("Package has been added")
            speaker.runAndWait()
            conduct_update()
        else:
            speaker.say("You have not added a tracking number.")
            speaker.runAndWait()

            self.status.setText("Package was not added.")


###################
# Search Packages #
###################
class Search(QDialog):
    def __init__(self, parent=None):
        super(Search, self).__init__(parent)

        self.db = database.SqlConnect()
        self.db.connect()

        self.layout = QGridLayout()

        self.setWindowTitle("Search")

        # Search input
        self.input = QLineEdit()
        self.input.textEdited[str].connect(self.conduct_search)
        self.layout.addWidget(self.input, 0, 0, 1, 2)

        # Display list
        self.display = QListWidget()
        self.layout.addWidget(self.display, 1, 0, 6, 3)

        # Close
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.accept)
        self.layout.addWidget(self.closeButton, 8, 2)

        self.setLayout(self.layout)
        self.show()

    def conduct_search(self):
        results = self.db.search_orders(self.input.text())

        # Clear display to prevent constantly adding and duplicating results
        self.display.clear()

        for package in results:
            self.display.addItem(package[1] + " - " + package[2] + " | " + package[3])


#######################
# Notification Widget #
#######################
class Notify(QDialog):
    def __init__(self, parent=None):
        super(Notify, self).__init__(parent)

        self.db = database.SqlConnect()

        self.layout = QGridLayout()

        self.setWindowTitle("Packages Delivered")

        self.deliveredlist = QListWidget()
        self.list = delivered.delivered()
        for package in self.list:
            self.deliveredlist.addItem(package[1] + " - " + package[2])

        self.layout.addWidget(self.deliveredlist, 0, 0, 5, 3)

        self.acceptButton = QPushButton("Ok")
        self.acceptButton.clicked.connect(self.notify_complete)

        self.layout.addWidget(self.acceptButton, 6, 1)

        self.setLayout(self.layout)

        if len(self.list) == 1:
            speaker.say("You have one package delivered.")
        else:
            speaker.say("You have " + len(self.list) + " packages delivered")

        speaker.runAndWait()

    def notify_complete(self):
        # Set notified value in DB
        for package in self.list:
            self.db.set_notified(package[2])

        # Clear the list to prevent repeated notifications
        delivered.clear()

        self.accept()


################
# Clock Widget #
################
class Clock(QLabel):
    def __init__(self, parent=None):
        super(Clock, self).__init__(parent)

        self.time = QDateTime.currentDateTime()

        # Set display format
        self.timeDisplay = self.time.toString('yyyy-MM-dd hh:mm:ss dddd')

        # Display the time in the label widget
        self.setText(self.timeDisplay)

        # Start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.start()

    def update(self):
        # Updates label
        self.time = QDateTime.currentDateTime()
        self.timeDisplay = self.time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.setText(self.timeDisplay)

        # Automatically update tracking every half hour
        if self.time.time().minute() == "00" or self.time.time().minute() == "30":
            conduct_update()

    def start(self):
        # Timer times out every second
        self.timer.start(1000)


###############
# Main Window #
###############
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("PackageTrack v1")
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)

        # Set layout
        self.layout = QVBoxLayout()

        # Database
        self.db = database.SqlConnect()
        self.db.connect()
        self.db.create()

        # Menu
        self.bar = self.menuBar()
        self.menu = self.bar.addMenu("Actions")
        self.addNewPackage = QAction("Add New Package", self)
        self.addNewPackage.setShortcut("Ctrl+A")
        self.menu.addAction(self.addNewPackage)
        self.searchPackage = QAction("Find Package", self)
        self.searchPackage.setShortcut("Ctrl+F")
        self.menu.addAction(self.searchPackage)
        self.updatePackage = QAction("Update Tracking", self)
        self.updatePackage.setShortcut("Ctrl+U")
        self.menu.addAction(self.updatePackage)
        self.quit = QAction("Quit", self)
        self.quit.setShortcut("Ctrl+Q")
        self.menu.addAction(self.quit)
        self.menu.triggered[QAction].connect(self.process_trigger)

        # Packages List
        self.packageList = QListWidget()
        self.packageList.resize(290, 400)
        self.update_list()

        self.layout.addWidget(self.packageList)

        self.setLayout(self.layout)

        self.setCentralWidget(self.packageList)

        # Status Bar
        # Displays time, also the manager for the hidden updating method
        self.statusbar = QStatusBar()
        self.clock = Clock()
        self.statusbar.addPermanentWidget(self.clock)
        self.setStatusBar(self.statusbar)

    def update_list(self):
        packages = self.db.get_orders()

        self.packageList.clear()

        if len(packages) == 0:
            self.packageList.addItem("No Packages Tracked")
        else:
            for package in packages:
                # Do not display delivered packages
                # Delivered packages will have been listed in the delivered list
                # And user notified of the list.
                # Packages delivered remain in database for user's ability to search, in case they forgot
                if package[4] == 1:
                    continue
                else:
                    compiler = package[1] + " - " + package[2] + " | " + str(package[3])
                    self.packageList.addItem(compiler)

    def process_trigger(self, item):
        # Get text of executing action
        action = item.text()

        # Compare and execute accordingly
        if action == "Add New Package":
            speaker.say("Adding new package.")
            speaker.runAndWait()

            add = AddPackage()
            add.exec_()
            self.update_list()
        elif action == "Find Package":
            speaker.say("What package should I locate?.")
            speaker.runAndWait()

            s = Search()
            s.exec_()
        elif action == "Update Tracking":
            speaker.say("Updating")
            speaker.runAndWait()

            conduct_update()
        elif action == "Quit":
            speaker.say("Goodbye.")
            speaker.runAndWait()

            sys.exit()


# main function for run
def main():
    app = QApplication([])

    conduct_update()

    window = MainWindow()
    window.show()

    app.exec_()


# Execute Program
main()