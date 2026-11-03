from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

from controllers import (
    actualizar_categoria,
    actualizar_producto,
    autenticar_usuario,
    crear_categoria,
    crear_producto,
    eliminar_categoria,
    eliminar_producto,
    listar_categorias,
    listar_productos,
    obtener_categoria_por_id,
    obtener_producto_por_id,
    registrar_usuario,
)
from schemas import (
    CategoriaQuerySchema,
    CategoriaSchema,
    CategoriaUpdateSchema,
    ProductoQuerySchema,
    ProductoSchema,
    ProductoUpdateSchema,
    UsuarioLoginSchema,
    UsuarioRegisterSchema,
)


blp = Blueprint("api", __name__, url_prefix="/api", description="API de gestión de productos")


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            current_role = claims.get("rol")
            if current_role not in allowed_roles:
                abort(403, description="No tiene permisos para realizar esta operación.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@blp.post("/auth/register")
@blp.arguments(UsuarioRegisterSchema)
def register(data):
    user = registrar_usuario(data)
    return jsonify({"message": "Usuario registrado correctamente.", "usuario": user}), 201


@blp.post("/auth/login")
@blp.arguments(UsuarioLoginSchema)
def login(data):
    token_data = autenticar_usuario(data)
    return jsonify(token_data), 200


@blp.get("/productos")
@blp.arguments(ProductoQuerySchema, location="query")
@role_required("CONSULTA", "EDITOR", "ADMIN")
def get_productos(query_data):
    return jsonify(listar_productos(query_data)), 200


@blp.post("/productos")
@blp.arguments(ProductoSchema)
@role_required("EDITOR", "ADMIN")
def create_producto(data):
    producto = crear_producto(data)
    return jsonify({"message": "Producto registrado correctamente.", "producto": producto}), 201


@blp.get("/productos/<int:producto_id>")
@role_required("CONSULTA", "EDITOR", "ADMIN")
def get_producto(producto_id):
    return jsonify(obtener_producto_por_id(producto_id)), 200


@blp.put("/productos/<int:producto_id>")
@blp.arguments(ProductoUpdateSchema)
@role_required("EDITOR", "ADMIN")
def update_producto(producto_id, data):
    producto = actualizar_producto(producto_id, data)
    return jsonify({"message": "Producto actualizado correctamente.", "producto": producto}), 200


@blp.delete("/productos/<int:producto_id>")
@role_required("ADMIN")
def delete_producto(producto_id):
    response = eliminar_producto(producto_id)
    return jsonify(response), 200


@blp.get("/categorias")
@blp.arguments(CategoriaQuerySchema, location="query")
@role_required("CONSULTA", "EDITOR", "ADMIN")
def get_categorias(query_data):
    return jsonify(listar_categorias(query_data)), 200


@blp.post("/categorias")
@blp.arguments(CategoriaSchema)
@role_required("EDITOR", "ADMIN")
def create_categoria_route(data):
    categoria = crear_categoria(data)
    return jsonify({"message": "Categoría registrada correctamente.", "categoria": categoria}), 201


@blp.get("/categorias/<int:categoria_id>")
@role_required("CONSULTA", "EDITOR", "ADMIN")
def get_categoria(categoria_id):
    return jsonify(obtener_categoria_por_id(categoria_id)), 200


@blp.put("/categorias/<int:categoria_id>")
@blp.arguments(CategoriaUpdateSchema)
@role_required("EDITOR", "ADMIN")
def update_categoria_route(categoria_id, data):
    categoria = actualizar_categoria(categoria_id, data)
    return jsonify({"message": "Categoría actualizada correctamente.", "categoria": categoria}), 200


@blp.delete("/categorias/<int:categoria_id>")
@role_required("ADMIN")
def delete_categoria_route(categoria_id):
    response = eliminar_categoria(categoria_id)
    return jsonify(response), 200
