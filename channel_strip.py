import typing

from ableton.v3.base import MultiSlot, listens
from ableton.v3.control_surface.components import (
    ChannelStripComponent as ChannelStripComponentBase,
)
from ableton.v3.control_surface.controls import ButtonControl
from ableton.v3.live import liveobj_changed, liveobj_valid


class ChannelStripComponent(ChannelStripComponentBase):
    # Selects this track, selects the first device in the chain (if
    # any), and momentarily shows the clip view, then switches to
    # device view when released.
    clip_view_button: typing.Any = ButtonControl(
        color="DefaultButton.Off",
        on_color="DefaultButton.On",
        disabled_color="Mixer.NoTrack",
    )

    # Resets the currently-selected send to 0, according to the parent
    # mixer's `send_index`.
    reset_send_button: typing.Any = ButtonControl(
        color="DefaultButton.Off",
        pressed_color="DefaultButton.On",
        disabled_color="Mixer.NoTrack",
    )

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for view_name in ("Detail", "Detail/DeviceChain"):
            self.register_slot(
                MultiSlot(
                    subject=(self.application.view),
                    listener=(self._update_clip_view_button),
                    event_name_list=("is_view_visible",),
                    extra_args=(view_name,),
                )
            )

        assert self.song

        # This will also fire when tracks are added/removed from the set.
        self.register_slot(
            self.song.view, self._update_clip_view_button, "selected_track"
        )

        assert self.__on_track_select_button_is_held_value
        self.__on_track_select_button_is_held_value.subject = self.track_select_button

    @clip_view_button.pressed
    def clip_view_button(self, _):  # type: ignore
        self._select_track()
        self._show_clip_view()
        self._select_first_device()

    @clip_view_button.released
    def clip_view_button(self, _):
        self._show_device_view()

    @reset_send_button.pressed
    def reset_send_button(self, _):
        # The parent is a MixerComponent.
        assert self.parent
        send_index = self.parent.send_index or 0

        assert self._track
        sends = self._track.mixer_device.sends

        if send_index < len(sends):
            sends[send_index].value = 0

    def update(self):
        super().update()
        self._update_clip_view_button()
        self._update_reset_send_button()

    def _select_first_device(self):
        assert self.song
        assert self._track

        devices = self._track.devices
        if devices is not None and len(devices) > 0:
            self.song.view.select_device(devices[0])

    def _show_clip_view(self):
        self.application.view.show_view("Detail/Clip")

    def _show_device_view(self):
        self.application.view.show_view("Detail/DeviceChain")

    def _toggle_track_folded(self):
        if self._track and self._track.is_foldable:
            self._track.fold_state = not self._track.fold_state

    def _update_clip_view_button(self):
        assert self.song

        has_clip_slots = self._has_clip_slots()
        self.clip_view_button.enabled = has_clip_slots

        if has_clip_slots:
            # Match the initial LED behavior of CTRL mode in the
            # original control surface script: if the device view is
            # visible, light the selected track, otherwise don't light
            # anything.
            self.clip_view_button.is_on = (
                self.application.view.is_view_visible("Detail")
                and self.application.view.is_view_visible("Detail/DeviceChain")
                and not liveobj_changed(self.song.view.selected_track, self._track)
            )

    def _update_reset_send_button(self):
        self.reset_send_button.enabled = self._has_sends()

    def _has_sends(self):
        return (
            liveobj_valid(self._track)
            and self.song
            and self._track
            and self._track != self.song.master_track
            and len(self._track.mixer_device.sends) > 0
        )

    def _has_clip_slots(self):
        return (
            self._track
            and liveobj_valid(self._track)
            and len(self._track.clip_slots) > 0
        )

    @listens("is_held")
    def __on_track_select_button_is_held_value(self, is_held):
        if is_held:
            self._toggle_track_folded()
