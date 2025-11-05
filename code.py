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
### WHICH BOARD IS THIS? #####
##############################

# The project follows the following scheme:

#     1
#   /    \
# 2  ---  3

# So please assign the board number here:
board_id = 1


# Ok now that I know which board I am, I will now prepared the inputs and outputs:

#ChatGPT helped me a bit here in these parts for the input and output using the Analogue connections.
if board_id == 1:
    signal_pin1 = DigitalInOut(board.D5)
    signal_pin1.direction = Direction.OUTPUT

    receiving_pin1 = DigitalInOut(board.D6)
    receiving_pin1.direction = Direction.INPUT
    receiving_pin1.pull = Pull.DOWN   # Ensures it reads LOW when not connected


elif board_id == 2:
    receiving_pin2 = DigitalInOut(board.D6)
    receiving_pin2.direction = Direction.INPUT
    receiving_pin2.pull = Pull.DOWN  # Ensures it reads LOW when not connected


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


while True:
    # Print ultrasonic sensor values.
    # Get distance.
    try:

        if board_id == 2:
            if receiving_pin2.value:
                # Send this to neopixel!
                pixels.fill((255, 255, 255))
            else:
                # No signal :(
                pixels.fill((0, 0, 0))

        # --- Get values ----- #
        voltage = get_voltage(photoresistor)
        distance = ultrasonic.distance  # In cm
        print("Photoresistor voltage:", round(voltage, 3))
        print(f"Distance: {distance:.2f} cm")
        
        sound = beep # Play beep sound.if


        # This is just for testing, but I am going to check if the three devices work correctly and do not present any interference.
        
              
        if distance > 40:
            global_volume = 1.0
            if board_id == 1:
                signal_pin1.value = False

            cooldown = 1.0
            
        elif distance > 30:
            global_volume = 1.00
            if board_id == 1:
                signal_pin1.value = False

            cooldown = 0.8

        elif distance > 20:
            global_volume = 1.00
            if board_id == 1:
                signal_pin1.value = False

            cooldown = 0.5

        elif distance > 10:
            global_volume = 1.00
            if board_id == 1:
                signal_pin1.value = False

            cooldown = 0.3
        
        elif distance > 0:
            global_volume = 1.00
            if board_id == 1:
                signal_pin1.value = True

            cooldown = 0.1            

  
        if sound:
            now = time.monotonic()
            # Play sound if there is a new audio file and the cooldown has finished.
        if sound != last_played or now - last_play_time > cooldown:
            mixer.voice[0].play(sound, loop=False)
            mixer.voice[0].level = global_volume
            last_played = sound
            last_play_time = now

    except RuntimeError:
        # Sometimes a reading may fail due to timeout.
        print("Retrying...")
    time.sleep(0.2)
