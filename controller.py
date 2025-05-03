from splashscreen import startscreen
from gui import run_gui


while True:
    selected_mode,log_to_file=startscreen()
    run_gui(selected_mode,log_to_file)
    
    