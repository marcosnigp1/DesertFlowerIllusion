# Desert Flower Illusion
# This file was originally the project example given by AdaFruit, for the Propmaker 2040.

import time
import board
import audiocore
import audiobusio
import audiomixer
from digitalio import DigitalInOut, Direction
import adafruit_hcsr04  # We need this to get the ultrasonic sensor working.


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
audio_file = open("audio/meowing-cat-401728.wav", "rb")
audio_file_1 = audiocore.WaveFile(audio_file1)
# ------
#  GLOBAL VOLUME ---- #
global_volume = 0.7


while True:
    # Print ultrasonic sensor values.
    # Get distance.
    try:
        # --- Get values ----- #
        distance = ultrasonic.distance  # In cm
        print(f"Distance: {distance:.2f} cm")

    except RuntimeError:
        # Sometimes a reading may fail due to timeout.
        print("Retrying...")
    time.sleep(0.2)
