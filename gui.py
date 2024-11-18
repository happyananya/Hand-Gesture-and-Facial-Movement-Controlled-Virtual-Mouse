import tkinter as tk
import subprocess
import signal
import pyautogui
import keyboard

root = tk.Tk()
root.title("Cursor Control")

heading_label = tk.Label(root, text="Multi Modal Cursor Control", font=("Arial", 24, "bold"))
heading_label.pack(pady=20)

process = None

def run_program(program_file):
    global process
    process = subprocess.Popen(['python', program_file])

def stop_program():
    global process
    if process:
        process.send_signal(signal.SIGTERM)
        process = None
def press_escape():
    # Simulate pressing the Escape key
    pyautogui.press('esc')
    
def exit():
    root.destroy()
    stop_program()

frame1 = tk.Frame(root, padx=10, pady=10)
frame1.pack(side=tk.LEFT)

button1 = tk.Button(frame1, text="Run eye cursor", command=lambda: run_program("/Users/ananyaagarwal/Documents/Project_1/eye.py"),bg="#03fca1")
button1.pack()

button1_stop = tk.Button(frame1, text="Stop eye cursor", command=stop_program,bg="#fc035e")
button1_stop.pack()


# Card 2
frame2 = tk.Frame(root, padx=10, pady=10)
frame2.pack(side=tk.LEFT)

button2 = tk.Button(frame2, text="Run hand gesture cursor", command=lambda: run_program("/Users/ananyaagarwal/Documents/Project_1/hand.py"),bg="#03fca1")
button2.pack()

button2_stop = tk.Button(frame2, text="Stop hand gesture cursor", command=stop_program,bg="#fc035e")
button2_stop.pack()


# Card 3
frame3 = tk.Frame(root, padx=10, pady=10)
frame3.pack(side=tk.RIGHT)

button3 = tk.Button(frame3, text="EXIT", command = exit , bg="#03fca1")

button3.pack()


root.mainloop()