from .existing_maps import ExistingMapsMixin
from .folder_validation import FolderValidationMixin
from .validation_mixin import ValidationMainMixin


class ValidationMixin(
    ValidationMainMixin,
    FolderValidationMixin,
    ExistingMapsMixin,
):
    pass


__all__ = [
    "ExistingMapsMixin",
    "FolderValidationMixin",
    "ValidationMainMixin",
    "ValidationMixin",
]
