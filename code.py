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
        # --- Get values ----- #
        distance = ultrasonic.distance  # In cm
        print(f"Distance: {distance:.2f} cm")

        sound = beep # Play beep sound.if


        # This is just for testing, but I am going to check if the three devices work correctly and do not present any interference.
        
              
        if distance > 40:
            global_volume = 1.0
            cooldown = 1.0
            
        elif distance > 30:
            global_volume = 1.00
            cooldown = 0.8

        elif distance > 20:
            global_volume = 1.00
            cooldown = 0.5

        elif distance > 10:
            global_volume = 1.00
            cooldown = 0.3
        
        elif distance > 0:
            global_volume = 1.00
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
