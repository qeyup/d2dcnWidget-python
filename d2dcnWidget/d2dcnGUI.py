#! /usr/bin/env python3
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

from PyQt5.QtWidgets import QApplication
import d2dcnWidget
import argparse
import sys

def main():


    parser = argparse.ArgumentParser(description="d2dcn GUI")
    args = parser.parse_args(sys.argv[1:])

    try:
        app = QApplication(sys.argv)

        window = d2dcnWidget.d2dcnWidget()
        window.show()

        app.exec()

    except KeyboardInterrupt:
        pass


# Main execution
if __name__ == '__main__':
    main()
