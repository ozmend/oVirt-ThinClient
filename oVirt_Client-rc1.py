#!/usr/bin/env	python3.6
# -*- coding: utf-8 -*-
'''
This was developed as oVirt VDI solution by Özmen Emre Demirkol <ozmend@gmail.com>, <ozmen.demirkol@tubitak.gov.tr>.
Purpose of this is making a basic gui to build a thin_client.
It connects to your ovirt server with an user account, get his/her vms and makes a spice connection.
'''


from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QLabel, \
    QLineEdit, QGroupBox, QGridLayout, QDesktopWidget, QMessageBox, \
    QSpacerItem, QHBoxLayout, QComboBox, QWidget, QSizePolicy, QStyle
from PyQt5.QtCore import Qt, QRect, QTranslator, QLocale
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess
import logging
import time
from ovirtsdk4 import ConnectionBuilder, types
from functools import partial
from configparser import ConfigParser

# Getting configurations from conf.cfg file
config = ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.cfg'))

dlist = [config['domains'][i] for i in config['domains']]
url = config['url']['url']
ca = os.path.dirname(__file__) + config['paths']['ca_path']
langs = os.path.dirname(__file__) + config['paths']['langs_path']
log = os.path.dirname(__file__) + config['paths']['logs_path']


logging.basicConfig(level=logging.DEBUG, filename=log + 'ovirt.log')


class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.login_initUI()

    def login_initUI(self):

        # self.setGeometry(300, 160, 300, 200)
        self.setGeometry(300, 160, 300, 200)

        self.setWindowTitle('oVirt VDI Client')
        # self.setWindowIcon(QIcon('ovirt-icon-16.png'))
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

        self.groupBox1 = QGroupBox(self.tr("Remote Desktop"), self)
        self.groupBox1.setGeometry(QRect(10, 10, 280, 180))

        self.groupBox1.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.gridLayout = QGridLayout(self.groupBox1)

        self.label_2 = QLabel(self.tr("Username"))
        self.label_3 = QLabel(self.tr("Password"))
        self.label_4 = QLabel(self.tr("Domain"))

        self.usernameline = QLineEdit()
        self.pwline = QLineEdit()
        self.pwline.setEchoMode(QLineEdit.Password)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.usernameline, 0, 1, 1, 2)
        self.gridLayout.addWidget(self.pwline, 1, 1, 1, 2)

        self.comboBox1 = QComboBox(self.groupBox1)
        self.gridLayout.addWidget(self.comboBox1, 2, 1, 1, 2)
        self.comboBox1.addItems(dlist)

        self.btnLogin = QPushButton(self.tr("Login"))
        self.btnLogin.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        self.btnCancel = QPushButton(self.tr("Cancel"))
        self.btnCancel.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogDiscardButton')))
        self.gridLayout.addWidget(self.btnLogin, 3, 1, 2, 1)
        self.gridLayout.addWidget(self.btnCancel, 3, 2, 2, 1)
        self.groupBox1.setLayout(self.gridLayout)

        self.btnLogin.clicked.connect(self.check_form)
        self.btnCancel.clicked.connect(QApplication.instance().quit)

        self.show()

    def check_form(self):

        self.uname = self.usernameline.text()
        self.upass = self.pwline.text()

        # Creating connection builder mechanism.
        try:
            self.builder = ConnectionBuilder(
                url=url,
                username=self.uname + '@' + self.comboBox1.currentText(),
                # username=self.uname + '@internal',
                password=self.upass,
                ca_file=ca,
                # compress = True,
                # connections=2,
                # pipeline=0,
                debug=False,
                log=logging.getLogger(),
            )

            if self.uname and self.upass:

                if self.builder.build().test(raise_exception=False):
                    self.close()
                    self.manageUI = ManageDialog(self.builder)
                    self.manageUI.show()
                else:
                    QMessageBox.warning(self, " ",
                                        self.tr("Unsuccessful!!!\nUsername/Password incorrect or account is locked."))
            else:
                QMessageBox.warning(self, " ", self.tr("Username or Password cannot be empty!!!"))
        except Exception as errorconn:
            QMessageBox.warning(self, " ", str(errorconn))

