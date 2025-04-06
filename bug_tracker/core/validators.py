from pathlib import Path

import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

default_extension_validator = FileExtensionValidator(allowed_extensions=settings.ATTACHMENTS_ALLOWED_FILE_TYPES.keys())


def validate_file_type(file: File, extension_validator=default_extension_validator) -> None:
    extension_validator(file)

    mime_type = magic.Magic(mime=True).from_buffer(file.read(2048))
    ext = Path(file.name).suffix.lstrip(".").lower()
    expected_mime_type = settings.ATTACHMENTS_ALLOWED_FILE_TYPES.get(ext)

    if expected_mime_type and mime_type != expected_mime_type:
        raise ValidationError(
            _('Invalid file type. Expected "%(expected)s", got "%(actual)s"')
            % {"expected": expected_mime_type, "actual": mime_type}
        )
