from music21 import *
import subprocess
import os
import platform
import tempfile

def display_midi_score(midi_path, musescore_path=None, show=True, save_path=None):
    """
    Robust MIDI to score display with multiple fallback methods
    
    Args:
        midi_path: Path to input MIDI file
        musescore_path: Explicit path to MuseScore executable
        show: Whether to display the score
        save_path: Optional path to save the score image
    """
    # 1. First try MuseScore conversion (best quality)
    if try_musescore_conversion(midi_path, musescore_path, save_path):
        if show and save_path:
            open_score_image(save_path)
        return True
    
    # 2. Try music21's built-in show (requires GUI)
    if try_music21_show(midi_path):
        return True
    
    # 3. Final fallback - convert to text representation
    print("Falling back to text representation:")
    show_text_representation(midi_path)
    return False

def try_musescore_conversion(midi_path, musescore_path=None, save_path=None):
    """Attempt conversion using MuseScore"""
    try:
        # Determine MuseScore path
        if not musescore_path:
            if platform.system() == 'Windows':
                musescore_path = 'C:/Program Files/MuseScore 4/bin/MuseScore4.exe'
            elif platform.system() == 'Darwin':
                musescore_path = '/Applications/MuseScore 4.app/Contents/MacOS/mscore'
            else:
                musescore_path = 'mscore'
        
        # Create temporary output path if none provided
        if not save_path:
            save_path = os.path.splitext(midi_path)[0] + '.png'
        
        # Run MuseScore conversion
        cmd = [musescore_path, midi_path, '-o', save_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully created score image at {save_path}")
            return True
        else:
            print(f"MuseScore conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"MuseScore conversion attempt failed: {str(e)}")
        return False

def try_music21_show(midi_path):
    """Attempt using music21's built-in show"""
    try:
        score = converter.parse(midi_path)
        score.show()
        return True
    except Exception as e:
        print(f"music21 show failed: {str(e)}")
        return False

def show_text_representation(midi_path):
    """Fallback text representation"""
    try:
        score = converter.parse(midi_path)
        print(score.show('text'))
    except Exception as e:
        print(f"Couldn't create text representation: {str(e)}")

def open_score_image(image_path):
    """Open image with default viewer"""
    try:
        if platform.system() == 'Windows':
            os.startfile(image_path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', image_path])
        else:
            subprocess.run(['xdg-open', image_path])
    except Exception as e:
        print(f"Couldn't open image: {str(e)}")

# Example usage with explicit MuseScore path

# Replace with your actual paths
midi_file = "output.mid"
custom_musescore_path = "C:/Program Files/MuseScore 4/bin/MuseScore4.exe"  # Set this if automatic detection fails

display_midi_score(
midi_path=midi_file,
musescore_path=custom_musescore_path,
save_path = "score.png"
)