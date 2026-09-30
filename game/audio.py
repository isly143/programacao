"""
Purble Bakery - Audio Manager & Synthesizer
Generates retro synthesized sound effects and cheerful BGM without any external audio downloads.
"""
import os
import math
import struct
import wave
import pygame

class AudioManager:
    def __init__(self, assets_dir="F:/isly/assets/sounds"):
        self.assets_dir = assets_dir
        self.sounds = {}
        self.music_playing = False
        self.muted = False
        self.volume = 0.7
        self.sample_rate = 44100
        
        # Ensure directory exists
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"Warning: Could not initialize mixer: {e}")
                
        # Generate sound files if missing
        self._generate_all_audio()
        self._load_sounds()

    def _write_wav(self, filename, samples):
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            return path
            
        with wave.open(path, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.sample_rate)
            data = bytearray()
            for s in samples:
                val = int(max(-32768, min(32767, s * 32767)))
                data.extend(struct.pack('<h', val))
            f.writeframes(data)
        return path

    def _generate_all_audio(self):
        sr = self.sample_rate
        
        # 1. Click
        if not os.path.exists(os.path.join(self.assets_dir, "click.wav")):
            duration = 0.05
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                env = math.exp(-60 * t)
                val = 0.4 * env * math.sin(2 * math.pi * 1200 * t)
                samples.append(val)
            self._write_wav("click.wav", samples)

        # 2. Conveyor belt sound
        if not os.path.exists(os.path.join(self.assets_dir, "conveyor.wav")):
            duration = 0.35
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                env = math.sin(math.pi * t / duration)
                val = 0.25 * env * (math.sin(2 * math.pi * 160 * t) + 0.5 * math.sin(2 * math.pi * 320 * t + math.sin(40 * t)))
                samples.append(val)
            self._write_wav("conveyor.wav", samples)

        # 3. Dispense Pan (metallic drop)
        if not os.path.exists(os.path.join(self.assets_dir, "dispense_pan.wav")):
            duration = 0.2
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                env = math.exp(-25 * t)
                val = 0.4 * env * (math.sin(2 * math.pi * 450 * t) + 0.6 * math.sin(2 * math.pi * 920 * t))
                samples.append(val)
            self._write_wav("dispense_pan.wav", samples)

        # 4. Dispense Batter (squishy pour)
        if not os.path.exists(os.path.join(self.assets_dir, "dispense_batter.wav")):
            duration = 0.3
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                freq = 280 + 120 * math.sin(25 * t)
                env = math.sin(math.pi * t / duration)
                noise = ((i * 1103515245 + 12345) % 65536 / 32768.0 - 1.0) * 0.15
                val = env * (0.35 * math.sin(2 * math.pi * freq * t) + noise)
                samples.append(val)
            self._write_wav("dispense_batter.wav", samples)

        # 5. Dispense Filling (creamy bloop)
        if not os.path.exists(os.path.join(self.assets_dir, "dispense_filling.wav")):
            duration = 0.25
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                freq = 350 + 200 * math.sin(math.pi * t / duration)
                env = math.exp(-12 * t)
                val = 0.45 * env * math.sin(2 * math.pi * freq * t)
                samples.append(val)
            self._write_wav("dispense_filling.wav", samples)

        # 6. Dispense Frosting (smooth swoosh glaze)
        if not os.path.exists(os.path.join(self.assets_dir, "dispense_frosting.wav")):
            duration = 0.3
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                freq = 500 - 150 * (t / duration)
                env = math.sin(math.pi * t / duration)
                val = 0.4 * env * (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * (freq * 1.5) * t))
                samples.append(val)
            self._write_wav("dispense_frosting.wav", samples)

        # 7. Dispense Topping (cheerful pop/plop)
        if not os.path.exists(os.path.join(self.assets_dir, "dispense_topping.wav")):
            duration = 0.18
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                freq = 600 + 400 * math.exp(-20 * t)
                env = math.exp(-18 * t)
                val = 0.45 * env * math.sin(2 * math.pi * freq * t)
                samples.append(val)
            self._write_wav("dispense_topping.wav", samples)

        # 8. Correct Cake Ding
        if not os.path.exists(os.path.join(self.assets_dir, "correct.wav")):
            duration = 0.45
            n = int(sr * duration)
            samples = []
            notes = [523.25, 659.25, 783.99, 1046.50] # C5, E5, G5, C6
            for i in range(n):
                t = i / sr
                note_idx = min(len(notes)-1, int(t / 0.08))
                freq = notes[note_idx]
                note_t = t - (note_idx * 0.08)
                env = math.exp(-10 * note_t) if note_idx < len(notes)-1 else math.exp(-6 * note_t)
                val = 0.4 * env * (math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(4 * math.pi * freq * t))
                samples.append(val)
            self._write_wav("correct.wav", samples)

        # 9. Wrong Cake Buzz
        if not os.path.exists(os.path.join(self.assets_dir, "wrong.wav")):
            duration = 0.35
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                env = math.exp(-6 * t)
                val = 0.45 * env * (math.sin(2 * math.pi * 140 * t) + 0.7 * math.sin(2 * math.pi * 148 * t))
                samples.append(val)
            self._write_wav("wrong.wav", samples)

        # 10. Trash Sound (whistle down)
        if not os.path.exists(os.path.join(self.assets_dir, "trash.wav")):
            duration = 0.4
            n = int(sr * duration)
            samples = []
            for i in range(n):
                t = i / sr
                freq = 800 * (1 - 0.75 * (t / duration))
                env = 1 - (t / duration)
                val = 0.4 * env * math.sin(2 * math.pi * freq * t)
                samples.append(val)
            self._write_wav("trash.wav", samples)

        # 11. Level Complete Fanfare
        if not os.path.exists(os.path.join(self.assets_dir, "level_win.wav")):
            duration = 1.2
            n = int(sr * duration)
            samples = []
            melody = [(0.0, 0.15, 523.25), (0.15, 0.15, 659.25), (0.30, 0.15, 783.99), 
                      (0.45, 0.15, 1046.50), (0.60, 0.60, 1318.51)]
            for i in range(n):
                t = i / sr
                val = 0
                for start, dur, freq in melody:
                    if start <= t < start + dur:
                        nt = t - start
                        env = math.exp(-4 * nt / dur) * math.sin(math.pi * nt / dur)
                        val += 0.35 * env * (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t))
                samples.append(val)
            self._write_wav("level_win.wav", samples)

        # 12. Cheerful Bakery BGM Loop (synthesized jaunty tune)
        if not os.path.exists(os.path.join(self.assets_dir, "bgm.wav")):
            # 8-bar loop at 128 BPM (~7.5 seconds loop)
            bpm = 125
            beat_dur = 60.0 / bpm
            total_dur = beat_dur * 16 # 16 beats = 4 bars
            n = int(sr * total_dur)
            samples = [0.0] * n
            
            # Simple happy melody sequence: (beat_start, beat_length, freq)
            notes_seq = [
                # Bar 1
                (0, 0.5, 523.25), (0.5, 0.5, 659.25), (1.0, 1.0, 783.99),
                (2.0, 0.5, 880.00), (2.5, 0.5, 783.99), (3.0, 1.0, 659.25),
                # Bar 2
                (4, 0.5, 587.33), (4.5, 0.5, 659.25), (5.0, 1.0, 698.46),
                (6.0, 1.0, 783.99), (7.0, 1.0, 587.33),
                # Bar 3
                (8, 0.5, 523.25), (8.5, 0.5, 659.25), (9.0, 1.0, 783.99),
                (10.0, 0.5, 1046.50), (10.5, 0.5, 880.00), (11.0, 1.0, 783.99),
                # Bar 4
                (12.0, 0.5, 698.46), (12.5, 0.5, 783.99), (13.0, 0.5, 659.25), (13.5, 0.5, 587.33),
                (14.0, 2.0, 523.25)
            ]
            
            # Bass accompaniment:
            bass_seq = [
                (0, 1.5, 130.81), (2, 1.5, 164.81),
                (4, 1.5, 146.83), (6, 1.5, 196.00),
                (8, 1.5, 130.81), (10, 1.5, 164.81),
                (12, 1.5, 174.61), (14, 1.5, 196.00)
            ]
            
            for b_start, b_len, freq in notes_seq:
                start_t = b_start * beat_dur
                dur_t = b_len * beat_dur
                start_idx = int(start_t * sr)
                end_idx = min(n, int((start_t + dur_t) * sr))
                for idx in range(start_idx, end_idx):
                    t = (idx - start_idx) / sr
                    env = math.exp(-3 * t / dur_t) * (1 - math.exp(-20 * t))
                    val = 0.22 * env * (math.sin(2 * math.pi * freq * (idx / sr)) + 0.2 * math.sin(4 * math.pi * freq * (idx / sr)))
                    samples[idx] += val
                    
            for b_start, b_len, freq in bass_seq:
                start_t = b_start * beat_dur
                dur_t = b_len * beat_dur
                start_idx = int(start_t * sr)
                end_idx = min(n, int((start_t + dur_t) * sr))
                for idx in range(start_idx, end_idx):
                    t = (idx - start_idx) / sr
                    env = math.exp(-2.5 * t / dur_t)
                    val = 0.18 * env * math.sin(2 * math.pi * freq * (idx / sr))
                    samples[idx] += val

            # Normalize to avoid clipping
            max_val = max(abs(s) for s in samples) or 1.0
            if max_val > 0.8:
                samples = [s * (0.8 / max_val) for s in samples]

            self._write_wav("bgm.wav", samples)

    def _load_sounds(self):
        sound_names = [
            "click", "conveyor", "dispense_pan", "dispense_batter",
            "dispense_filling", "dispense_frosting", "dispense_topping",
            "correct", "wrong", "trash", "level_win"
        ]
        for name in sound_names:
            path = os.path.join(self.assets_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.volume)
                except Exception as e:
                    print(f"Failed to load sound {name}: {e}")

    def play(self, sound_name):
        if self.muted:
            return
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass

    def start_bgm(self):
        bgm_path = os.path.join(self.assets_dir, "bgm.wav")
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(self.volume * 0.5)
                pygame.mixer.music.play(-1) # Loop indefinitely
                self.music_playing = True
            except Exception as e:
                print(f"Error starting music: {e}")

    def stop_bgm(self):
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except Exception:
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume * 0.5)
        return self.muted
