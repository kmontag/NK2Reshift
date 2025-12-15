## NK2Reshift

This is an Ableton Live control surface script for the [Korg
nanoKONTROL2](https://www.korg.com/us/products/computergear/nanokontrol2/).

It's a replica of dynamiiic's excellent
[NanoKontrol2Shift](https://forum.ableton.com/viewtopic.php?t=193316).
It uses more recent Live APIs to provide some usability benefits, for
example:

- more consistent LED behavior, for example when changing modes
  or working with the clip matrix.
- blinking LEDs to represent playing/triggered clips.
- device identification, so the session ring ("red box") is only
  visible when the nanoKONTROL2 is actually connected.

### Status

This script supports Live 12.3 and up. Many features will probably
work in earlier versions of Live, but YMMV.

This is an unofficial script. If you run into any issues, please [file
them](../../issues) in this repository, not with Ableton.

Note that NK2Reshift uses recent APIs which are subject to change in
future Live versions. Things should be pretty stable in practice, but
please file an issue here if you see any breakage after updating Live.
I'll do my best to keep the script up-to-date with upstream changes.

### Usage

Usage is the same as NanoKontrol2Shfit:

> It loads in a default or initial mode and there are 3 modes buttons:
>
> - STOP: Shift Mode
> - PLAY: Alt Mode
> - RECORD: Ctrl Mode
>   Press one of them to enter that mode, pressing again will deactivate it and return to the initial mode. If you have one mode active and press other mode button, simply it deactivates the first and activates the second.
>
> OVERVIEW ON MODES:
>
> DEFAULT MODE:
>
> - Track Nav - Session left/right
> - Rewind, Forward - Session up/down
> - Marker Left, Right - Send up/down
> - Cycle, Set Marker - Does nothing
> - Faders - Session tracks volume
> - Knobs - Session tracks send A (Assignable with marker left/right to the other sends)
> - Solo, Arm, Mute - Session Clip Launch Matrix 8x3
>
> SHIFT MODE:
>
> - Track Nav - Same as in default mode
> - Rewind, Forward - Same as in default mode
> - Marker Left, Right - Same as in default mode
> - Cycle, Set Marker - Does nothing
> - Faders - Same as in default mode
> - Knobs - Same as in default mode
> - Solo, Arm, Mute - Solo, Arm and Mute for the Session controlled tracks
>
> ALT MODE:
>
> - Track Nav - Same as in default mode
> - Rewind, Forward - Same as in default mode
> - Marker Left, Right - Same as in default mode
> - Cycle, Set Marker - Does nothing
> - Faders - Same as in default mode
> - Knobs - Same as in default mode
> - Solo - Resets the value of the current send for the Session controlled tracks
> - Mute - Select track for the Session controlled tracks
> - Arm - Stop button for the Session controlled tracks
>
> CTRL MODE:
>
> - Track Nav - Same as in default mode
> - Rewind, Forward - Same as in default mode
> - Marker Left, Right - Device left/right
> - Cycle - Device turn on/off
> - Set Marker - Device lock/unlock
> - Faders - Same as in default mode
> - Knobs - Controls 8 knobs on a selected device
> - Solo - Clip/Device view for the Session controlled tracks
> - Mute - The 3 first Mute buttons are assigned to the 3 scene launch, the rest unassigned (Ideas are welcome)
> - Arm 1 - Stop
> - Arm 2 - Play
> - Arm 3 - Record
> - Arm 4 - Global Quantization
> - Arm 5 - Tempo Down
> - Arm 6 - Tempo Up
> - Arm 7 - Metronome
> - Arm 8 - Stop All Clips

### Installation

- Download or clone this repository and place it under
  `Remote Scripts` in your Live User Library. If you download it
  directly, change the folder name from `NK2Reshift-main` to
  `NK2Reshift` (or anything without a hyphen).
- Start or restart Live.
- In the Live settings dialog under `Link/Tempo/MIDI`, choose
  `NK2Reshift` as one of your control surfaces.
- Make sure your nanoKONTROL2 device is plugged in, and select the
  nanoKONTROL2 ports for the control surface input/output.

### Configuration

To configure the nanoKONTROL2 for use with this script, hold the `SET`
and `STOP` buttons while plugging it in. This is the setup for Live
integration recommended in the nanoKONTROL2 manual (so it also works
with the built-in MackieControl control surface script).

Note that this default configuration is **not** the same as the one
expected by the original NanoKontrol2Shift. If you want to use the
[NanoKontrol2Shift
configuration](https://sonicbloom.net/free-midi-remote-script-apc-emulation-for-korg-nanokontrol-2/)
instead, create a file called `user.py` in this
directory, containing:

```python
# user.py
from .configuration import NanoKontrol2ShiftConfiguration

configuration = NanoKontrol2ShiftConfiguration()
```

Alternatively, you can provide a custom mapping by exporting any
`configuration` from `user.py`, for example:

```python
# user.py
from .configuration import cc_button, Configuration

configuration = Configuration(
    track_left_button=cc_button(50),
    track_right_button=cc_button(51),
    # ...
)
```

See [configuration.py](configuration.py) for more details and the full list of settings.

### Development

[Poetry](https://python-poetry.org/) must be installed to use the dev
tools.

Install development dependencies with `make deps`. This sets up Poetry
and (if Ableton Live 12 is detected) decompiles Ableton's Python
libraries for type checking.

Run `make check` for type checking, `make lint` to check formatting,
and `make fix` to auto-format code.
