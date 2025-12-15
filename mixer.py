import typing
from itertools import zip_longest

from ableton.v3.base import depends
from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase

from .channel_strip import ChannelStripComponent


class MixerComponent(MixerComponentBase):
    @depends(show_message=None)
    def __init__(
        self,
        *a,
        channel_strip_component_type=ChannelStripComponent,
        show_message: typing.Optional[typing.Callable[[str], typing.Any]] = None,
        **k,
    ):
        super().__init__(
            *a, channel_strip_component_type=channel_strip_component_type, **k
        )

        assert show_message
        self._show_message = show_message

        self._clip_view_buttons = None
        self._reset_send_buttons = None

    def set_clip_view_buttons(self, buttons):
        self._clip_view_buttons = buttons
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.clip_view_button.set_control_element(button)
            strip.update()

    def set_reset_send_buttons(self, buttons):
        self._reset_send_buttons = buttons
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            assert isinstance(strip, ChannelStripComponent)
            strip.reset_send_button.set_control_element(button)
            strip.update()

    def _on_send_index_changed(self):
        self._show_message(
            f"Controlling Send {self._send_index_control.send_index + 1}"
        )
        return super()._on_send_index_changed()
