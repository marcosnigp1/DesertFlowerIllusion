# "Desert Rose Illusion Project" by Elora, Keya, Mirette and Marcos.
# This file was originally the project example given by AdaFruit, for the Propmaker 2040.

import time
import board
import analogio  # For the photoresistor.
import audiocore
import audiobusio
import audiomixer
import neopixel
from digitalio import DigitalInOut, Direction, Pull  # Pull suggested by ChatGPT
import adafruit_hcsr04  # We need this to get the ultrasonic sensor working.

# ------------------------------------------------------------- #
# ------------------------------------------------------------- #
# ------------------------------------------------------------- #

###############################
### BOARD CONFIGURATION  #####
##############################

# The project follows the following scheme:


#     B    <---- The one with the photoresistor.
#   /    \
# A  ---  C


# Level of intensity
level_intensity = 0  # Starts at 0. There are 3 levels of intensity, the first one
# is where the main structure glitches and the rest stay quiet.
# On the second level, it glitches more and the rest of the devices
# go into level 1. On level 3, everything sets to level 3.


# ChatGPT helped me a bit here in these parts for the input and output using the Analogue connections.

# Connection from one side
signal_pin_1 = DigitalInOut(board.D5)
signal_pin_1.direction = Direction.OUTPUT

receiving_pin_1 = DigitalInOut(board.D6)
receiving_pin_1.direction = Direction.INPUT
receiving_pin_1.pull = (
    Pull.DOWN
)  # Ensures it reads LOW when not connected or not receiving signal.


# Connection from the other side
signal_pin_2 = DigitalInOut(board.D9)
signal_pin_2.direction = Direction.OUTPUT

receiving_pin_2 = DigitalInOut(board.D10)
receiving_pin_2.direction = Direction.INPUT
receiving_pin_2.pull = (
    Pull.DOWN
)  # Ensures it reads LOW when not connected or not receiving signal.


# ------------------------------------------------------------- #
# ------------------------------------------------------------- #
# ------------------------------------------------------------- #

# Photoresistor Set-up
photoresistor = analogio.AnalogIn(board.A3)


# Function to get the values from the photoresistor.
def get_voltage(pin):
    return (
        (pin.value * 3.3) / 65535
    )  # Convert 16-bit reading to volts (suggested by ChatGPT) and also taken from an earlier project I (Marcos) did.


# Neopixel setup:
neopixel_pin = board.EXTERNAL_NEOPIXELS  # External Neopixel pin
num_pixels = 60  # 170 pixels per structure.
pixels = neopixel.NeoPixel(
    neopixel_pin, num_pixels, brightness=1, auto_write=True
)  # Some boards will require the pixel_order=neopixel.GRBW added in order to properly display the colors with neopixel.fill((R,G,B))


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

audio_file0 = open("media/noGlitch.wav", "rb")  # https://freesound.org/s/535934/
noglitch_audio = audiocore.WaveFile(audio_file0)

# Level 1 Glitching
audio_file1 = open("media/level1glitch.wav", "rb")  # https://freesound.org/s/535934/
level1glitch_audio = audiocore.WaveFile(audio_file1)

# Level 2 Glitching
audio_file2 = open("media/level2glitch.wav", "rb")  # https://freesound.org/s/820020/
level2glitch_audio = audiocore.WaveFile(audio_file2)

# Level 3 Glitching
audio_file3 = open("media/level3glitch.wav", "rb")  # https://freesound.org/s/820020/
level3glitch_audio = audiocore.WaveFile(audio_file3)


# ---- Last sound variable (to store and compare files) ---#
last_play_time = 0
last_played = None
cooldown = 2  # This will let some audios play over and over again seemingly.

# ------
#  GLOBAL VOLUME ---- #
global_volume = 0.5


# ---
# TIME RELATED VARIABLES #
# ----

trigger_time = 10  # Seconds required.
start_time = 0  # The timer will start with 0 seconds.
start_timer = False  # This will help start the countdown of the seconds.
glitching_state = False  # For the glitching effect.


# -----
# You shall not pass!!!
# -----

you_shall_not_pass = False


# ----
# Am I the board with the photoresistor?
# ----

this_photoresistor = False

# Mandate other boards to light up.
we_can_light = False

# Globally deactivate photoresistor mode.
photoresistor_mode = False

