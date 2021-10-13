from marshmallow import fields
from . import BaseSchema
from marshmallow_sqlalchemy  import auto_field
from marshmallow.fields import Date
from marshmallow_sqlalchemy.fields import Nested

from app.models.user import User

from app.schemas.role_schema import RoleSchema
from app.schemas.phone_schema import PhoneSchema

class UserSchema(BaseSchema):
    class Meta:
        model=User
        load_instance=True
        dateformat = '%Y-%m-%dT%H:%M:%S'
    
    id = auto_field()
    name = auto_field()
    additional_info = auto_field()
    created_at = Date()
    updated_at = Date()

    roles = Nested(RoleSchema, many=True)
    phones = Nested(PhoneSchema, many=True)

    # def on_bind_field(self, field_name, field_obj):
    #     super().on_bind_field(field_name, field_obj)
        
        