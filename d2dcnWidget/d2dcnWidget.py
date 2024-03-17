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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QPushButton, QTabWidget, QFrame, QCheckBox, QDoubleSpinBox, QSpinBox, QLineEdit, QScrollArea
from PyQt5.QtCore import Qt, QEvent, QCoreApplication, QEventLoop, pyqtSignal, QTimer
from PyQt5.QtGui import QFontMetrics

import weakref

import d2dcn


version = "0.1.2"

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)


class d2dcnWidget(QWidget):
    def __init__(self, device_hlayout=False, category_hlayout=False, object_hlayout=False):
        super().__init__()
        self.__genMainLayout(device_hlayout, category_hlayout, object_hlayout)

        self.__d2dcn_client = d2dcn.d2d()
        self.__d2dcn_client.onCommandUpdate = lambda command, weak_widget=weakref.ref(self) : d2dcnWidget.__on_command_update(command, weak_widget)
        self.__d2dcn_client.onInfoUpdate = lambda info, weak_widget=weakref.ref(self) : d2dcnWidget.__on_info_update(info, weak_widget)
        self.__d2dcn_client.onCommandRemove = lambda command, weak_widget=weakref.ref(self) : d2dcnWidget.__on_command_remove(command, weak_widget)
        self.__d2dcn_client.onInfoRemove = lambda info, weak_widget=weakref.ref(self) : d2dcnWidget.__on_info_remove(info, weak_widget)

        self.resize(500,500)


    def __del__(self):
        del self.__d2dcn_client


    def __genMainLayout(self, device_hlayout, category_hlayout, object_hlayout):

        self.__not_use_layout = QHBoxLayout()
        self.__not_use_layout.setSpacing(0)
        self.__not_use_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__not_use_layout)

        self.__scroll_widget = QWidget()
        self.__main_layout = QHBoxLayout()
        self.__scroll_widget.setLayout(self.__main_layout)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__scroll_widget)
        self.__not_use_layout.addWidget(self.__scroll_area)

        self.__service_view = serviceView(device_hlayout, category_hlayout, object_hlayout)
        self.__main_layout.addWidget(self.__service_view)


    def __on_info_update(info, d2dcn_widget_weak):
        d2dcn_widget = d2dcn_widget_weak()
        if d2dcn_widget:
            QCoreApplication.postEvent(d2dcn_widget.__service_view, serviceView.addServiceInfoEvent(info))


    def __on_command_update(command, d2dcn_widget_weak):
        d2dcn_widget = d2dcn_widget_weak()
        if d2dcn_widget:
            QCoreApplication.postEvent(d2dcn_widget.__service_view, serviceView.addServiceCommandEvent(command))


    def __on_info_remove(info, d2dcn_widget_weak):
        d2dcn_widget = d2dcn_widget_weak()
        if d2dcn_widget:
            QCoreApplication.postEvent(d2dcn_widget.__service_view, serviceView.removeServiceInfoEvent(info))


    def __on_command_remove(command, d2dcn_widget_weak):
        d2dcn_widget = d2dcn_widget_weak()
        if d2dcn_widget:
            QCoreApplication.postEvent(d2dcn_widget.__service_view, serviceView.removeServiceCommandEvent(command))


    def subscribeComands(self, mac:str="", service:str="", category:str="", command:str="") -> bool:
        return self.__d2dcn_client.subscribeComands(mac, service, category, command)


    def subscribeInfo(self, mac:str="", service:str="", category="", name:str="") -> bool:
        return self.__d2dcn_client.subscribeInfo(mac, service, category, name)


class lateralPanel(QWidget):
    def __init__(self):
        super().__init__()


