#!/usr/bin/python3
import io
import sys
from struct import *


def wrap(msg):
    msg_len = len(msg)
    if msg_len > 65535:
        return "Message exceeds 65535 bytes."
    my_list = []
    first_byte = msg_len >> 8
    second_byte = msg_len
    my_list.append(first_byte % 256)
    my_list.append(second_byte % 256)

    # create an empty bytearray
    data_frame = bytearray([x for x in my_list])
    data_frame.extend(msg)

    return data_frame


def un_wrap(data):
    message = data.decode('utf-8', 'backslashreplace')
    return message[2:]
