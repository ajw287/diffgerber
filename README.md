# diffgerber
Graphical tool to help users compare gerber files, the output from PCB CAD software

# Setup
This project depends on python3, pillow, tkinter & pygerber.  The following commands are recommended:

1. Setup a python venv
   ```bash
   python -m venv diffgerber
   source ./diffgerber/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install tk pillow pygerber
   ```
4. Run the program:
   ```bash
   python diffgerber.py
   ```

# Using diffgerber
This is a basic tool to highlight differences in gerber files so that they can be compared.

![Picture of the Gerber Difftool](docs/pics/GerberDifferenceViewer.png?raw=true "diffgerber")
