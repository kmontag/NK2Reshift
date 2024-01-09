from __future__ import annotations

from ableton.v3.control_surface.colors import BasicColors
from ableton.v3.control_surface.elements import Color


# Keeps track of the current position within a cycle of some number of
# ticks, and provides objects to generate on/off LED values which are
# synchronized with the cycle. This is used to synchronize the timing
# of blinking LEDs, so that the controller doesn't look too wacky when
# multiple buttons are blinking.
class BlinkManager:
    class ValueGenerator:
        def __init__(
            self, parent: BlinkManager, ticks_per_toggle: int, cycle_position: int
        ):
            self._parent = parent
            self._ticks_per_toggle = ticks_per_toggle
            self._cycle_position = cycle_position

        @property
        def ticks_per_toggle(self):
            return self._ticks_per_toggle

        # This is expected to be called once on every tick while the blink is active.
        def on_tick(self):
            self._cycle_position = (self._cycle_position + 1) % self._parent.cycle_ticks
            self._parent._set_cycle_position(self._cycle_position)

        # Get the value that should be sent to the button on the
        # current tick. This should be accessed after `on_tick` is
        # called for a given tick.
        @property
        def value(self) -> int:
            toggle_cycle_ticks = self._ticks_per_toggle * 2

            # Move the local cycle position in reverse, to allow for a short initial OFF value followed by
            toggle_cycle_position = (
                self._cycle_position
                # self._parent.cycle_ticks - self._cycle_position
            ) % toggle_cycle_ticks

            # Initially lit, then turned off for the second half of the cycle.
            return 127 if toggle_cycle_position < self._ticks_per_toggle else 0

        def disconnect(self):
            self._parent._value_generator_disconnected()

    def __init__(self, cycle_ticks: int):
        self._cycle_ticks = cycle_ticks
        self._cycle_position = 0
        self._num_active_value_generators = 0

    @property
    def cycle_ticks(self) -> int:
        return self._cycle_ticks

    def get_value_generator(self, ticks_per_toggle: int):
        if self._num_active_value_generators == 0:
            # UX hack - if there are no other buttons currently
            # blinking, advance the cycle position to start in the OFF
            # state, for better visual feedback in the typical case
            # when the button is already lit.
            #
            # As opposed to just starting with the OFF state in the
            # `ValueGenerator`, this allows us to use the cycle length
            # to display OFF for a short number of ticks, then ON for
            # a longer number of ticks (e.g. if the cycle length is 4
            # and our `ticks_per_toggle` is 3).
            #
            # We could make `ticks_per_toggle` an array if we ever
            # need more flexibility here.
            self._cycle_position = ticks_per_toggle - 1

        self._num_active_value_generators += 1
        return BlinkManager.ValueGenerator(
            parent=self,
            ticks_per_toggle=ticks_per_toggle,
            cycle_position=self._cycle_position,
        )

    def _value_generator_disconnected(self):
        # This method shouldn't be called except by a currently-active value generator.
        self._num_active_value_generators -= 1
        assert self._num_active_value_generators >= 0

        # Reset the cycle position when nothing is blinking.
        if self._num_active_value_generators == 0:
            self._cycle_position = 0

    # Called by all active value generators on every tick. The value
    # generators should always all be at the same cycle position, so
    # repeated calls on the same tick will just be a no-op.
    def _set_cycle_position(self, cycle_position: int):
        self._cycle_position = cycle_position


# A color which interacts with our custom `BlinkingButtonElement` to
# send blinking effects.
class BlinkingColor(Color):
    def __init__(self, ticks: int, blink_manager: BlinkManager, *a, **k):
        """
        :param int ticks: the number of task ticks (one per 100ms) comprising a single ON
                          or OFF period for the button. In practice, the number of ticks
                          during which a given state is shown will also depend on the cycle
                          length of the associated `BlinkManager`.
        """
        super().__init__(*a, **k)

        self._ticks = ticks
        self._blink_manager = blink_manager

    @property
    def ticks(self):
        return self._ticks

    def draw(self, interface):
        # Any button to which this color is assigned must implement
        # our custom `BlinkingButtonElement` interface.
        interface.send_blink(self.ticks, self._blink_manager)


_blink_manager = BlinkManager(8)
BLINK = BlinkingColor(6, _blink_manager)
BLINK_FAST = BlinkingColor(2, _blink_manager)


class Skin:
    class Modes:
        # When a non-default mode is active, we replace its usual
        # button with a default-mode button, which should be
        # highlighted.
        class Default:
            On = BasicColors.OFF
            Off = BasicColors.ON

        # When default mode is active, all mode buttons should be
        # highlighted.
        class ShiftFromDefault(Default):
            pass

        class AltFromDefault(Default):
            pass

        class CtrlFromDefault(Default):
            pass

    class Session:
        ClipStopped = BasicColors.ON

        ClipPlaying = BLINK
        ClipRecording = BLINK

        ClipTriggeredPlay = BLINK_FAST
        ClipTriggeredRecord = BLINK_FAST

        SlotTriggeredPlay = BLINK_FAST
        SlotTriggeredRecord = BLINK_FAST

    class Transport:
        StopOn = BasicColors.OFF
