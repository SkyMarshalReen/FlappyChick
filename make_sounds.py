import math
import wave
from pathlib import Path

SAMPLE_RATE = 44100
SOUND_DIR = Path("sounds")
SOUND_DIR.mkdir(exist_ok=True)


def make_tone(filename, frequency, duration, volume=0.4):
    frames = []

    sample_count = int(SAMPLE_RATE * duration)

    for i in range(sample_count):
        t = i / SAMPLE_RATE
        sample = math.sin(2 * math.pi * frequency * t)

        # Fade out slightly toward the end
        fade = 1 - (i / sample_count)
        sample *= fade

        value = int(sample * volume * 32767)
        frames.append(value)

    path = SOUND_DIR / filename

    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        for value in frames:
            wav.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))


make_tone("jump.wav", 700, 0.12)
make_tone("score.wav", 1100, 0.18)
make_tone("hit.wav", 420, 0.35, 0.7)

print("Sounds created in ./sounds")
