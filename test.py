#! /usr/bin/python3
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

import unittest
import time
import signal
import sys
import subprocess
import threading
import datetime
import argparse

import d2dcnWidget

import ServiceDiscovery
import d2dcn

import weakref

import PyQt5

class container():
    pass


class mqttBroker(unittest.TestCase):

    def __init__(self):
        # Launch discover broker process
        self.broker_discover = ServiceDiscovery.daemon(d2dcn.d2dConstants.MQTT_SERVICE_NAME)
        self.broker_discover.run(True)


        # Launch broker process
        self.pro = subprocess.Popen("mosquitto", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)

        time.sleep(2)


    def __del__(self):
        self.pro.send_signal( signal.SIGTERM)
        #self.pro.send_signal(signal.SIGINT)
        self.pro.wait()


class Test_d2dcnWidget(unittest.TestCase):

    def setUp(self):
        self.app = PyQt5.QtWidgets.QApplication(sys.argv)


    def createSimulatedDevice(self, service, command_prefix, info_prefix, info_category="test"):

        simulated_device = d2dcn.d2d(service=service)
        api_result = {}
        api_result["arg1"] = {}
        api_result["arg1"]["type"] = "int"
        api_result["arg2"] = {}
        api_result["arg2"]["type"] = "string"
        api_result["arg2"]["optional"] = True
        api_result["arg3"] = {}
        api_result["arg3"]["type"] = "float"
        api_result["arg3"]["optional"] = True
        api_result["arg4"] = {}
        api_result["arg4"]["type"] = "bool"
        api_result["arg4"]["optional"] = True

        fixed_response = {}
        fixed_response["arg1"] = 1
        fixed_response["arg2"] = "test"
        fixed_response["arg3"] = 1.1
        fixed_response["arg4"] = True

        command_category = "test"

        def testEnable(enable):
            self.assertTrue(simulated_device.enableCommand(command_prefix + "5", enable))
            return {}


        self.assertTrue(simulated_device.addServiceCommand(lambda args : args, command_prefix + "1", api_result, api_result, command_category + "1"))
        self.assertTrue(simulated_device.addServiceCommand(lambda args : {}, command_prefix + "2", api_result, {}, command_category + "2"))
        self.assertTrue(simulated_device.addServiceCommand(lambda args, rv=fixed_response : rv, command_prefix + "3", {}, api_result, command_category + "3"))
        self.assertTrue(simulated_device.addServiceCommand(lambda args : testEnable(True), command_prefix + "4", {}, {}, command_category + "4"))
        self.assertTrue(simulated_device.addServiceCommand(lambda args : testEnable(False), command_prefix + "5", {}, {}, command_category + "5", False))


        def updateTread(weak_ref, info_prefix, info_category):

            int_value = 0
            float_value = 0.0
            bool_value = 0


            while True:
                sharer_ptr = weak_ref()
                if not sharer_ptr:
                    return

                sharer_ptr.publishInfo(info_prefix + "1", int_value, info_category + "1")
                sharer_ptr.publishInfo(info_prefix + "2", float_value, info_category + "2")
                sharer_ptr.publishInfo(info_prefix + "3", bool_value, info_category + "3")
                sharer_ptr.publishInfo(info_prefix + "4", datetime.datetime.now().strftime("%H:%M:%S"), info_category + "4")

                int_value += 1
                float_value += 0.5
                bool_value = not bool_value

                del sharer_ptr
                time.sleep(0.25)

        thread  = threading.Thread(target=updateTread, daemon=True, args=[weakref.ref(simulated_device), info_prefix, info_category])
        thread .start()


        return simulated_device


    def test1_testCreateDelete(self):

        def testScope():
            test = d2dcnWidget.d2dcnWidget()
            test.subscribeComands()
            test.subscribeInfo()
            weak = weakref.ref(test)
            return weak

        weak = testScope()
        self.assertTrue(weak() == None)


    def test2_DetectNewDevices(self):

        simulated_deviceA = self.createSimulatedDevice("simulatedService1", "TestsCommand_A", "TestInfo_A")
        simulated_deviceB = self.createSimulatedDevice("simulatedService2", "TestsCommand_B", "TestInfo_B")
        simulated_deviceC = self.createSimulatedDevice("simulatedService3", "TestsCommand_C", "TestInfo_C")
        simulated_deviceD = self.createSimulatedDevice("simulatedService4", "TestsCommand_D", "TestInfo_D")

        test = d2dcnWidget.d2dcnWidget()
        self.assertTrue(test.subscribeComands())
        self.assertTrue(test.subscribeInfo())

        test.show()
        self.app.exec()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--not-instance-broker',
        required=False,
        action="store_false",
        help='Not instance test broker')
    parser.add_argument('filename')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    sys.argv[1:] = args.unittest_args

    if args.not_instance_broker:
        mqtt_broker = mqttBroker()

    unittest.main()