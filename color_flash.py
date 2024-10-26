import tkinter as tk
from tkinter import Toplevel, Label
import time
from utils import logger

root = None

def initialize_root():
    global root
    if root is None or not tk._default_root:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-alpha', 0)  # Make root fully transparent

def color_flash(color, duration, location=(0, 0), size=(100, 100), opacity=0.5, text=""):
    logger.debug(f"color_flash called with: {color}, {duration}, {location}, {size}, {opacity}, {text}")
    initialize_root()
    
    flash_window = Toplevel(root)
    flash_window.overrideredirect(True)
    flash_window.geometry(f"{size[0]}x{size[1]}+{location[0]}+{location[1]}")
    flash_window.configure(bg=color)
    flash_window.attributes('-alpha', opacity)
    flash_window.attributes('-topmost', True)
    
    if text:
        canvas = tk.Canvas(flash_window, bg=color, highlightthickness=0)
        canvas.pack(expand=True, fill=tk.BOTH)
        
        # Create outlined text
        outline_color = "black"
        text_color = "white"
        font = ("Arial", 18, "bold")
        
        for x_offset in [-1, 1]:
            for y_offset in [-1, 1]:
                canvas.create_text(size[0]//2 + x_offset, size[1]//2 + y_offset, 
                                   text=text, fill=outline_color, font=font,
                                   width=size[0]-10)  # Wrap text if necessary
        
        canvas.create_text(size[0]//2, size[1]//2, text=text, fill=text_color, font=font,
                           width=size[0]-10)  # Wrap text if necessary
    
    def fade_out():
        for i in range(10, -1, -1):
            flash_window.attributes('-alpha', i * opacity / 10)
            flash_window.update()
            time.sleep(0.05)
        flash_window.destroy()
    
    flash_window.after(int(duration * 1000), fade_out)
    
    return flash_window

def process_color_flashes():
    if root:
        root.update()

if __name__ == "__main__":
    initialize_root()
    flash_window = color_flash(
        color="red",
        size=(300, 200),
        location=(100, 100),
        duration=2,
        opacity=0.7,
        text="Test Flash"
    )
    root.mainloop()
