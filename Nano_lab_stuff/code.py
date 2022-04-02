'''
ESC204 2022W Widget Lab 2, Part 13
Task: Use PWM to modulate the volume (and frequency) of a buzzer noise.
'''
import board
import pwmio
import time

# set up buzzer as PWM output
buzzbuzz = pwmio.PWMOut(board.TX, duty_cycle = 1000, frequency = 150, variable_frequency = True)

# set mode
#mode = "duty"
#mode = "freq"
mode = "neo"

notes = {'a':220, 'b':247, 'C':262, 'C#':277, 'D':294, 'D#':277, 'E':330,'F':349, 'F#':370, 'G':392, 'G#': 466, 'A':440, 'A#':932, 'B':494}
score_lamb = "EDCDEEEDDDEGGEDCDEEECDDEDC"
note_duration_lamb = "11111121121121111111111114"
score_sandstorm = "bbbbbbbbbbbbEEEEEEEDDDDDDDaabbbbbbbbbbbbEEbbbbbbbbbbbEE"
note_duration_sandstorm = "1111211111121111112111111211111121111112111111211111122"

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

    elif mode == "neo":
        i = 0
        for note in score_sandstorm:
            duration = (int(note_duration_sandstorm[i]))/8.5
            if note == 'R':
                buzzbuzz.duty_cycle = 0
                time.sleep(duration)
            else:
                buzzbuzz.duty_cycle = 2**12
                buzzbuzz.frequency = notes[note]
                print(notes[note])
                time.sleep(duration)
                buzzbuzz.duty_cycle = 0
                time.sleep(0.005)
            i += 1
        #buzzbuzz.duty_cycle = 0
        #time.sleep(5)
