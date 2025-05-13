import numpy as np
import pyaudio
import queue
import threading
from constants import *

class SoundProcessor:
    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=1)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=RATE,
                                 input=True,
                                 frames_per_buffer=CHUNK_SIZE)
        self.running = True
        self.sound_buffer = []
        self.buffer_size = 3
        
    def start(self):
        self.thread = threading.Thread(target=self._process_audio)
        self.thread.daemon = True
        self.thread.start()
        
    def _process_audio(self):
        while self.running:
            try:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                # Calculate RMS (Root Mean Square) of the audio data
                rms = np.sqrt(np.mean(np.square(audio_data)))
                
                # Apply amplification with faster response
                amplified_rms = rms * SOUND_AMPLIFICATION
                
                # Add to buffer
                self.sound_buffer.append(amplified_rms)
                if len(self.sound_buffer) > self.buffer_size:
                    self.sound_buffer.pop(0)
                
                # Calculate average of recent samples with more weight on recent values
                avg_intensity = np.mean(self.sound_buffer)
                
                # Apply minimal smoothing for faster response
                smoothed_intensity = avg_intensity * 0.3 + amplified_rms * 0.7
                
                # Clear old values from queue
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # Put new value
                self.audio_queue.put(smoothed_intensity)
                
            except Exception as e:
                print(f"Error processing audio: {e}")
                self.audio_queue.put(0.0)
                
    def get_intensity(self):
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return 0.0
            
    def stop(self):
        self.running = False
        self.thread.join(timeout=1.0)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate() 