from marshmallow import Schema, ValidationError, fields, validate


class CategoriaSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=120))
    descripcion = fields.String(allow_none=True)
    estado = fields.Boolean(load_default=True)
    fecha_creacion = fields.DateTime(dump_only=True)


class CategoriaQuerySchema(Schema):
    nombre = fields.String(load_default=None)
    estado = fields.Boolean(load_default=None)


class CategoriaUpdateSchema(Schema):
    nombre = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    descripcion = fields.String(allow_none=True, load_default=None)
    estado = fields.Boolean(load_default=None)


class ProductoSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=180))
    descripcion = fields.String(allow_none=True)
    precio = fields.Decimal(required=True, places=2, as_string=False, validate=validate.Range(min=0.01))
    stock = fields.Integer(required=True, validate=validate.Range(min=0))
    estado = fields.Boolean(load_default=True)
    categoria_id = fields.Integer(required=True, validate=validate.Range(min=1))
    fecha_creacion = fields.DateTime(dump_only=True)


class ProductoUpdateSchema(Schema):
    nombre = fields.String(load_default=None, validate=validate.Length(min=1, max=180))
    descripcion = fields.String(allow_none=True, load_default=None)
    precio = fields.Decimal(load_default=None, places=2, as_string=False, validate=validate.Range(min=0.01))
    stock = fields.Integer(load_default=None, validate=validate.Range(min=0))
    estado = fields.Boolean(load_default=None)
    categoria_id = fields.Integer(load_default=None, validate=validate.Range(min=1))


class ProductoQuerySchema(Schema):
    categoria_id = fields.Integer(load_default=None)
    nombre = fields.String(load_default=None)
    estado = fields.Boolean(load_default=None)


class UsuarioRegisterSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    rol = fields.String(load_default="CONSULTA")


class UsuarioLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    rol = fields.String(dump_only=True)
    activo = fields.Boolean(dump_only=True)
    fecha_creacion = fields.DateTime(dump_only=True)


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not any(char.isupper() for char in password):
        raise ValidationError("La contraseña debe incluir al menos una letra mayúscula.")
    if not any(char.isdigit() for char in password):
        raise ValidationError("La contraseña debe incluir al menos un número.")
