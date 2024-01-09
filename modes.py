import typing

from ableton.v3.base import depends
from ableton.v3.control_surface.mode import ModesComponent as ModesComponentBase

from .configuration import Configuration


class ModesComponent(ModesComponentBase):
    @depends(configuration=None)
    def __init__(self, *a, configuration: typing.Union[None, Configuration], **k):
        super().__init__(*a, **k)

        assert configuration

        self.selected_mode = configuration.initial_mode
