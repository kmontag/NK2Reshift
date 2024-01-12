import typing

from ableton.v3.control_surface.components import (
    TransportComponent as TransportComponentBase,
)
from ableton.v3.control_surface.controls import ButtonControl

import Live

TEMPO_MIN = 20.0
TEMPO_MAX = 999.0

# Ignore triplet quantizations.
IGNORED_QUANTIZATIONS = [
    Live.Song.Quantization.q_half_triplet,
    Live.Song.Quantization.q_quarter_triplet,
    Live.Song.Quantization.q_eight_triplet,
    Live.Song.Quantization.q_sixtenth_triplet,
]


class TransportComponent(TransportComponentBase):
    tempo_up_button: typing.Any = ButtonControl(
        color="DefaultButton.Off", pressed_color="DefaultButton.On"
    )
    tempo_down_button: typing.Any = ButtonControl(
        color="DefaultButton.Off", pressed_color="DefaultButton.On"
    )
    clip_trigger_quantization_button: typing.Any = ButtonControl(
        color="DefaultButton.Off", pressed_color="DefaultButton.On"
    )

    @tempo_up_button.pressed
    def tempo_up_button(self, _):
        self._adjust_tempo(1)

    @tempo_down_button.pressed
    def tempo_down_button(self, _):
        self._adjust_tempo(-1)

    @clip_trigger_quantization_button.pressed
    def clip_trigger_quantization_button(self, _):
        assert self.song
        self.song.clip_trigger_quantization = self._get_next_clip_trigger_quantization(
            self.song.clip_trigger_quantization
        )

    def _adjust_tempo(self, amount):
        assert self.song
        self.song.tempo = max(TEMPO_MIN, min(TEMPO_MAX, self.song.tempo + amount))

    def _get_next_clip_trigger_quantization(self, start):
        new_index = int(start) + 1
        if new_index not in Live.Song.Quantization.values:
            new_index = 0

        result = Live.Song.Quantization.values[new_index]

        # Skip to the next value if the result is in the blacklist.
        if result in IGNORED_QUANTIZATIONS:
            result = self._get_next_clip_trigger_quantization(result)

        return result
