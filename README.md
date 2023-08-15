# diffgerber
Graphical tool to help users compare gerber files, the output from PCB CAD software

I have put in 3 backends, but I'm plannig to switch to just using pygerber 2.0.0.


# Setup

1. Install in editable format:

```bash
git clone https://github.com/ajw287/diffgerber.git
cd diffgerber
python3 -venv venv
source ./venv/bin/activate
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

N.B. at this time (Jul-23) pygerber library only seems to work with a subset of gerber files.

![Picture of the Gerber Difftool](docs/pics/GerberDifferenceViewer.png?raw=true "diffgerber")

1. Click "Browse" on the left-hand column, navigate to "./example/1/" click "OK".  You should see two layers of gerbers

2. Click "Browse" on the right-hand column, navigate to "./example/2/" click "OK".  You should see another two layers of gerbers

3. Because they have the same name, they are paired.  Select a 'top.grb' file, the label will tell you that they are identical.

4. Select a 'bottom.grb' file, the label will tell you the similarity value.  Can you see the difference?

5. Click the "Highlight Differences" button, the differences will be highlighted with an outliine.
