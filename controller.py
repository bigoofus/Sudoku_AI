from splashscreen import startscreen
from gui import run_gui


while True:
        selected_mode,logging=startscreen()
        run_gui(selected_mode,logging)
    

    