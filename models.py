from pydantic import BaseModel


class Template(BaseModel):
    template_name: str
    deployment: dict