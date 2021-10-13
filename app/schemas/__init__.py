from marshmallow_sqlalchemy.schema import SQLAlchemySchema

class BaseSchema(SQLAlchemySchema):
    
    @staticmethod    
    def camelcase(s):
        parts = iter(s.split("_"))
        return next(parts) + "".join(i.title() for i in parts)
    
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = BaseSchema.camelcase(field_obj.data_key or field_name)