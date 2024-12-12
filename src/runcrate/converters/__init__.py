from .base import Converter
from .cwl import CwlConverter


CONVERTERS = {
    "cwl": CwlConverter(),
}
