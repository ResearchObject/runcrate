from .base import Converter
from .cwl import CwlConverter


CONVERTERS = {
    "base": Converter(),
    "cwl": CwlConverter(),
}
