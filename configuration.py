# This file defines the configuration schema and defaults for the
# application.
#
# To customize these settings, create a file called
# `configuration_local.py` in this directory, and export a custom
# `Configuration` instance named `configuration`, for example:
#
#   # configuration_local.py
#   from .configuration import cc_button, Configuration
#
#   configuration = Configuration(
#       track_left_button=cc_button(50),
#       track_right_button=cc_button(51),
#       # ...
#   )
import typing

import Live
from ableton.v3.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE, MIDI_PB_TYPE

DEFAULT_CHANNEL = 0
MAP_MODES = Live.MidiMap.MapMode


class ButtonConfiguration(typing.NamedTuple):
    identifier: int
    msg_type: int
    channel: int


class EncoderConfiguration(typing.NamedTuple):
    identifier: int
    msg_type: int
    channel: int
    map_mode: int


def cc_button(identifier, channel=DEFAULT_CHANNEL):
    return ButtonConfiguration(
        identifier=identifier, msg_type=MIDI_CC_TYPE, channel=channel
    )


def cc_encoder(identifier, channel=DEFAULT_CHANNEL, map_mode=MAP_MODES.absolute):
    return EncoderConfiguration(
        identifier=identifier, msg_type=MIDI_CC_TYPE, channel=channel, map_mode=map_mode
    )


def note_button(identifier, channel=DEFAULT_CHANNEL):
    return ButtonConfiguration(
        identifier=identifier, msg_type=MIDI_NOTE_TYPE, channel=channel
    )


def pb_encoder(channel=DEFAULT_CHANNEL):
    return EncoderConfiguration(
        identifier=0,
        msg_type=MIDI_PB_TYPE,
        channel=channel,
        map_mode=MAP_MODES.absolute,
    )


class Configuration(typing.NamedTuple):
    """
    Application configuration, including mappings for all controls on the nanoKONTROL2.

    The default layout can be loaded onto the device by holding the SET and STOP buttons
    while plugging it in. This layout also works with the built-in MackieControl control
    surface.

    All buttons are expected to have momentary behavior.
    """

    #### Physical controls.

    # Transport and navigation buttons.
    track_left_button: ButtonConfiguration = note_button(46)
    track_right_button: ButtonConfiguration = note_button(47)

    cycle_button: ButtonConfiguration = note_button(86)

    marker_set_button: ButtonConfiguration = note_button(82)
    marker_left_button: ButtonConfiguration = note_button(84)
    marker_right_button: ButtonConfiguration = note_button(85)

    rewind_button: ButtonConfiguration = note_button(91)
    fast_forward_button: ButtonConfiguration = note_button(92)
    stop_button: ButtonConfiguration = note_button(93)
    play_button: ButtonConfiguration = note_button(94)
    record_button: ButtonConfiguration = note_button(95)

    # Channel strip buttons.
    solo_buttons: typing.List[ButtonConfiguration] = [
        note_button(8 + i) for i in range(8)
    ]
    mute_buttons: typing.List[ButtonConfiguration] = [
        note_button(16 + i) for i in range(8)
    ]
    arm_buttons: typing.List[ButtonConfiguration] = [note_button(i) for i in range(8)]

    # Encoders.
    sliders: typing.List[EncoderConfiguration] = [pb_encoder(i) for i in range(8)]
    knobs: typing.List[EncoderConfiguration] = [
        cc_encoder(16 + i, map_mode=MAP_MODES.relative_signed_bit) for i in range(8)
    ]

    #### Control surface behavior.

    # The mode active at startup. Options are: default, shift, alt,
    # ctrl.
    initial_mode: str = "default"


# To use the original NanoKontrol2Shift configuration, do something
# like the following in `configuration_local.py`:
#
#   # configuration_local.py
#   from .configuration import NanoKontrol2ShiftConfiguration
#
#   configuration = NanoKontrol2ShiftConfiguration()
#
class NanoKontrol2ShiftConfiguration(Configuration):
    """
    Control mappings from the original NanoKontrol2Shift layout.
    """

    track_left_button = cc_button(40)
    track_right_button = cc_button(41)

    cycle_button = cc_button(42)
    marker_set_button = cc_button(43)
    marker_left_button = cc_button(44)
    marker_right_button = cc_button(45)

    rewind_button = cc_button(46)
    fast_forward_button = cc_button(47)
    stop_button = cc_button(48)
    play_button = cc_button(49)
    record_button = cc_button(50)

    solo_buttons = [cc_button(16 + i) for i in range(8)]
    mute_buttons = [cc_button(24 + i) for i in range(8)]
    arm_buttons = [cc_button(32 + i) for i in range(8)]

    sliders = [cc_encoder(i) for i in range(8)]
    knobs = [cc_encoder(8 + i) for i in range(8)]
