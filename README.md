# Sound-Controlled Jumping Hen Game

A fun game where you control a hen's jumping height using sound input! The louder the sound, the higher the hen jumps.

## Requirements

- Python 3.7 or higher
- Pygame
- NumPy
- Librosa
- PyAudio

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. For Windows users, you might need to install PyAudio using a wheel file. Visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and download the appropriate wheel file for your Python version.

## How to Play

1. Run the game:
```bash
python jumping_hen.py
```

2. Make sounds (clap, speak, or any sound) to make the hen jump
3. The louder the sound, the higher the hen will jump
4. The current sound intensity is displayed in the top-left corner
5. Close the window to exit the game

## Controls

- No keyboard controls needed! Just make sounds to control the hen
- The hen will automatically jump when it detects sound above the threshold
- The jumping height is proportional to the sound intensity

## Troubleshooting

If you encounter any issues with PyAudio installation:
1. Make sure you have the latest pip version: `pip install --upgrade pip`
2. For Windows users, install the appropriate PyAudio wheel file
3. For Linux users, you might need to install portaudio: `sudo apt-get install python3-pyaudio` 