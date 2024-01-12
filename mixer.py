import typing
from itertools import zip_longest

from ableton.v3.base import depends
from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.controls import ButtonControl

from .channel_strip import ChannelStripComponent


class MixerComponent(MixerComponentBase):
    prev_send_button: typing.Any = ButtonControl(
        color="DefaultButton.Off", pressed_color="DefaultButton.On"
    )
    next_send_button: typing.Any = ButtonControl(
        color="DefaultButton.Off", pressed_color="DefaultButton.On"
    )

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

    def set_prev_send_button(self, button):
        self.prev_send_button.set_control_element(button)

    def set_next_send_button(self, button):
        self.next_send_button.set_control_element(button)

    def set_clip_view_buttons(self, buttons):
        self._clip_view_buttons = buttons
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.clip_view_button.set_control_element(button)
            strip.update()

    def set_reset_send_buttons(self, buttons):
        self._reset_send_buttons = buttons
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.reset_send_button.set_control_element(button)
            strip.update()

    @prev_send_button.pressed
    def prev_send_button(self, _):
        self._increment_send_index(-1)

    @next_send_button.pressed
    def next_send_button(self, _):
        self._increment_send_index(1)

    def _increment_send_index(self, amount: int):
        if self._send_index_manager.num_sends > 0:
            self._send_index_manager.send_index = (
                self._send_index_manager.send_index + amount
            ) % self._send_index_manager.num_sends

    def _on_send_index_changed(self):
        self._show_message(f"Controlling Send {self.send_index+ 1}")
        return super()._on_send_index_changed()
