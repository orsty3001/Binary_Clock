Binary Watch for Linux 
A native GTK 3 desktop clock with the upright LED arrangement of Newson’s Electronics’ binary watch. Original application code; no downloaded watch
code or images are bundled. 
Run 
Open a terminal in this folder and run: 
./launch.sh

Requires Python 3, GTK 3, PyGObject and Cairo. These are already available on the computer where this app was created. On Ubuntu/Debian, if needed: 
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

On Fedora: 
sudo dnf install python3-gobject python3-cairo gtk3

The app is portable: keep the folder together. No network connection, account or Python package download is required during use. 
Reading the display 
Columns are hours, minutes, seconds, left to right, colored red, yellow, green. Weights are 32, 16, 8, 4, 2, 1, top to bottom. Add the illuminated values in
each column. For 18:42:13, hours light 16+2, minutes light 32+8+2, seconds light 8+4+1. Hours use 24-hour time. The hours 32 LED stays off; the
hardware watch uses that position for a blue low-battery warning, which this app does not simulate. 
Time comes from the system clock and follows system time changes and resume from sleep. Use the checkboxes to hide weights or digital time; adjust
LED brightness with the slider. “Keep above” depends on the window manager. F11 toggles fullscreen; Escape exits it. Preferences last for the current
session. The app does not change the system clock. 
Validation 
python3 -m unittest discover -s tests -v
./launch.sh --render preview.png --time 18:42:13

The renderer used by the actual window also generates the PNG preview
