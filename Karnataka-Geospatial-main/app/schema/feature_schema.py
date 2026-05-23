from pydantic import BaseModel


class FeatureResponse(BaseModel):

    id: int
    name: str

    class Config:

        from_attributes = True