class serviceView(QWidget):

    class addServiceCommandEvent(QEvent):
        def __init__(self, command):
            super().__init__(QEvent.User)
            self.command = command

    class removeServiceCommandEvent(QEvent):
        def __init__(self, command):
            super().__init__(QEvent.User)
            self.command = command

    class addServiceInfoEvent(QEvent):
        def __init__(self, info):
            super().__init__(QEvent.User)
            self.info = info

    class removeServiceInfoEvent(QEvent):
        def __init__(self, info):
            super().__init__(QEvent.User)
            self.info = info


    def __init__(self, device_hlayout, category_hlayout, object_hlayout):
        super().__init__()
        self.__service_widget_map = {}

        self.__object_hlayout = object_hlayout
        self.__category_hlayout = category_hlayout

        if device_hlayout:
            self.__main_layout = QHBoxLayout()
        else:
            self.__main_layout = QVBoxLayout()

        self.__main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(self.__main_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def event(self, event):
        if isinstance(event, serviceView.addServiceCommandEvent):
            self.addServiceCommand(event.command)

        elif isinstance(event, serviceView.addServiceInfoEvent):
            self.addServiceInfo(event.info)

        elif isinstance(event, serviceView.removeServiceCommandEvent):
            self.removeServiceCommand(event.command)

        elif isinstance(event, serviceView.removeServiceInfoEvent):
            self.removeServiceInfo(event.info)

        else:
            return super().event(event)

        return True


    def generateServiceUID(self, device_mac, service_name):
        return device_mac + "/" + service_name


    def addService(self, device_mac, service_name):
        self.removeService(device_mac, service_name)
        widget = service(device_mac, service_name, self.__category_hlayout, self.__object_hlayout)
        self.__service_widget_map[self.generateServiceUID(device_mac, service_name)] = widget
        self.__main_layout.addWidget(widget)


    def removeService(self, device_mac, service_name):
        uid = self.generateServiceUID(device_mac, service_name)
        if not uid in self.__service_widget_map:
            return

        self.__main_layout.removeWidget(self.__service_widget_map[uid])
        self.__service_widget_map.remove(uid)


    def addServiceInfo(self, info_obj):
        uid = self.generateServiceUID(info_obj.mac, info_obj.service)
        if uid not in self.__service_widget_map:
            self.addService(info_obj.mac, info_obj.service)

        widget = self.__service_widget_map[uid]
        widget.addInfo(info_obj)


    def removeServiceInfo(self, info_obj):
        uid = self.generateServiceUID(info_obj.mac, info_obj.service)
        if uid not in self.__service_widget_map:
            return

        widget = self.__service_widget_map[uid]
        widget.removeInfo(info_obj)


    def addServiceCommand(self, command_obj):
        uid = self.generateServiceUID(command_obj.mac, command_obj.service)
        if uid not in self.__service_widget_map:
            self.addService(command_obj.mac, command_obj.service)

        widget = self.__service_widget_map[uid]
        widget.addCommand(command_obj)


    def removeServiceCommand(self, command_obj):
        uid = self.generateServiceUID(command_obj.mac, command_obj.service)
        if uid not in self.__service_widget_map:
            return

        widget = self.__service_widget_map[uid]
        widget.removeCommand(command_obj)


class service(QTabWidget):

    def __init__(self, device_mac, service_name, category_hlayout, object_hlayout):
        super().__init__()
        self.__device_mac = device_mac
        self.__service_name = service_name
        self.__object_hlayout = object_hlayout
        self.__category_hlayout = category_hlayout
        widget_main = QWidget()
        self.addTab(widget_main, service_name + " (" + device_mac + ")")

        self.__info_widget_map = {}
        self.__info_widget_category_map = {}
        self.__command_widget_map = {}
        self.__command_widget_category_map = {}

        self.__main_layout = QHBoxLayout()
        widget_main.setLayout(self.__main_layout)

        self.__info_widget = QWidget()
        self.__info_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__info_widget.hide()

        if object_hlayout:
            self.__info_layout = QHBoxLayout()
        else:
            self.__info_layout = QVBoxLayout()

        self.__info_layout.setAlignment(Qt.AlignTop)
        self.__info_widget.setLayout(self.__info_layout)
        self.__main_layout.addWidget(self.__info_widget)

        self.__dif_line = QVLine()
        self.__main_layout.addWidget(self.__dif_line)
        self.__dif_line.hide()

        self.__command_widget = QWidget()
        self.__command_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__command_widget.hide()

        if object_hlayout:
            self.__command_layout = QHBoxLayout()
        else:
            self.__command_layout = QVBoxLayout()

        self.__command_layout.setAlignment(Qt.AlignTop)
        self.__command_widget.setLayout(self.__command_layout)
        self.__main_layout.addWidget(self.__command_widget)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


    def addInfo(self, info_obj):

        if info_obj.name not in self.__info_widget_map:

            if info_obj.category not in self.__info_widget_category_map:
                category_container = QWidget()
                if self.__category_hlayout:
                    category_container_layout = QHBoxLayout()
                else:
                    category_container_layout = QVBoxLayout()
                category_container_layout.setSpacing(0)
                category_container_layout.setContentsMargins(0, 0, 0, 0)
                category_container_layout.setAlignment(Qt.AlignTop)
                category_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                category_container.setLayout(category_container_layout)
                self.__info_widget_category_map[info_obj.category] = category_container_layout

                if len(self.__info_widget_category_map) >= 2:
                    if self.__object_hlayout:
                        self.__info_layout.addWidget(QVLine())
                    else:
                        self.__info_layout.addWidget(QHLine())

                self.__info_layout.addWidget(category_container)

            else:
                category_container_layout = self.__info_widget_category_map[info_obj.category]

            widget = fieldOutput(info_obj.name, info_obj.valueType, info_obj.value)
            self.__info_widget_map[info_obj.name] = widget
            category_container_layout.addWidget(widget)

        else:
            self.__info_widget_map[info_obj.name].update(info_obj.value)

        self.__info_widget.show()
        if len(self.__info_widget_map) > 0 and len(self.__command_widget_map) > 0:
            self.__dif_line.show()


    def removeInfo(self, info_obj):
        if info_obj.name in self.__info_widget_map:
            self.__info_widget_map.pop(info_obj.name).deleteLater()


    def addCommand(self, command_obj):

        if command_obj.name not in self.__command_widget_map:

            if command_obj.category not in self.__command_widget_category_map:
                category_container = QWidget()
                if self.__category_hlayout:
                    category_container_layout = QHBoxLayout()
                else:
                    category_container_layout = QVBoxLayout()
                category_container_layout.setSpacing(0)
                category_container_layout.setContentsMargins(0, 0, 0, 0)
                category_container_layout.setAlignment(Qt.AlignTop)
                category_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                category_container.setLayout(category_container_layout)
                self.__command_widget_category_map[command_obj.category] = category_container_layout

                if len(self.__command_widget_category_map) >= 2:
                    if self.__object_hlayout:
                        self.__command_layout.addWidget(QVLine())
                    else:
                        self.__command_layout.addWidget(QHLine())

                self.__command_layout.addWidget(category_container)

            else:
                category_container_layout = self.__command_widget_category_map[command_obj.category]


            widget = serviceCommand(command_obj)
            self.__command_widget_map[command_obj.name] = widget
            category_container_layout.addWidget(widget)

        else:
            self.__command_widget_map[command_obj.name].update(command_obj)

        self.__command_widget.show()
        if len(self.__info_widget_map) > 0 and len(self.__command_widget_map) > 0:
            self.__dif_line.show()


    def removeCommand(self, command_obj):
        if command_obj.name in self.__command_widget_map:
            self.__command_widget_map.pop(command_obj.name).deleteLater()


class fieldOutput(QWidget):
    def __init__(self, name, valueType, value, scroll_time=250):
        super().__init__()

        self.__main_layout = QHBoxLayout()
        self.__value_label = QLineEdit()
        self.__value_label.setReadOnly(True)
        self.__value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.__value_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.__valueType = valueType

        self.setLayout(self.__main_layout)
        tag_label = QLabel(name + ": ")
        tag_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        tag_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.__main_layout.addWidget(tag_label)
        self.__main_layout.addWidget(self.__value_label)
        self.update(value)

        if scroll_time > 0:
            self.__update_timer = QTimer()
            self.__update_timer.timeout.connect(self.scrollTextStep)
            self.__update_timer.start(scroll_time)


    def scrollTextStep(self):
        if self.__value_label.hasSelectedText():
            return

        cursor_pos = self.__value_label.cursorPosition()
        if cursor_pos == len(self.__value_label.text()):
            cursor_pos = 0

        elif cursor_pos == 0:
            font_metric = QFontMetrics(self.__value_label.font())
            pix_pos = 0
            for c in self.__value_label.text():
                char_pix = font_metric.horizontalAdvance(c)
                pix_pos += char_pix
                cursor_pos += 1
                if pix_pos >= self.__value_label.width() - (5 * char_pix):
                    break

        else:
            cursor_pos += 1

        self.__value_label.setCursorPosition(cursor_pos)


    def resizeEvent(self, event):
        self.__value_label.setCursorPosition(0)
        super().resizeEvent(event)


    def update(self, value):

        if self.__valueType == d2dcn.d2dConstants.valueTypes.BOOL:
            self.__value_label.setText(str(value))

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.FLOAT:
            self.__value_label.setText(str(value))

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.INT:
            self.__value_label.setText(str(value))

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.STRING:
            self.__value_label.setText(value)

        else:
            self.__value_label.setText("unknown type")

        text_lenght = len(self.__value_label.text()) * 8
        if text_lenght < 100:
            self.__value_label.setMinimumWidth(text_lenght)

        else:
            self.__value_label.setMinimumWidth(100)


class fieldInput(QWidget):

    class CLineEdit(QLineEdit):

        clicked = pyqtSignal()

        def __init__(self):
            super().__init__()

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            self.clicked.emit()

    class CDoubleSpinBox(QDoubleSpinBox):

        def __init__(self):
            super().__init__()
            c_line_edit = fieldInput.CLineEdit()
            c_line_edit.clicked.connect(self.updateDecimal)
            self.setLineEdit(c_line_edit)
            self.setMaximum(2147483647)
            self.setMinimum(-2147483648)


        def updateDecimal(self):

            cursor_pos = self.lineEdit().cursorPosition()
            total_nums_digs = len(self.lineEdit().text()) - 1
            int_digs = total_nums_digs - self.decimals()

            if cursor_pos -1 > int_digs:
                offset = cursor_pos - 1
            else:
                offset = cursor_pos

            exponent = self.decimals() - (total_nums_digs - offset)
            min_step = 1 / (10**exponent)
            self.setSingleStep(min_step)

    class CSpinBox(QSpinBox):

        def __init__(self):
            super().__init__()
            c_line_edit = fieldInput.CLineEdit()
            c_line_edit.clicked.connect(self.updateDecimal)
            self.setLineEdit(c_line_edit)
            self.setMaximum(2147483647)
            self.setMinimum(-2147483648)

        def updateDecimal(self):

            cursor_pos = self.lineEdit().cursorPosition()
            digits = len(self.lineEdit().text())
            exp = digits - cursor_pos
            min_step = 10**exp if exp > 0 else 1
            self.setSingleStep(min_step)


    class CLabel(QLabel):

        clicked = pyqtSignal()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            self.clicked.emit()


    def __init__(self, name, valueType, optional):
        super().__init__()

        self.__main_layout = QHBoxLayout()
        self.__valueType = valueType
        self.__enable = True


        self.setLayout(self.__main_layout)
        tag_label = fieldInput.CLabel(name + ": ")
        tag_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        tag_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.__main_layout.addWidget(tag_label)


        if self.__valueType == d2dcn.d2dConstants.valueTypes.BOOL:
            self.__input_widget = QCheckBox()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.FLOAT:
            self.__input_widget = fieldInput.CDoubleSpinBox()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.INT:
            self.__input_widget = fieldInput.CSpinBox()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.STRING:
            self.__input_widget = QLineEdit()

        else:
            self.__input_widget = QLineEdit("Unknown type")

        self.__input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.__main_layout.addWidget(self.__input_widget)


        if optional:
            self.__enableDisableOptional()
            tag_label.clicked.connect(self.__enableDisableOptional)


    def __enableDisableOptional(self):
        self.__enable = not self.__enable

        if self.__valueType == d2dcn.d2dConstants.valueTypes.BOOL:
            self.__input_widget.setEnabled(self.__enable)

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.FLOAT:
            self.__input_widget.setEnabled(self.__enable)

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.INT:
            self.__input_widget.setEnabled(self.__enable)

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.STRING:
            self.__input_widget.setEnabled(self.__enable)

        else:
            self.__input_widget.setEnabled(self.__enable)


    def getValue(self):

        if not self.__enable:
            return None

        if self.__valueType == d2dcn.d2dConstants.valueTypes.BOOL:
            return self.__input_widget.isChecked()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.FLOAT:
            return self.__input_widget.value()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.INT:
            return self.__input_widget.value()

        elif self.__valueType == d2dcn.d2dConstants.valueTypes.STRING:
            return self.__input_widget.text()

        else:
            return self.__input_widget.text()


class serviceCommand(QWidget):
    def __init__(self, command_obj):
        super().__init__()

        self.__main_layout = QHBoxLayout()
        self.setLayout(self.__main_layout)
        self.__exec_buttom = QPushButton()
        self.__main_layout.addWidget(self.__exec_buttom)
        self.__commad_exec_widget = commandExecution(command_obj)
        self.__exec_buttom.setText(command_obj.name)
        self.__exec_buttom.setEnabled(command_obj.enable)
        self.__exec_buttom.clicked.connect(lambda : self.__commad_exec_widget.runCommand())


    def update(self, command_obj):
        self.__exec_buttom.setEnabled(command_obj.enable)
        self.__commad_exec_widget.upateCommand(command_obj)


class commandExecution(QWidget):

    def __init__(self, command_obj):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.resize(self.sizeHint())


        self.__command_obj = command_obj

        self.__main_layout = QHBoxLayout()
        self.setLayout(self.__main_layout)


    def upateCommand(self, command_obj):
        self.__command_obj = command_obj


    def runCommand(self):

        if len(self.__command_obj.params) > 0:
            self.show()
            command_args = commandArgs(self.__command_obj.params)
            self.__main_layout.addWidget(command_args)
            args = command_args.getArgs()

        else:
            args = {}
        response = self.__command_obj.call(args)
        if not response.error and len(response) == 0:
            self.hide()
        else:
            self.show()
            command_response = commmandResponse(self.__command_obj.response, response)
            command_response.exit_buttom.clicked.connect(self.hide)
            self.__main_layout.addWidget(command_response)


    def hideEvent(self, event):
        super().hideEvent(event)
        for i in range(self.__main_layout.count()):
            item = self.__main_layout.takeAt(i)
            if item and item.widget():
                item.widget().deleteLater()


class commandArgs(QWidget):

    def __init__(self, args_map):
        super().__init__()


        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

        self.__input_fields = {}
        for arg in args_map:
            valueType = args_map[arg][d2dcn.d2dConstants.infoField.TYPE]
            optional = d2dcn.d2dConstants.infoField.OPTIONAL in args_map[arg] and args_map[arg][d2dcn.d2dConstants.infoField.OPTIONAL]
            field_input = fieldInput(arg, valueType, optional)
            self.__input_fields[arg] = field_input
            self.__main_layout.addWidget(field_input)

        expanding_widget = QWidget()
        expanding_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__main_layout.addWidget(expanding_widget)

        self.loop = QEventLoop()
        self.exit_buttom = QPushButton("Execute")
        self.exit_buttom.clicked.connect(self.deleteLater)
        self.exit_buttom.clicked.connect(self.loop.quit)
        self.__main_layout.addWidget(self.exit_buttom)


    def getArgs(self):

        self.loop.exec()

        args = {}
        for input_field in self.__input_fields:
            value = self.__input_fields[input_field].getValue()
            if value != None:
                args[input_field] = value

        return args


class commmandResponse(QWidget):

    def __init__(self, resonse_proto, response_map):
        super().__init__()

        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

        label = QLabel()
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if response_map.error:
            label.setText(response_map.error)
            self.__main_layout.addWidget(label)

        else:
            if len(response_map) == 0:
                label.setText("Done!")
                self.__main_layout.addWidget(label)

            else:
                for response in response_map:
                    if response not in resonse_proto:
                        label = QLabel("Invalid field " + response)

                    else:
                        item = fieldOutput(response, resonse_proto[response][d2dcn.d2dConstants.infoField.TYPE], response_map[response])

                    self.__main_layout.addWidget(item)

        expanding_widget = QWidget()
        expanding_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__main_layout.addWidget(expanding_widget)

        self.exit_buttom = QPushButton("Close")
        self.exit_buttom.clicked.connect(self.deleteLater)
        self.__main_layout.addWidget(self.exit_buttom)
