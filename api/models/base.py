from pydantic import BaseModel, ConfigDict

class SecureBaseModel(BaseModel):
    """
    Hardened base model for security
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        strict=True,
        frozen=True
    )