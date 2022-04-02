'''
ESC204 2022W Widget Lab 2, Part 13
Task: Use PWM to modulate the volume (and frequency) of a buzzer noise.
'''
import board
import pwmio
import time

# set up buzzer as PWM output
buzzbuzz = pwmio.PWMOut(board.GP16, duty_cycle = 1000, frequency = 150, variable_frequency = True)

# set mode
mode = "duty"
#mode = "freq"

# run PWM while changing either duty cycle or frequency
while True:
    # cycle up and down through duty cycle values
    if mode == "duty":
        for duty in range(0,40000,1000):
            # increasing duty cycle
            buzzbuzz.duty_cycle = duty
            time.sleep(0.1)
            buzzbuzz.duty_cycle = 0
            time.sleep(0.01)

        for duty in range(40000,0,-1000):
            # decreasing duty cycle
            buzzbuzz.duty_cycle = duty
            time.sleep(0.1)
            buzzbuzz.duty_cycle = 0
            time.sleep(0.01)

    elif mode == "freq":
        # cycle up and down through frequency values
        for f in range(50,700,50):
            # increasing duty cycle
            buzzbuzz.frequency = f# Up
            time.sleep(0.1)

        for f in range(700,50,-50):
            # decreasing duty cycle
            buzzbuzz.frequency = f# Down
            time.sleep(0.1)
