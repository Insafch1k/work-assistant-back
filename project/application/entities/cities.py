from pydantic import ConfigDict, BaseModel


class City(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

