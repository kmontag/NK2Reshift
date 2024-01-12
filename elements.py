from __future__ import annotations

import typing

from ableton.v3.base import depends, task
from ableton.v3.control_surface import ElementsBase
from ableton.v3.control_surface.elements import ButtonElement

from .colors import BlinkManager
from .configuration import (
    ButtonConfiguration,
    Configuration,
    EncoderConfiguration,
)
from .live import lazy_attribute

NUM_TRACKS = 8
NUM_SCENES = 3


class BlinkingButtonElement(ButtonElement):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        # Current blink value generator, if any.
        self._value_generator: typing.Union[None, BlinkManager.ValueGenerator] = None

        # Help the type checker.
        self._tasks: task.TaskGroup

    def send_value(self, value, force=False, channel=None, is_blinking=False):
        """
        :param bool is_blinking: whether this value is being sent as part of the blinking task.
        """

        # Don't kill the blink task if this is being called as
        # part of the blink loop.
        if not is_blinking:
            self._stop_blinking()

        return super().send_value(value, force, channel)

    # This gets invoked by `BlinkingColor` skin values.
    def send_blink(self, ticks_per_toggle: int, blink_manager: BlinkManager):
        # Don't do anything if we're already blinking at this rate.
        if not (
            self._value_generator
            and self._value_generator.ticks_per_toggle is ticks_per_toggle
        ):
            self._start_blinking(ticks_per_toggle, blink_manager)

    def _start_blinking(self, ticks_per_toggle, blink_manager):
        # Clean up the old blink state, if any.
        self._stop_blinking()

        self._value_generator = blink_manager.get_value_generator(ticks_per_toggle)
        self._blink_task.restart()

    def _stop_blinking(self):
        if self._value_generator:
            self._value_generator.disconnect()
            self._value_generator = None
            # Include this within the conditional - if no value
            # generator has been set, the blink task must be killed or
            # non-existent, so there's no need to call the lazy
            # generator.
            self._blink_task.kill()

    @lazy_attribute
    def _blink_task(self):
        assert self._tasks
        blink_task = self._tasks.add(task.loop(task.run(self._handle_blink_tick)))
        blink_task.kill()
        return blink_task

    def _handle_blink_tick(self):
        assert self._value_generator
        self._value_generator.on_tick()

        value = self._value_generator.value
        if value is not self._last_sent_value:
            self.send_value(value, is_blinking=True)


class Elements(ElementsBase):
    @depends(configuration=None)
    def __init__(
        self, *a, configuration: typing.Union[None, Configuration] = None, **k
    ):
        super().__init__(*a, **k)

        assert configuration
        self._configuration = configuration

        # Type checker helpers for implicitly created attributes.
        self.mixer_buttons = None

        self._add_physical_elements()
        self._add_meta_elements()

    # The base class' button helpers don't allow for providing
    # an alternate button factory via arguments; we need to reimplement them with
    # our own button-create method.
    def add_button(self, identifier, name, **k):
        attr_name = self._create_attribute_name(name)
        k["channel"] = k.get("channel", self._global_channel)
        setattr(self, attr_name, self._create_button(identifier, name, **k))

    def add_button_matrix(self, identifiers, base_name, channels=None, *a, **k):
        (self.add_matrix)(
            identifiers,
            base_name,
            *a,
            channels=channels,
            element_factory=self._create_button,
            **k,
        )

    def _create_button(self, identifier, name, **k):
        return BlinkingButtonElement(identifier, name=name, **k)

    def _add_physical_elements(self):
        for name in [
            "track_left_button",
            "track_right_button",
            "cycle_button",
            "marker_set_button",
            "marker_left_button",
            "marker_right_button",
            "rewind_button",
            "fast_forward_button",
            "stop_button",
            "play_button",
            "record_button",
        ]:
            control_config = getattr(self._configuration, name)
            self.add_button(
                control_config.identifier,
                name,
                msg_type=control_config.msg_type,
                channel=control_config.channel,
            )

        def get_matrix_args(
            # List of list of control configurations.
            row_configurations: typing.List[typing.List[typing.Any]],
            # Attributes that should be mapped into a list of
            # lists. Keys are the matrix creation helper argument
            # name, values are the name of the attribute on individual
            # control configurations.
            variadic_attrs: typing.Dict[str, str],
            # Attributes provided as additional kwargs. These need to
            # be the same for all individual control configurations.
            common_attrs: typing.List[str],
        ):
            assert len(row_configurations) > 0 and len(row_configurations[0]) > 0
            example_control = row_configurations[0][0]

            common_attr_values = {}
            for common_attr in common_attrs:
                common_attr_values[common_attr] = getattr(example_control, common_attr)

            for row_configuration in row_configurations:
                assert len(row_configuration) is NUM_TRACKS
                for control_configuration in row_configuration:
                    for common_attr, common_attr_value in common_attr_values.items():
                        assert (
                            getattr(control_configuration, common_attr)
                            is common_attr_value
                        )

            variadic_attr_values = {}
            for arg_name, attr_name in variadic_attrs.items():
                variadic_attr_values[arg_name] = [
                    [
                        getattr(control_configuration, attr_name)
                        for control_configuration in row_configuration
                    ]
                    for row_configuration in row_configurations
                ]

            return dict(**common_attr_values, **variadic_attr_values)

        def get_encoder_matrix_args(
            row_configurations: typing.List[typing.List[EncoderConfiguration]],
        ):
            return get_matrix_args(
                row_configurations,
                dict(identifiers="identifier", channels="channel"),
                ["msg_type", "map_mode"],
            )

        def get_button_matrix_args(
            row_configurations: typing.List[typing.List[ButtonConfiguration]],
        ):
            return get_matrix_args(
                row_configurations,
                dict(identifiers="identifier", channels="channel"),
                ["msg_type"],
            )

        self.add_button_matrix(
            base_name="mixer_buttons",
            **get_button_matrix_args(
                [
                    self._configuration.solo_buttons,
                    self._configuration.mute_buttons,
                    self._configuration.arm_buttons,
                ]
            ),
        )

        self.add_encoder_matrix(
            base_name="sliders",
            **get_encoder_matrix_args([self._configuration.sliders]),
        )
        self.add_encoder_matrix(
            base_name="knobs", **get_encoder_matrix_args([self._configuration.knobs])
        )

    def _add_meta_elements(self):
        self.add_submatrix(self.mixer_buttons, "solo_buttons", rows=(0, 1))
        self.add_submatrix(self.mixer_buttons, "mute_buttons", rows=(1, 2))
        self.add_submatrix(self.mixer_buttons, "arm_buttons", rows=(2, 3))

        # A subset of the mute buttons are used for scene launch.
        self.add_submatrix(
            self.mixer_buttons,
            "scene_launch_buttons",
            columns=(0, NUM_SCENES),
            rows=(1, 2),
        )
