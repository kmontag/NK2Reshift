from ableton.v3.control_surface import ControlSurface
from ableton.v3.control_surface.mode import CallFunctionMode

from .elements import NUM_TRACKS
from .modes import ModesComponent

SHIFT_BUTTON = "stop_button"
ALT_BUTTON = "play_button"
CTRL_BUTTON = "record_button"


def create_mappings(control_surface: ControlSurface):
    mappings = {}

    # Session navigation is always active.
    mappings["SessionNavigation"] = dict(
        up_button="rewind_button",
        down_button="fast_forward_button",
        left_button="track_left_button",
        right_button="track_right_button",
    )

    mappings["Mixer"] = dict(
        # Sliders always control track volume.
        volume_controls="sliders",
    )

    # The common setup shared by default, shift, and alt modes.
    #
    # The raw object gets modified during mode creation, so we need to
    # recreate the object whenever it's needed.
    def sends_mode():
        return dict(
            component="Mixer",
            send_controls="knobs",
            next_send_button="marker_right_button",
            prev_send_button="marker_left_button",
        )

    # A mode that just selects another mode. We use this to get a
    # different button color when selecting e.g. SHIFT mode from
    # DEFAULT mode versus SHIFT mode from ALT mode. Specifically, in
    # DEFAULT mode, all mode buttons are lit, but in the other modes,
    # only the back-to-DEFAULT button is lit.
    def set_selected_mode_mode(target_mode_name):
        def on_enter():
            control_surface.component_map["Modes"].selected_mode = target_mode_name

        return CallFunctionMode(on_enter_fn=on_enter)

    mappings["Modes"] = dict(
        modes_component_type=ModesComponent,
        # Use wrapper modes to get a different button color when DEFAULT is active.
        shift_from_default_button=SHIFT_BUTTON,
        alt_from_default_button=ALT_BUTTON,
        ctrl_from_default_button=CTRL_BUTTON,
        default=dict(
            modes=[
                dict(
                    component="Session",
                    clip_launch_buttons="mixer_buttons",
                ),
                sends_mode(),
            ]
        ),
        shift_from_default=set_selected_mode_mode("shift"),
        alt_from_default=set_selected_mode_mode("alt"),
        ctrl_from_default=set_selected_mode_mode("ctrl"),
        shift=dict(
            modes=[
                dict(
                    component="Mixer",
                    solo_buttons="solo_buttons",
                    mute_buttons="mute_buttons",
                    arm_buttons="arm_buttons",
                ),
                dict(
                    component="Modes",
                    default_button=SHIFT_BUTTON,
                    alt_button=ALT_BUTTON,
                    ctrl_button=CTRL_BUTTON,
                ),
                sends_mode(),
            ]
        ),
        alt=dict(
            modes=[
                dict(
                    component="Session",
                    stop_track_clip_buttons="arm_buttons",
                ),
                dict(
                    component="Mixer",
                    reset_send_buttons="solo_buttons",
                    track_select_buttons="mute_buttons",
                ),
                dict(
                    component="Modes",
                    shift_button=SHIFT_BUTTON,
                    default_button=ALT_BUTTON,
                    ctrl_button=CTRL_BUTTON,
                ),
                sends_mode(),
            ]
        ),
        ctrl=dict(
            modes=[
                dict(
                    component="Device",
                    parameter_controls="knobs",
                    device_lock_button="marker_set_button",
                    device_on_off_button="cycle_button",
                ),
                dict(
                    component="DeviceNavigation",
                    prev_button="marker_left_button",
                    next_button="marker_right_button",
                ),
                dict(component="Mixer", clip_view_buttons="solo_buttons"),
                dict(
                    component="Transport",
                    stop_button=f"mixer_buttons_raw[{2 * NUM_TRACKS}]",
                    play_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 1}]",
                    clip_trigger_quantization_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 3}]",
                    tempo_down_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 4}]",
                    tempo_up_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 5}]",
                    metronome_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 6}]",
                ),
                dict(
                    component="Recording",
                    arrangement_record_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 2}]",
                ),
                dict(
                    component="Session",
                    scene_launch_buttons="scene_launch_buttons",
                    stop_all_clips_button=f"mixer_buttons_raw[{2 * NUM_TRACKS + 7}]",
                ),
                dict(
                    component="Modes",
                    shift_button=SHIFT_BUTTON,
                    alt_button=ALT_BUTTON,
                    default_button=CTRL_BUTTON,
                ),
            ]
        ),
    )

    return mappings
