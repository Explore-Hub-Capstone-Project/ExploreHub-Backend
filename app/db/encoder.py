from bson import ObjectId
from fastapi.encoders import jsonable_encoder


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Not a valid ObjectId: {v}")
        return str(v)


def custom_jsonable_encoder(obj, by_alias: bool = False, exclude_none: bool = False):
    if isinstance(obj, ObjectId):
        return str(obj)
    return jsonable_encoder(obj, by_alias=by_alias, exclude_none=exclude_none)
