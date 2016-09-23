#!/usr/bin/python
import cgi,sys,cgitb,os

FIFO_PATH = "/home/pi/tardis/cgififo"
cgitb.enable()

lightmodes = {"on":0, "off":1, "blink":2}
sounds = {"none":0, "exterminate":1, "tardis":2, "theme":3}

form = cgi.FieldStorage()
light_mode = form.getfirst("lightmode")
sound = form.getfirst("sound")

if form.getfirst("triggerenabled") == "on":
    trigger = 1
else:
    trigger = 0

control_byte = (lightmodes[light_mode] << 4 | sounds[sound] | trigger << 7)

print "Status: 204 No Response", "\n\n"
print "Content-type: text/plain", "\n"
#print "You Submitted: " + light_mode + " " + sound + " 0x%x"%control_byte

fifo = os.open(FIFO_PATH, os.O_WRONLY)

os.write(fifo,bytearray([control_byte]))
os.close(fifo)
