#!/usr/bin/python
# -*- coding: utf-8 -*-

# Message structure: 2400bps using 8 databits, 1 stop bit and even parity.
# messages consist of at least 5 bytes and start with header address and followed by source address. Addresses are only used when a hub connects two or more devices.
# MSB of each byte is the IDHT (IDentify Header/Trailer bit) 1 for head/destination address byte at end of transfer byte and 0 for all bytes in between.
# David Gregory 21724425@student.uwa.edu.au

import os
import sys
import serial
import time
import binascii
from std_msgs.msg import String
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
import math

ser = serial.Serial(
    '/dev/ttyS1',
    baudrate=2400,
    timeout=5,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    )

message_base = '800022'

class Message:

    def __init__(self, msg_type):

        self.status = msg_type
        self.value = ''


Status = {  # Values are HEX values not decimal.
    'Voltage': '60',
    'Current': '61',
    'Amp Hours': '62',
    'State of Charge': '64',
    'Time Remaining': '65',
    'Temperature': '66',
    'Monitor Status': '67',
    'Aux Voltage': '68',
    }

def message(tbs_message, message):
    newValue = message_helper(tbs_message, message.status)
    value = message.value if newValue is None or newValue == 0 else newValue
    try:
        value = float(value)
        return '{0:.2f}'.format((value*100)/100)
        # return '{0:.2f}'.format(math.ceil((value*100)/100))
    except:
        return value

def message_helper(tbs_message, status):
    val = tbs_message[tbs_message.find(message_base
            + Status[status]):tbs_message.find(message_base
            + Status[status]) + 16]

    val = val[6:-2]

    if status == 'Voltage':

        return get_value(val)
    elif status == 'Current':
        # 2 DECIMAL RESOLUTION (DEFAULT)
        return get_twos_enabled(val)
    elif status == 'Amp Hours':
        # 1 DECIMAL RESOLUTION
        return get_twos_enabled(val) * 10
    elif status == 'Time Remaining':
        # TIME IS IN MINUTES
        time = get_twos_enabled(val)

        if time <= 0:
            return None
        else:
            return time * 100
    elif status == 'Temperature':
        return get_twos_enabled(val) * 10
    elif status == 'Monitor Status':
        return get_status(val, 1)
    elif status == 'Aux Voltage':
        return get_value(val)
    elif status == 'State of Charge':
        try:
            return get_value(val) * 10
        except:
            pass
    else:
        pass


def get_value(message):
    try:
        MSB = int(message[2:4], 16)
        MSB = MSB << 14
        ASB = int(message[4:6], 16)
        ASB = ASB << 7
        LSB = int(message[6:8], 16)
        return (MSB + ASB + LSB) / 100
    except:
        pass


def get_twos_enabled(message):
    try:
        MSB = int(message[2:4], 16)
        MSB = MSB << 14
        ASB = int(message[4:6], 16)
        ASB = ASB << 7
        LSB = int(message[6:8], 16)
        result = MSB + ASB + LSB
        temp = bin(result).zfill(21)
        temp = temp.replace('b', '')
        negative = temp[1:2]
        result = temp[2:]
        result = int(result, 2)
        if negative == '1':
            return -1 * result / 100
        else:
            return result / 100
    except:
        return 0

def get_status(msg, verbose):
    try:
        message = ''
        MSB = int(msg[2:4], 16)
        ASB = int(msg[4:6], 16)
        LSB = int(msg[6:8], 16)
        MSB_BIN = bin(MSB).zfill(8)
        ASB_BIN = bin(ASB).zfill(8)
        LSB_BIN = bin(LSB).zfill(8)

        if verbose:
            if MSB_BIN[1] == '1':
                message = message + ' reserved | '
            if MSB_BIN[2] == '1':
                message = message + ' reserved | '
            if MSB_BIN[3] == '1':
                message = message \
                    + ' Voltage > Auto-Sync Voltage Level | '
            if MSB_BIN[4] == '1':
                message = message \
                    + ' Current < Auto-Sync Current Level | '
            if MSB_BIN[5] == '1':
                message = message \
                    + ' Battery has been discharged far enough to let it Auto-Sync again | '
            if MSB_BIN[6] == '1':
                message = message \
                    + ' Battery monitor is outputting data in expert 501 compatibility mode | '
            if MSB_BIN[7] == '1':
                message = message \
                    + " Alarm switch triggered due to command 'Alarm switch on' | "
            if ASB_BIN[1] == '1':
                message = message + ' Backlight switched on | '
            if ASB_BIN[2] == '1':
                message = message + ' Display test switched on | '
            if ASB_BIN[3] == '1':
                message = message \
                    + ' No temperature sensor detected by battery monitor | '
            if ASB_BIN[4] == '1':
                message = message \
                    + " Auxillary battery's high voltage alarm triggered | "
            if ASB_BIN[5] == '1':
                message = message \
                    + " Auxillary battery's low voltage alarm triggered | "
            if ASB_BIN[6] == '1':
                message = message + ' Installer-lock enabled | '
            if ASB_BIN[7] == '1':
                message = message \
                    + " Main battery's high voltage alarm triggered | "
            if LSB_BIN[1] == '1':
                message = message \
                    + " Main battery's low voltage alarm triggered | "
            if LSB_BIN[2] == '1':
                message = message \
                    + ' Discharge floor reached and main battery needs charging | '
            if LSB_BIN[3] == '1':
                message = message \
                    + ' Main battery fully discharged (0.0%) | '
            if LSB_BIN[4] == '1':
                message = message \
                    + ' Main battery fully charged (100.0%) | '
            if LSB_BIN[5] == '1':
                message = message \
                    + ' Main battery needs to be charged | '
            if LSB_BIN[6] == '1':
                message = message \
                    + ' Monitor is not in sync with battery, charge battery | '
            if LSB_BIN[7] == '1':
                message = message \
                    + ' Monitor has been reset due to a poewr-loss | '
            return message
        elif not verbose:
            return msg
    except:
        pass


# ROS 2 conversion
class TBSTalker(Node):
    def __init__(self):
        super().__init__("talker")

        self.pub = self.create_publisher(String, 'tbs_meter', 10)
        
        self.timer_ = self.create_timer(0.1, self.talk)

        voltage = Message('Voltage')
        current = Message('Current')
        amp_hours = Message('Amp Hours')
        state_of_charge = Message('State of Charge')
        time_remaining = Message('Time Remaining')
        temperature = Message('Temperature')
        monitor_status = Message('Monitor Status')
        aux_voltage = Message('Aux Voltage')
        self.message_types = [
            voltage,
            current,
            amp_hours,
            state_of_charge,
            time_remaining,
            temperature,
            monitor_status,
            aux_voltage,
            ]

    def talk(self):
        # print("start | " + self.message_types[0].status)
        bytesToRead = ser.inWaiting()
        tbs_message = ser.read(bytesToRead).hex()
        n = 0
        # print(str(tbs_message))
        ros_msg = ' '

        for battery_message in self.message_types:
            battery_message.value = message(tbs_message,
                    battery_message)

            # ros_msg += str(battery_message.value)

        # flushes serial input so it doesn't have old messages stuck in it.
        ser.flushInput()

        try:
            for x in self.message_types:
                if x.status == "State of Charge" and x.value is None:
                    raise Exception("State of Charge value is None")
                ros_msg = ros_msg + str(x.status) + ': ' + str(x.value) \
                    + ' | '
            msg = String()
            msg.data = ros_msg
            self.pub.publish(msg)
        except:
            pass


def main(args=None):
    rclpy.init()
    node = TBSTalker()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
