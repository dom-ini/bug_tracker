import pytest
from core.validators import validate_file_size, validate_file_type, validate_mime_type
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def txt_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("example.txt", b"Sample content", content_type="text/plain")


def test_validate_mime_type_valid(mocker: MockerFixture, txt_file: SimpleUploadedFile) -> None:
    mocker.patch("core.validators.magic.Magic", return_value=mocker.Mock(from_buffer=lambda _: "text/plain"))
    allowed = {"txt": "text/plain"}

    validate_mime_type(txt_file, allowed_file_types=allowed)


def test_validate_mime_type_invalid_mime_type(mocker: MockerFixture, txt_file: SimpleUploadedFile) -> None:
    mocker.patch("core.validators.magic.Magic", return_value=mocker.Mock(from_buffer=lambda _: "application/pdf"))
    allowed = {"txt": "text/plain"}

    with pytest.raises(ValidationError):
        validate_mime_type(txt_file, allowed_file_types=allowed)


def test_validate_file_type_valid(mocker: MockerFixture, txt_file: SimpleUploadedFile) -> None:
    validate_file_type(
        txt_file,
        extension_validator=mocker.Mock(),
        mime_type_validator=mocker.Mock(),
    )


def test_validate_file_type_invalid_extension(mocker: MockerFixture, txt_file: SimpleUploadedFile) -> None:
    mock_extension_validator = mocker.Mock(side_effect=ValidationError("Invalid extension"))

    with pytest.raises(ValidationError):
        validate_file_type(
            txt_file,
            extension_validator=mock_extension_validator,
            mime_type_validator=mocker.Mock(),
        )


def test_validate_file_type_invalid_mime_type(mocker: MockerFixture, txt_file: SimpleUploadedFile) -> None:
    mock_mime_type_validator = mocker.Mock(side_effect=ValidationError("Invalid extension"))

    with pytest.raises(ValidationError):
        validate_file_type(
            txt_file,
            extension_validator=mocker.Mock(),
            mime_type_validator=mock_mime_type_validator,
        )


def test_validate_file_size_valid() -> None:
    file = SimpleUploadedFile("file.txt", b"12345")

    validate_file_size(file, max_size=1024)


def test_validate_file_size_too_large() -> None:
    file = SimpleUploadedFile("file.txt", b"12345")

    with pytest.raises(ValidationError):
        validate_file_size(file, max_size=1)
