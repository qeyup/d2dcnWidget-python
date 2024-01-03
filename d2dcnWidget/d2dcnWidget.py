# 
# This file is part of the d2dcnWidget distribution.
# Copyright (c) 2023 Javier Moreno Garcia.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton
from PyQt5.QtCore import Qt, QByteArray, QBuffer
from PyQt5.QtGui import QColor, QPalette, QPixmap, QGuiApplication, QImage, QImageReader

import d2dcn


version = "0.1.0"


class d2dcnWidget(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        test = QPushButton("test")
        layout.addWidget(test)

        test = QPushButton("test")
        layout.addWidget(test)

        test = QPushButton("test")
        layout.addWidget(test)

        d2dcn_client = d2dcn.d2d()



