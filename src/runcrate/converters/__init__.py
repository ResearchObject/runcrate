from .base import converter
from .cwl import cwlConverter


CONVERTERS = {
    "base": converter(),
    "cwl": cwlConverter(),
}
