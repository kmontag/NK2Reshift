import logging
import typing

from ableton.v3.base import const, inject
from ableton.v3.control_surface import (
    ControlSurface,
    ControlSurfaceSpecification,
    create_skin,
)
from ableton.v3.control_surface.capabilities import (
    CONTROLLER_ID_KEY,
    NOTES_CC,
    PORTS_KEY,
    REMOTE,
    SCRIPT,
    controller_id,
    inport,
    outport,
)
from ableton.v3.control_surface.legacy_bank_definitions import best_of_banks

from .colors import Skin
from .configuration import Configuration
from .elements import NUM_SCENES, NUM_TRACKS, Elements
from .mappings import create_mappings
from .mixer import MixerComponent
from .transport import TransportComponent

logger = logging.getLogger(__name__)

# Load a local configuration if possible, or fall back to the default.
_local_configuration: typing.Union[None, Configuration] = None
try:
    from .configuration_local import (  # type: ignore
        configuration as _local_configuration,  # type: ignore
    )

    logger.info("loaded local configuration")

except (ImportError, ModuleNotFoundError):
    logger.info("loaded default configuration")

_configuration: Configuration = _local_configuration or Configuration()


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=0x0944,
            product_ids=0x0117,
            model_name=["nanoKONTROL2"],
        ),
        PORTS_KEY: [
            inport(props=[NOTES_CC]),
            inport(props=[NOTES_CC, SCRIPT, REMOTE]),
            outport(props=[NOTES_CC]),
            outport(props=[NOTES_CC, SCRIPT, REMOTE]),
        ],
    }


def create_instance(c_instance):
    return NK2Reshift(c_instance=c_instance)


class Specification(ControlSurfaceSpecification):
    identity_response_id_bytes = (0x42, 0x13, 0x01)
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin)
    num_tracks = NUM_TRACKS
    num_scenes = NUM_SCENES
    create_mappings_function = create_mappings
    component_map = {
        "Mixer": MixerComponent,
        "Transport": TransportComponent,
    }

    # Use legacy parameter banks to preserve behavior from the
    # original script.
    parameter_bank_definitions = best_of_banks()


class NK2Reshift(ControlSurface):
    def __init__(self, *a, **k):
        super().__init__(*a, specification=Specification, **k)

    # Dependencies to be injected throughout the application.
    #
    # We need the `Any` return type because otherwise the type checker
    # infers `None` as the only valid return type.
    def _get_additional_dependencies(self) -> typing.Any:
        deps: typing.Dict[str, typing.Any] = (
            super()._get_additional_dependencies() or {}
        )

        deps["configuration"] = const(_configuration)

        return deps

    @staticmethod
    def _create_elements(specification: ControlSurfaceSpecification):
        # Element creation happens before the main dependency injector
        # is built, so we need to explicitly inject any necessary
        # dependencies for this stage.
        with inject(configuration=const(_configuration)).everywhere():
            return super(NK2Reshift, NK2Reshift)._create_elements(specification)

    def setup(self):
        super().setup()
        logger.info(f"{self.__class__.__name__} setup complete")

    def on_identified(self, response_bytes):
        super().on_identified(response_bytes)
        logger.info("identified nanoKONTROL2 device")
