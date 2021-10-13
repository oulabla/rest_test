from . import BaseSchema
from marshmallow_sqlalchemy  import auto_field
from marshmallow.fields import Date
from app.models.phone import Phone


class PhoneSchema(BaseSchema):
    class Meta:
        model=Phone
        load_instance=True
        dateformat = '%Y-%m-%dT%H:%M:%S'
    
    id = auto_field()
    phone = auto_field()
