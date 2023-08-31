# diffgerber

<p align="center">
   <img src="./docs/images/diffgerber-logo.png" alt="diffgerber logo" width="300" title="the diffgerber logo">
</p>

Graphical tool to help users compare gerber files, the output from EDA tools (PCB CAD software) such as KiCAD using pygerber 2.0.0.

![Picture of the Gerber Difftool](docs/images/GerberDifferenceViewer.png?raw=true "a diffgerber screenshot")

# Setup

1. Install in editable format:

```bash
git clone https://github.com/ajw287/diffgerber.git
cd diffgerber
python3 -venv venv
source ./venv/bin/activate
pip install -r requirements.txt
pip install -e .
```
## Or: 

This project depends on python3, pillow, tkinter, difflib & pygerber.  The following commands are recommended:

1. Setup a python venv
   ```bash
   python -m venv diffgerber
   source ./diffgerber/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install tk pillow pygerber difflib
   ```
4. Run the program:
   ```bash
   python diffgerber.py
   ```

# Using diffgerber
This is a basic tool to highlight differences in gerber files so that they can be compared.  At this time two directories of gerber files can be opened, layers are matched based on filename and checked for similarity.  If they are identical no differences will be expected, if there is more than 25% similarity, then a graphical "diff" is attempted.

Aug-23:  Started on a V2.0 with only pygerber backend.  The original 3 backends (pygerber, pcb-tools, gerbv) each had problems/eccentricities and limitations, by limiting myself to one backend more progress will be seen.

1. Click "Browse" on the left-hand column, navigate to "./example/1/" click "OK".  You should see two layers of gerbers

2. Click "Browse" on the right-hand column, navigate to "./example/2/" click "OK".  You should see another two layers of gerbers

3. Because they have the same name, they are paired.  Select a 'top.grb' file, the label will tell you that they are identical.

4. Select a 'bottom.grb' file, the label will tell you the similarity value.  Can you see the difference?

5. Click the "Highlight Differences" button, the differences will be highlighted with an outliine.