class ManageDialog(QDialog):

    def __init__(self, builder):
        super().__init__()

        self.builder = builder
        self.getVMs()
        self.manage_UI()

    def getVMs(self):
        try:

            with self.builder.build() as connection:
                self.vm_list = {vm.name: vm.id for vm in connection.system_service().vms_service().list()}

        except Exception as error1:
            QMessageBox.warning(self, " ", str(error1))

    def manage_UI(self):

        self.setGeometry(620, 180, 620, 180)
        self.setWindowTitle(self.tr('oVirt VDI Client Connections'))
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

        self.groupBox2 = QGroupBox(self.tr("My Connections"), self)
        self.groupBox2.setGeometry(QRect(10, 10, 600, 160))
        self.groupBox2.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.gridLayout = QGridLayout(self.groupBox2)

        self.comboBox = QComboBox(self.groupBox2)
        self.comboBox.setGeometry(QRect(10, 30, 180, 30))
        self.comboBox.addItems(self.vm_list.keys())
        self.set_icons()

        self.widget = QWidget(self.groupBox2)
        self.widget.setGeometry(QRect(340, 30, 250, 120))

        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.btnAc = QPushButton(self.tr("Run"), self.widget)
        self.btnKapat = QPushButton(self.tr("Stop"), self.widget)
        self.btnGucukes = QPushButton(self.tr("PowerOff"), self.widget)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.btnCancel = QPushButton(self.tr("Cancel"))
        self.btnCancel.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCloseButton')))
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)

        # self.groupBox2.setLayout(self.gridLayout)

        self.widget1 = QWidget(self.groupBox2)
        self.widget1.setGeometry(QRect(144, 30, 143, 29))

        self.horizontalLayout = QHBoxLayout(self.widget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        spacerItem2 = QSpacerItem(55, 24, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)

        self.gridLayout.addWidget(self.btnAc, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.btnKapat, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.btnGucukes, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.btnCancel, 2, 2, 2, 1)

        self.btnAc.clicked.connect(partial(self.change_vm_status, mkstatus=1))
        self.btnKapat.clicked.connect(partial(self.change_vm_status, mkstatus=2))
        self.btnGucukes.clicked.connect(partial(self.change_vm_status, mkstatus=9))
        self.btnCancel.clicked.connect(QApplication.instance().quit)

        self.btnEkran = QPushButton(self.tr("Monitor"), self.widget1)
        self.btnEkran.setDefault(True)
        self.horizontalLayout.addWidget(self.btnEkran)

        self.btnEkran.clicked.connect(self.ekran_ac)
        self.btnCancel.clicked.connect(QApplication.instance().quit)

        self.change_buttons()

        self.comboBox.currentIndexChanged.connect(self.change_buttons)

        # self.show()

    def set_icons(self):
        try:

            with self.builder.build() as connection:

                for k, i in enumerate(self.vm_list):
                    vm = connection.system_service().vms_service().vm_service(self.vm_list[i])

                    if vm.get().status in (types.VmStatus.DOWN, types.VmStatus.POWERING_DOWN):
                        # self.comboBox.setItemIcon(k, QIcon("stop-16.ico"))
                        self.comboBox.setItemIcon(k, QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop'))))
                    if vm.get().status in (types.VmStatus.UP, types.VmStatus.POWERING_UP):
                        # self.comboBox.setItemIcon(k, QIcon("play-16.ico"))
                        self.comboBox.setItemIcon(k, QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))))
                    if vm.get().status == types.VmStatus.PAUSED:
                        # self.comboBox.setItemIcon(k, QIcon("pause-16.ico"))
                        self.comboBox.setItemIcon(k, QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPause'))))
                    if vm.get().status == types.VmStatus.UNKNOWN:
                        # self.comboBox.setItemIcon(k, QIcon("error-16.ico"))
                        self.comboBox.setItemIcon(k, QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning'))))
                    else:
                        pass

        except Exception as error2:
            QMessageBox.warning(self, " ", str(error2))

    def change_buttons(self):

        self.makine_adi = self.comboBox.currentText()

        try:

            with self.builder.build() as connection:

                vm = connection.system_service().vms_service().vm_service(self.vm_list[self.makine_adi])

                if vm.get().status in (types.VmStatus.DOWN, types.VmStatus.PAUSED, types.VmStatus.POWERING_DOWN):

                    self.btnAc.setEnabled(True)
                    self.btnEkran.setEnabled(False)
                    self.btnKapat.setEnabled(False)
                    self.btnGucukes.setEnabled(False)

                elif vm.get().status in (types.VmStatus.REBOOT_IN_PROGRESS, types.VmStatus.UNKNOWN,
                                         types.VmStatus.IMAGE_LOCKED, types.VmStatus.MIGRATING,
                                         types.VmStatus.NOT_RESPONDING):

                    self.btnAc.setEnabled(False)
                    self.btnEkran.setEnabled(False)
                    self.btnKapat.setEnabled(False)
                    self.btnGucukes.setEnabled(False)

                else:

                    self.btnAc.setEnabled(False)
                    self.btnEkran.setEnabled(True)
                    self.btnKapat.setEnabled(True)
                    self.btnGucukes.setEnabled(True)

        except Exception as error3:
            QMessageBox.warning(self, " ", str(error3))

    def change_vm_status(self, mkstatus):

        self.makine_adi = self.comboBox.currentText()
        self.mkstatus = mkstatus

        try:
            with self.builder.build() as connection:
                vm = connection.system_service().vms_service().vm_service(self.vm_list[self.makine_adi])

                if self.mkstatus == 1:
                    vm.start()
                    time.sleep(10)
                if self.mkstatus == 2:
                    vm.shutdown()
                    time.sleep(10)
                if self.mkstatus == 9:
                    question = QMessageBox.warning(self, self.tr('ATTENTION!!!'), self.tr(
                        "This process can cause undesirable data lost."
                        "\n\n        Do you want to proceed?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if question == QMessageBox.Yes:
                        vm.stop()
                        time.sleep(10)
                else:
                    pass
        except Exception as error4:
            QMessageBox.warning(self, " ", str(error4))

        self.change_buttons()
        self.set_icons()

    def ekran_ac(self):

        try:
            with self.builder.build() as connection:
                # check vm status. If it's up resume

                vm = connection.system_service().vms_service().vm_service(self.vm_list[self.makine_adi])
                # Find the graphic console of the virtual machine:
                # graphics_consoles_service = vm_service.graphics_consoles_service()
                graphics_consoles_service = vm.graphics_consoles_service()
                graphics_console = graphics_consoles_service.list()[0]

                # Generate the remote viewer connection file:
                console_service = graphics_consoles_service.console_service(graphics_console.id)
                remote_viewer_connection_file = console_service.remote_viewer_connection_file()
                # print(type(remote_viewer_connection_file))

                # Change fullscreen mode
                next_file = remote_viewer_connection_file.replace("fullscreen=0", "fullscreen=1")

                # Write the content to file "/tmp/remote_viewer_connection_file.vv"
                path = "/tmp/remote_viewer_connection_file.vv"

                with open(path, "w") as f:
                    # f.write(remote_viewer_connection_file)
                    f.write(next_file)

            subprocess.Popen(["remote-viewer", "/tmp/remote_viewer_connection_file.vv"])
            time.sleep(0.5)

        except Exception as error5:
            QMessageBox.warning(self, " ", str(error5))

if __name__ == '__main__':
    translator = QTranslator()
    langfile = QLocale.system().name() + '.qm'
    translator.load(langs + langfile)

    app = QApplication(sys.argv)
    app.installTranslator(translator)

    login = LoginDialog()
    sys.exit(app.exec_())
