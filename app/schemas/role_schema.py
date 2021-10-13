from . import BaseSchema
from marshmallow_sqlalchemy  import auto_field
from marshmallow.fields import Date
from app.models.user import User


class RoleSchema(BaseSchema):
    class Meta:
        model=User
        load_instance=True
        dateformat = '%Y-%m-%dT%H:%M:%S'
    
    id = auto_field()
    name = auto_field()
    created_at = Date()
    updated_at = Date()
