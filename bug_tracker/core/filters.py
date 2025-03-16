from abc import ABC
from typing import Sequence

from core.utils import snake_to_title_case
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _


class BaseOrdering(ABC):
    base_fields: Sequence[str] = ()

    @classmethod
    def _generate_ordering_fields(cls, fields: Sequence[str]) -> Sequence[tuple[str, str]]:
        result = []
        for field in fields:
            label = _(snake_to_title_case(field))
            result.append((field, label))
            result.append((f"-{field}", f"{label} {_("(descending)")}"))
        return result

    @classproperty
    def fields(cls) -> Sequence[tuple[str, str]]:
        return cls._generate_ordering_fields(cls.base_fields)
