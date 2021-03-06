# coding: utf-8

import os
import logging
import serial
import database
import config
from datetime import datetime

# Plant IDs in the order they are connected to the Arduino


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.join(
                        config.OUT_FOLDER, 'arduino_serial.log'),
                    filemode='w')


def process_line(line):
    # Read a line received via serial and return measurements as list
    rv = None
    kind = line[:line.index(" ")]
    msg = line[line.index(" ") + 1:]

    if kind == "status":
        logging.info("Arduino: {}".format(msg))
    elif kind == "measurement":
        logging.info("Measured {}".format(msg))
        rv = msg.split(",")
    return rv


def read_serial():
    logging.info("Connecting to Arduino...")
    ser = serial.Serial(config.SERIAL_DEVICE, 9600)
    while True:
        yield ser.readline().decode('ascii').strip()


def run():
    try:
        for line in read_serial():
            msg = process_line(line)
            if msg:
                dt = datetime.now().isoformat()
                for i, plant in enumerate(config.PLANTS_CONNECTED):
                    logging.debug("{}: plant {} value {}".format(
                        msg, plant, msg[i]))
                    database.store_measurements(plant, msg[i], dt)
    except KeyboardInterrupt:
        logging.info("Closing serial monitor")


if __name__ == "__main__":
    run()
