import os,time,serial,select,random,errno

FIFO_PATH = "cgififo"
SERIAL_PORT = "/dev/ttyACM0"
TRIGGER_HOLDOFF = 3

last_trigger_time = 0.0
ser = ''


def playSound(sound):
    os.system("mpg123 sounds/" + sound)
    print "Playing: ",sound

def lightOn():
    global ser
    ser.write('1')
    print "Light On"

def lightOff():
    global ser
    ser.write('0')
    print "Light Off"

def lightBlink():
    global ser
    ser.write('2')
    print "Light Blink"

def playExterminate():
    playSound("exterminate.mp3")
    time.sleep(0.5)
    playSound("exterminate.mp3")

def playTheme():
    playSound("theme.mp3")

def playTardis():
    playSound("tardis.mp3")

light_map = {0:lightOn, 1:lightOff, 2:lightBlink}
sound_map = {1:playExterminate, 2:playTardis, 3:playTheme}

def exterminate():
    lightOff()
    playExterminate()
    lightOn()

def theme():
    lightOn()
    playTheme()

def tardis():
    lightBlink()
    playTardis()
    lightOn()

actions = [theme, exterminate, tardis]

def trigger_action():
    global last_trigger_time

    # Only trigger another action if the holdoff time has passed
    if (time.time() - last_trigger_time) > TRIGGER_HOLDOFF:
        print "Trigger"
        random.choice(actions)()
        last_trigger_time = time.time()

def main():
    global ser
    triggerEnabled = True

    # Set volume to 100%
    os.system("./vol 100")

    # Create the input FIFO if it doesn't already exist
    if os.path.exists(FIFO_PATH):
        os.unlink(FIFO_PATH)

    os.umask(0)
    os.mkfifo(FIFO_PATH, 0666)

    # Open to FIFO for reading
    input_fifo = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)

    # Open the Arduino serial port
    ser = serial.Serial(SERIAL_PORT, 115200, timeout=0 )

    # Create the list of file descriptors to wait on
    waitlist = [input_fifo, ser]

    while True:
        # Wait until some data is received
        select.select(waitlist, [], [], 1)

        # Process serial port bytes
        last_read = ''
        while True:
            ser_in = ser.read()

            if not ser_in:
                if last_read == 'T':
                    if triggerEnabled == True:
                        print "Trigger"
                        trigger_action()
                break

            last_read = ser_in

	# Process CGI input
	while True:
	    try:
    	        cgi_in = os.read(input_fifo, 1)
	    except OSError as err:
    	        if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                    cgi_in = None
                else:
                    raise  # something else has happened -- better reraise

            if cgi_in is None or cgi_in == "":
                break

            cgi_in = ord(cgi_in)

            if (cgi_in >> 7 == 1):
                triggerEnabled = True
            else:
                triggerEnabled = False

            light = cgi_in >> 4 & 0x7
            sound = cgi_in & 0xF

            light_map[light]()
            if sound != 0:
              sound_map[sound]()

    # Close the serial port and FIFO
    ser.close()
    os.unlink(FIFO_PATH)

if __name__ == "__main__":
    main()
