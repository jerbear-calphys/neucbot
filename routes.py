from flask import current_app as app
from . import neucbot

@app.route('/')
def main_function():
    neucbot.run_alpha_energy_loss()  # Call the main function from neucbot
    return f"The result is: {result}"