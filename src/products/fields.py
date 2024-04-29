import re

from django.db import models


class RegexpIntegerField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        self.regexp = kwargs.pop("regexp", "")
        self.group = kwargs.pop("group", "")
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        try:
            print(re.search(self.regexp, value))
            cleaned_value = (
                re.search(self.regexp, value).group(self.group).replace("\u2009", "")
            )
            print(cleaned_value)
        except AttributeError:
            return super().get_prep_value(value)
        else:
            return super().get_prep_value(cleaned_value)

    def to_python(self, value):
        try:
            cleaned_value = (
                re.search(self.regexp, value).group(self.group).replace("\u2009", "")
            )
        except AttributeError:
            return super().to_python(value)
        else:
            return super().to_python(cleaned_value)
