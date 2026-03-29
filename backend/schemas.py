from pydantic import BaseModel

# This is the expected format when a user sends movie data to our API
class MovieCreate(BaseModel):
    title: str
    year: int
    director: str
    genre: str
    description: str

    class Config:
        from_attributes = True