import magic
from core.utils import bytes_to_mib, get_file_extension
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

default_extension_validator = FileExtensionValidator(allowed_extensions=settings.ATTACHMENTS_ALLOWED_FILE_TYPES.keys())


def validate_mime_type(
    file: File, allowed_file_types: dict[str, str] = settings.ATTACHMENTS_ALLOWED_FILE_TYPES
) -> None:
    mime_type = magic.Magic(mime=True).from_buffer(file.read(2048))
    ext = get_file_extension(file.name)
    expected_mime_type = allowed_file_types.get(ext)

    if expected_mime_type and mime_type != expected_mime_type:
        raise ValidationError(
            _('Invalid file type. Expected "%(expected)s", got "%(actual)s"')
            % {"expected": expected_mime_type, "actual": mime_type}
        )


def validate_file_type(
    file: File, extension_validator=default_extension_validator, mime_type_validator=validate_mime_type
) -> None:
    extension_validator(file)
    mime_type_validator(file)


def validate_file_size(file: File, max_size: int = settings.ATTACHMENTS_MAX_SIZE) -> None:
    if file.size > max_size:
        raise ValidationError(
            _("File should not exceed %(max_size)s MiB.") % {"max_size": f"{bytes_to_mib(max_size):.6f}"}
        )
