#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import shelve
#GPIO.output(2,GPIO.HIGH)

SHELF_FILE = "/home/pi/HomeAutomation/ExtensionBoardStatus.db"  
INITIALIZE = False
GPIO_PINS = (2,3,17,4)
SWITCH_PIN_MAP = {"a": 2, "b": 3, "c":17, "d":4}
SWITCH_NAMES = ("a", "b", "c", "d")

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        parsed_arg = urlparse.parse_qs(self.path)
        print "parsed",  parsed_arg
        try:
            print "switch called : ", parsed_arg['/switch']
            self.wfile.write("<html><body><h1>Lights on!</h1></body></html>")
            toggle_value(parsed_arg['/switch'][0])
        except:
            pass

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        print self.headers.getheader('content-type')
        varLen = int(self.headers['Content-Length'])
        content = self.rfile.read(varLen)
        print "Content : ", content

def run(server_class=HTTPServer, handler_class=S, port=80):
    try:
        init_pins()
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print 'Starting httpd...'
        httpd.serve_forever()
    finally:
        GPIO.cleanup()

def init_pins():
    shelf_values = current_switch_states()
    print "Shelf values in init_pins: ", shelf_values
    GPIO.setmode(GPIO.BCM)
    for id, i in enumerate(GPIO_PINS):
        GPIO.setup(i, GPIO.OUT)
        if shelf_values[SWITCH_NAMES[id]] == False:
            GPIO.output(i, GPIO.HIGH)
        else:
            GPIO.output(i, GPIO.LOW)

def switch_on(pin_num):
    try:
        GPIO.output(pin_num, GPIO.LOW)
        print "Light on"
    except KeyboardInterrupt:
        print "  Quit"
        # Reset GPIO settings
        GPIO.cleanup()

def switch_off(pin_num):
    try:
        GPIO.output(pin_num, GPIO.HIGH)
        print "Lights off"
    except KeyboardInterrupt:
        print "  Quit"
        # Reset GPIO settings
        GPIO.cleanup()

# Shelf functions 
def initialize_switch_state():
    switch_states  = {"a": False, "b": False, "c": False, "d": False}
    try:
        shelf = shelve.open(SHELF_FILE)
        for key,val in switch_states.items():
            shelf[key] = val
        print "Shelf values added"
    finally:
        shelf.close()

def current_switch_states():
    try:
        shelf_values = {}
        shelf = shelve.open(SHELF_FILE)
        for key,val in shelf.items():
            print "key : " + str(key) + " value: " + str(shelf[key])
            shelf_values[key] = (shelf[key])
    finally:
        shelf.close()
        return shelf_values

def toggle_value(key):
    try:
        shelf = shelve.open(SHELF_FILE)
        shelf[key] = not shelf[key]
        if shelf[key] is True:
            switch_on(SWITCH_PIN_MAP[key])
        else:
            switch_off(SWITCH_PIN_MAP[key])
    finally:
        shelf.close()

if __name__ == "__main__":
    # Run only once to initialize shelf file
    if INITIALIZE is True:
        initialize_switch_state()
        current_switch_states()
    else:
        run()
