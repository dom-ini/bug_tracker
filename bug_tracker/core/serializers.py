from typing import Sequence

from rest_framework import exceptions, serializers


class CommaSeparatedMultipleChoiceField(serializers.MultipleChoiceField):
    def to_internal_value(self, data: Sequence) -> str:
        for item in data:
            if item not in self.choice_strings_to_values:
                self.fail("invalid_choice", input=item)
        return ",".join(data)


def create_validation_error_for_field(field: str, message: str) -> exceptions.ValidationError:
    return exceptions.ValidationError({field: [message]})
