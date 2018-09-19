import time
import pigpio
import pprint

# read temperature program from file
program = []
with open("tempman.program", "r") as p:
    data = p.readlines()
    for line in data:
        program.append(line.split(","))
p.close()

# open pi connection and init temp sensor
pi = pigpio.pi()
if not pi.connected:
    exit(0)
sensor = pi.spi_open(2, 1000000, 256)  # CE2 on auxiliary SPI

# define temp read function


def get_temperature():
    c, d = pi.spi_read(sensor, 2)
    if c == 2:
        word = (d[0] << 8) | d[1]
        if (word & 0x8006) == 0:  # Bits 15, 2, and 1 should be zero.
            t = (word >> 3)/4.0
            pprint.pprint(t)
            #print("{:.2f}".format(t))
        else:
            print("bad reading {:b}".format(word))
    time.sleep(0.25)  # Don't try to read more often than 4 times a second.
    return t

# define heater on function
def heat_on():
    return

# define heater off function
def heat_off():
    return

# define regime calculate function
def regime_calc(current_temp, target_temp, regime_time):
    step = (target_temp - current_temp) / regime_time
    if step < 0:
        direction = -1
    else:
        direction = 1
    return [step, direction]


# execute program
for regime in program:
    regime_time = regime[0]
    target_temp = regime[1]
    seconds_run = 0
    temp_step, direction = regime_calc(
        get_temperature(), target_temp, regime_time)
    last_temp = get_temperature()

    while seconds_run <= regime_time:
        current_temp = get_temperature()
        if last_temp + temp_step > current_temp:
            if 1 == direction:
                heat_on()
            else:
                heat_off()
        else:
            if 1 == direction:
                heat_off()
            else:
                heat_on()
        last_temp = current_temp
        seconds_run += 1


# finish up and close resources
heat_off()
pi.spi_close(sensor)
pi.stop()
