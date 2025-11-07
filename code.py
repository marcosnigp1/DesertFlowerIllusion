# Desert Flower Illusion
# This file was originally the project example given by AdaFruit, for the Propmaker 2040.

import time
import board
import analogio  # For the photoresistor.
import audiocore
import audiobusio
import audiomixer
import neopixel
from digitalio import DigitalInOut, Direction, Pull # Pull suggested by ChatGPT
import adafruit_hcsr04  # We need this to get the ultrasonic sensor working.

# ------------------------------------------------------------- #
# ------------------------------------------------------------- #
# ------------------------------------------------------------- #

###############################
### BOARD CONFIGURATION  #####
##############################

# The project follows the following scheme:

#     1
#   /    \
# 2  ---  3

# Distance testing mode
testing_mode = 1

# Level of intensity
level_intensity = 0  # Starts at 0. There are 3 levels of intensity, the first one
                     # is where the main structure glitches and the rest stay quiet.
                     # On the second level, it glitches more and the rest of the devices
                     # go into level 1. On level 3, everything sets to level 3.


#ChatGPT helped me a bit here in these parts for the input and output using the Analogue connections.
#     
# Connection from one side
signal_pin_1 = DigitalInOut(board.D5)
signal_pin_1.direction = Direction.OUTPUT

receiving_pin_1 = DigitalInOut(board.D6)
receiving_pin_1.direction = Direction.INPUT
receiving_pin_1.pull = Pull.DOWN   # Ensures it reads LOW when not connected


# Connection with board 3
signal_pin_2 = DigitalInOut(board.D9)
signal_pin_2.direction = Direction.OUTPUT

receiving_pin_2 = DigitalInOut(board.D10)
receiving_pin_2.direction = Direction.INPUT
receiving_pin_2.pull = Pull.DOWN   # Ensures it reads LOW when not connected


# ------------------------------------------------------------- #
# ------------------------------------------------------------- #
# ------------------------------------------------------------- #

# Photoresistor Set-up
photoresistor = analogio.AnalogIn(board.A3)

# Function to get the values from the photoresistor.
def get_voltage(pin):
    return (
        pin.value * 3.3
    ) / 65535  # Convert 16-bit reading to volts (suggested by ChatGPT) and also taken from an earlier project I did.

# Neopixel setup:
neopixel_pin = board.EXTERNAL_NEOPIXELS  # External Neopixel pin
num_pixels = 12
pixels = neopixel.NeoPixel(neopixel_pin, num_pixels, brightness=0.8, auto_write=True)


# Enable external power pin for the Speaker.
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True  # Turn ON or OFF.

# Outputs for the ultrasonic sensor.
ultrasonic = adafruit_hcsr04.HCSR04(trigger_pin=board.SDA, echo_pin=board.SCL)

# Speaker Playback

# Mixer Options
mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
audio.play(mixer)

# ----- AUDIO FILES ---------#
audio_file = open("media/testingbeep.wav", "rb") # https://pixabay.com/sound-effects/beep-313342/
beep = audiocore.WaveFile(audio_file)


# ---- Last sound variable (to store and compare files) ---#
last_play_time = 0
last_played = None
cooldown = 2  # This will let some audios play over and over again seemingly.

# ------
#  GLOBAL VOLUME ---- #
global_volume = 0.7


# --- 
# TIME RELATED VARIABLES #
# ----

trigger_time = 10        # Seconds required.
start_time = 0           # The timer will start with 0 seconds.
start_timer = False      # This will help start the countdown of the seconds.
glitching_state = False  # For the glitching effect.
 

# -----
# You shall not pass!!!
# -----

you_shall_not_pass = False

# STARTING THE CODE!!!

while True:
    try:
        # --- Get values ----- #
        voltage = get_voltage(photoresistor)
        distance = ultrasonic.distance  # In cm
        print("Photoresistor voltage:", round(voltage, 3))
        print(f"Distance: {distance:.2f} cm")
        
        sound = beep # Play beep sound.
        

        # -------------- Light show! --------------------

        # Although lets first check if I am receiving some energy output in order to synchronize...abs
        if (receiving_pin_1.value == True or receiving_pin_2.value == True) and you_shall_not_pass == False:
            glitching_state = True
        else:
            glitching_state = False

        if distance > 0 and distance < 10:
            if glitching_state == False:
                # After the glitching state condition has been evaluated, and this is not the one that is on a glitching state, 
                # start the timer to create the effect.
                if not start_timer:
                    start_time = time.monotonic()
                    start_timer = True
                
                # Since this is not the one in a glitching state, it will keep track of the seconds until it reaches 10 seconds, where it will
                # "Synchronize" the rest of the boards.

                elapsed = time.monotonic() - start_time
                print("Seconds in range:", round(elapsed, 2))

                if elapsed >= 5:
                    # I will synchronize EVERYONE!
                    signal_pin_1.value = True
                    signal_pin_2.value = True
                    you_shall_not_pass = True # DO NOT MAKE ME YELLOW AAAA
                    # signal_pin_2.value = True
                elif elapsed <= 5:
                    signal_pin_1.value = False
                    signal_pin_2.value = False
                    you_shall_not_pass = False # DO NOT MAKE ME YELLOW AAAA
                    # signal_pin_2.value = False

                # Make sound
                global_volume = 1.0
                cooldown = 0.3

                if sound:
                    now = time.monotonic()
                    # Play sound if there is a new audio file and the cooldown has finished.
                if sound != last_played or now - last_play_time > cooldown:
                    mixer.voice[0].play(sound, loop=False)
                    mixer.voice[0].level = global_volume
                    last_played = sound
                    last_play_time = now
                
                # White, to show the other ones as affected.
                pixels.fill((255, 255, 255))

            elif glitching_state == True:
                pixels.fill((255, 255, 0)) # Testing connection.
            
        elif distance >= 11 and glitching_state == False:
            pixels.fill((255, 255, 255))
            # The person has moved away
            start_timer = False
            you_shall_not_pass = False
            signal_pin_1.value = False
            signal_pin_2.value = False

        elif distance >= 11 and glitching_state == True:
            pixels.fill((255, 255, 0)) # Testing connection.



        # -----------------------------------------------


        # This is just for testing, but I am going to check if the three devices work correctly and do not present any interference.
        """ if testing_mode == 1:
      
            if distance > 40:
                global_volume = 1.0
                if board_id == 1:
                    signal_pin_1.value = False

                cooldown = 1.0
                
            elif distance > 30:
                global_volume = 1.00
                if board_id == 1:
                    signal_pin_1.value = False

                cooldown = 0.8

            elif distance > 20:
                global_volume = 1.00
                if board_id == 1:
                    signal_pin_1.value = False

                cooldown = 0.5

            elif distance > 10:
                global_volume = 1.00
                if board_id == 1:
                    signal_pin_1.value = False

                cooldown = 0.3
            
            elif distance > 0:
                global_volume = 1.00
                if board_id == 1:
                    signal_pin_1.value = False

                cooldown = 0.1            

    
            if sound:
                now = time.monotonic()
                # Play sound if there is a new audio file and the cooldown has finished.
            if sound != last_played or now - last_play_time > cooldown:
                mixer.voice[0].play(sound, loop=False)
                mixer.voice[0].level = global_volume
                last_played = sound
                last_play_time = now """

    except RuntimeError:
        # Sometimes a reading may fail due to timeout.
        print("Retrying...")
    time.sleep(0.2)
