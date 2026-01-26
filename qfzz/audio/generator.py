"""
Audio generation tools for QFZZ.
"""

import logging
import math
import struct
import wave

logger = logging.getLogger(__name__)


def generate_tone(filename: str, duration_sec: int = 3, freq_hz: int = 440):
    """
    Generate a simple sine wave tone WAV file.

    Args:
        filename: Output filename
        duration_sec: Duration in seconds
        freq_hz: Frequency in Hertz
    """
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration_sec)

        with wave.open(filename, "w") as wav_file:
            # 1 channel (mono), 2 bytes per sample (16-bit), 44100Hz
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            # Generate samples
            for i in range(n_samples):
                # t = time in seconds
                t = i / sample_rate
                # sine wave
                value = int(32767.0 * math.sin(2.0 * math.pi * freq_hz * t))
                # pack as 16-bit short (little endian)
                data = struct.pack("<h", value)
                wav_file.writeframes(data)

        logger.info(f"Generated test audio: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return False