while True:
    try:
        # --- Get values ----- #
        voltage = get_voltage(photoresistor)
        distance = ultrasonic.distance  # In cm
        print("Photoresistor voltage:", round(voltage, 3))
        print(f"Distance: {distance:.2f} cm")

        sound = noglitch_audio  # Load the no glitch audio to play later.

        # Check if this is the board with the photoresistor.

        if photoresistor_mode == True:
            if this_photoresistor == True:
                if voltage <= 0.15:
                    signal_pin_1.value = True
                    signal_pin_2.value = True
                    we_can_light = True
                    this_photoresistor = False

            # Once the voltage is received after the photoresistor confirms there is light, turn everyone up.
            if (
                receiving_pin_1.value == True or receiving_pin_2.value == True
            ) and this_photoresistor == False:
                we_can_light = True
        else:
            we_can_light = True

        # -------------- Light show! --------------------

        # Although lets first check if I am receiving some energy output in order to synchronize...

        if we_can_light == True:
            if (
                receiving_pin_1.value == True or receiving_pin_2.value == True
            ) and you_shall_not_pass == False:
                glitching_state = True
            else:
                glitching_state = False

            if (distance > 0 and distance < 68) and glitching_state == False:
                # After the glitching state condition has been evaluated, and this is not the one that is on a glitching state,
                # start the timer to create the effect.
                if not start_timer:
                    start_time = time.monotonic()
                    start_timer = True

                # Since this is not the one in a glitching state, it will keep track of the seconds until it reaches 10 seconds, where it will
                # "Synchronize" the rest of the boards.

                elapsed = time.monotonic() - start_time
                print("Seconds in range:", round(elapsed, 2))

                if elapsed >= 16:
                    # Load the glitching level 3 audio.
                    sound = level3glitch_audio

                    # I will synchronize EVERYONE!
                    signal_pin_1.value = True
                    signal_pin_2.value = True
                    you_shall_not_pass = True  # Do not override main circuit.

                elif elapsed >= 10 and elapsed <= 16:
                    # Load the glitching level 2 audio.
                    sound = level2glitch_audio

                    # I will synchronize EVERYONE!
                    signal_pin_1.value = True
                    signal_pin_2.value = True
                    you_shall_not_pass = True

                elif elapsed >= 1 and elapsed <= 10:
                    # Load the glitching level 1 audio.
                    sound = level1glitch_audio

                    signal_pin_1.value = False
                    signal_pin_2.value = False
                    you_shall_not_pass = False

                # Make sound
                # global_volume = 1.0
                cooldown = (
                    10.0  # Cooldown has to be 0 preferably to avoid a silence gap.
                )

                if sound:
                    now = time.monotonic()
                    # Play sound if there is a new audio file and the cooldown has finished.
                if sound != last_played or now - last_play_time > cooldown:
                    mixer.voice[0].play(sound, loop=False)
                    mixer.voice[0].level = global_volume
                    last_played = sound
                    last_play_time = now

                # White, to show the other ones as affected.
                if elapsed >= 3 and elapsed <= 9:
                    for i in range(0, 40):
                        pixels.fill((255 - int(i), 100 - int(i), 0))  # Dimming effect.

                elif elapsed >= 10 and elapsed <= 16:
                    # ---- #
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    # ---- #

                elif elapsed >= 17:
                    # ---- #
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    # ---- #

            elif distance >= 69 and glitching_state == False:
                pixels.fill((255, 100, 0))
                # The person has moved away
                start_timer = False
                you_shall_not_pass = False
                signal_pin_1.value = False
                signal_pin_2.value = False

                # Make sound
                # global_volume = 1.0
                cooldown = (
                    20.0  # Cooldown has to be 0 preferably to avoid a silence gap.
                )

                if sound:
                    now = time.monotonic()
                    # Play sound if there is a new audio file and the cooldown has finished.
                if sound != last_played or now - last_play_time > cooldown:
                    mixer.voice[0].play(sound, loop=True)
                    mixer.voice[0].level = global_volume
                    last_played = sound
                    last_play_time = now

            elif distance >= 0 and glitching_state == True:
                if not start_timer:
                    start_time = time.monotonic()
                    start_timer = True

                elapsed = time.monotonic() - start_time

                if elapsed >= 1 and elapsed <= 10:
                    sound = level1glitch_audio
                    for i in range(0, 40):
                        pixels.fill((255 - int(i), 100 - int(i), 0))  # Dimming effect.

                elif elapsed >= 11 and elapsed <= 16:
                    # The audio.
                    sound = level2glitch_audio

                    # ---- #
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((30, 255, 255))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    pixels.fill((255, 30, 30))
                    # ---- #

                elif elapsed >= 17:
                    # The audio.
                    sound = level3glitch_audio

                    # ---- #
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((45, 255, 255))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    pixels.fill((255, 45, 45))
                    # ---- #

                # Make sound
                # global_volume = 1.0
                cooldown = (
                    10.0  # Cooldown has to be 0 preferably to avoid a silence gap.
                )

                if sound:
                    now = time.monotonic()
                    # Play sound if there is a new audio file and the cooldown has finished.
                if sound != last_played or now - last_play_time > cooldown:
                    mixer.voice[0].play(sound, loop=False)
                    mixer.voice[0].level = global_volume
                    last_played = sound
                    last_play_time = now

            # -----------------------------------------------

    except RuntimeError:
        # Sometimes a reading may fail due to timeout.
        print("Retrying...")
    time.sleep(0.2)
