from dataclasses import dataclass

from fastapi import Request
from jinja2 import Environment

from ..edit.render import ALLOW_EDITING_VIA_FORMS
from ..loader import ENV


@dataclass
class Home:
    request: Request
    env: Environment = ENV
    template: str = "templates/home.jinja"

    def __str__(self) -> str:
        return self.env.get_template(self.template).render(
            request=self.request,
            edit_on=ALLOW_EDITING_VIA_FORMS,
        )

    def encode(self, charset: str) -> str:
        return str(self).encode(encoding=charset)
