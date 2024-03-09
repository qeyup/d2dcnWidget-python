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
    parser.add_argument(
        '--device-hlayout',
        required=False,
        default="",
        action="store_true",
        help='Device horizontal layout')
    parser.add_argument(
        '--category-hlayout',
        required=False,
        default="",
        action="store_true",
        help='Category object horizontal layout')
    parser.add_argument(
        '--object-hlayout',
        required=False,
        default="",
        action="store_true",
        help='Object object horizontal layout')

    parser.add_argument(
        '--ignore-command',
        required=False,
        default="",
        action="store_true",
        help='Ignore commands')
    parser.add_argument(
        '--command-mac-pattern',
        metavar = "[COMMAND_MAC_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command mac pattern')
    parser.add_argument(
        '--command-service-pattern',
        metavar = "[COMMAND_SERVICE_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command service pattern')
    parser.add_argument(
        '--command-category-pattern',
        metavar = "[COMMAND_CATEGORY_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command category pattern')
    parser.add_argument(
        '--command-name-pattern',
        metavar = "[COMMAND_NAME_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command name pattern')

    parser.add_argument(
        '--ignore-info',
        required=False,
        default="",
        action="store_true",
        help='Ignore info')
    parser.add_argument(
        '--info-mac-pattern',
        metavar = "[INFO_MAC_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command mac pattern')
    parser.add_argument(
        '--info-service-pattern',
        metavar = "[INFO_SERVICE_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command service pattern')
    parser.add_argument(
        '--info-category-pattern',
        metavar = "[INFO_CATEGORY_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command category pattern')
    parser.add_argument(
        '--info-name-pattern',
        metavar = "[INFO_NAME_PATTERN]",
        required=False,
        default="",
        help='Regular expresion for command name pattern')
    args = parser.parse_args(sys.argv[1:])


    try:
        app = QApplication(sys.argv)

        window = d2dcnWidget.d2dcnWidget(args.device_hlayout, args.category_hlayout, args.object_hlayout)
        if not args.ignore_command:
            window.subscribeComands(args.command_mac_pattern, args.command_service_pattern, args.command_category_pattern, args.command_name_pattern)

        if not args.ignore_info:
            window.subscribeInfo(args.info_mac_pattern, args.info_service_pattern, args.info_category_pattern, args.info_name_pattern)

        window.show()

        app.exec()
        del window

    except KeyboardInterrupt:
        pass


# Main execution
if __name__ == '__main__':
    main()
