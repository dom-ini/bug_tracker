from typing import Callable, ParamSpec, TypeVar

from django.db.models import Model
from django.http import Http404

ModelT = TypeVar("ModelT", bound=Model)
P = ParamSpec("P")
Selector = Callable[P, ModelT | None]


def query_or_404(selector: Selector, *args: P.args, **kwargs: P.kwargs) -> ModelT:
    obj = selector(*args, **kwargs)
    if not obj:
        raise Http404
    return obj
