from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

ABSTAIN_KEY = "__abstain__"
OptionId = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=128),
]


class ChoiceOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: OptionId
    label: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, min_length=1, max_length=512
        ),
    ]


class ChoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instruction: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, min_length=1, max_length=2048
        ),
    ]
    text: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, min_length=1, max_length=32768
        ),
    ]
    options: list[ChoiceOption] = Field(min_length=1, max_length=254)

    @model_validator(mode="after")
    def validate_option_ids(self):
        ids = [option.id for option in self.options]
        if len(ids) != len(set(ids)) or ABSTAIN_KEY in ids:
            raise ValueError("Option IDs must be unique and must not use __abstain__")
        return self


class ChoiceResponse(BaseModel):
    status: Literal["matched", "abstain"]
    selected_id: str | None
    confidence: float = Field(strict=True, ge=0, le=1, allow_inf_nan=False)
