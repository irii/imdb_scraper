# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\frontend\view\ui\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1551, 1154)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton_scrape = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_scrape.setMaximumSize(QtCore.QSize(200, 16777215))
        self.pushButton_scrape.setObjectName("pushButton_scrape")
        self.verticalLayout_2.addWidget(self.pushButton_scrape)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.comboBox_select_type = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_select_type.setObjectName("comboBox_select_type")
        self.verticalLayout_2.addWidget(self.comboBox_select_type)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView_items = QtWidgets.QTableView(self.centralwidget)
        self.tableView_items.setObjectName("tableView_items")
        self.verticalLayout.addWidget(self.tableView_items)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1551, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Database = QtWidgets.QAction(MainWindow)
        self.actionOpen_Database.setObjectName("actionOpen_Database")
        self.actionSave_Database = QtWidgets.QAction(MainWindow)
        self.actionSave_Database.setObjectName("actionSave_Database")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionOpen_Database)
        self.menuFile.addAction(self.actionSave_Database)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IMDB Scraper | Ivan Radeljak (3222492), OTH-Regensburg"))
        self.pushButton_scrape.setText(_translate("MainWindow", "Scrape"))
        self.label.setText(_translate("MainWindow", "Select a category:"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen_Database.setText(_translate("MainWindow", "Open Database"))
        self.actionSave_Database.setText(_translate("MainWindow", "Save Database"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
