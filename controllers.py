from decimal import Decimal

from flask import abort
from flask_jwt_extended import create_access_token

from extensions import db
from models import Categoria, Producto, Role, Usuario


def serialize_categoria(categoria):
    return {
        "id": categoria.id,
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion,
        "estado": categoria.estado,
        "fecha_creacion": categoria.fecha_creacion.isoformat() if categoria.fecha_creacion else None,
    }


def serialize_producto(producto):
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": float(producto.precio),
        "stock": producto.stock,
        "estado": producto.estado,
        "categoria_id": producto.categoria_id,
        "fecha_creacion": producto.fecha_creacion.isoformat() if producto.fecha_creacion else None,
    }


def serialize_usuario(usuario):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
        "activo": usuario.activo,
        "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None,
    }


def listar_categorias(query_params=None):
    filters = query_params or {}
    query = Categoria.query
    nombre = (filters.get("nombre") or "").strip()
    if nombre:
        query = query.filter(Categoria.nombre.ilike(f"%{nombre}%"))
    estado = filters.get("estado")
    if estado is not None:
        query = query.filter(Categoria.estado == bool(estado))
    return [serialize_categoria(c) for c in query.order_by(Categoria.id).all()]


def obtener_categoria_por_id(categoria_id):
    categoria = Categoria.query.get(categoria_id)
    if categoria is None:
        abort(404, description="Categoría no encontrada.")
    return serialize_categoria(categoria)


def crear_categoria(data):
    nombre = (data.get("nombre") or "").strip()
    descripcion = data.get("descripcion")
    if not nombre:
        abort(400, description="El nombre de la categoría es obligatorio.")
    if Categoria.query.filter_by(nombre=nombre).first():
        abort(409, description="Ya existe una categoría con ese nombre.")

    categoria = Categoria(
        nombre=nombre,
        descripcion=descripcion,
        estado=bool(data.get("estado", True)),
    )
    db.session.add(categoria)
    db.session.commit()
    return serialize_categoria(categoria)


def actualizar_categoria(categoria_id, data):
    categoria = Categoria.query.get(categoria_id)
    if categoria is None:
        abort(404, description="Categoría no encontrada.")

    nombre = (data.get("nombre") or categoria.nombre).strip()
    if not nombre:
        abort(400, description="El nombre de la categoría es obligatorio.")
    if (
        Categoria.query.filter(Categoria.nombre.ilike(nombre), Categoria.id != categoria_id).first()
        is not None
    ):
        abort(409, description="Ya existe otra categoría con ese nombre.")

    categoria.nombre = nombre
    categoria.descripcion = data.get("descripcion", categoria.descripcion)
    categoria.estado = data.get("estado", categoria.estado)
    db.session.commit()
    return serialize_categoria(categoria)


def eliminar_categoria(categoria_id):
    categoria = Categoria.query.get(categoria_id)
    if categoria is None:
        abort(404, description="Categoría no encontrada.")
    if Producto.query.filter_by(categoria_id=categoria_id).first():
        abort(400, description="No se puede eliminar una categoría que tiene productos asociados.")
    db.session.delete(categoria)
    db.session.commit()
    return {"message": "Categoría eliminada correctamente."}


def listar_productos(query_params=None):
    filters = query_params or {}
    query = Producto.query
    categoria_id = filters.get("categoria_id")
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == int(categoria_id))
    nombre = (filters.get("nombre") or "").strip()
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    estado = filters.get("estado")
    if estado is not None:
        query = query.filter(Producto.estado == bool(estado))
    return [serialize_producto(p) for p in query.order_by(Producto.id).all()]


def obtener_producto_por_id(producto_id):
    producto = Producto.query.get(producto_id)
    if producto is None:
        abort(404, description="Producto no encontrado.")
    return serialize_producto(producto)


def crear_producto(data):
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        abort(400, description="El nombre del producto es obligatorio.")
    categoria = Categoria.query.get(data.get("categoria_id"))
    if categoria is None:
        abort(400, description="La categoría ingresada no existe.")
    precio = data.get("precio")
    stock = data.get("stock")
    if precio is None or Decimal(str(precio)) <= 0:
        abort(400, description="El precio debe ser mayor que cero.")
    if stock is None or int(stock) < 0:
        abort(400, description="El stock debe ser un entero mayor o igual a cero.")

    producto = Producto(
        nombre=nombre,
        descripcion=data.get("descripcion"),
        precio=Decimal(str(precio)),
        stock=int(stock),
        estado=bool(data.get("estado", True)),
        categoria_id=int(data["categoria_id"]),
    )
    db.session.add(producto)
    db.session.commit()
    return serialize_producto(producto)


def actualizar_producto(producto_id, data):
    producto = Producto.query.get(producto_id)
    if producto is None:
        abort(404, description="Producto no encontrado.")
    if data.get("categoria_id") is not None:
        categoria = Categoria.query.get(data["categoria_id"])
        if categoria is None:
            abort(400, description="La categoría ingresada no existe.")
        producto.categoria_id = int(data["categoria_id"])

    nombre = data.get("nombre")
    if nombre is not None:
        nombre = nombre.strip()
        if not nombre:
            abort(400, description="El nombre del producto es obligatorio.")
        producto.nombre = nombre
    descripcion = data.get("descripcion")
    if descripcion is not None:
        producto.descripcion = descripcion
    if data.get("precio") is not None:
        precio = Decimal(str(data["precio"]))
        if precio <= 0:
            abort(400, description="El precio debe ser mayor que cero.")
        producto.precio = precio
    if data.get("stock") is not None:
        stock = int(data["stock"])
        if stock < 0:
            abort(400, description="El stock debe ser un entero mayor o igual a cero.")
        producto.stock = stock
    if data.get("estado") is not None:
        producto.estado = bool(data["estado"])

    db.session.commit()
    return serialize_producto(producto)


def eliminar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto is None:
        abort(404, description="Producto no encontrado.")
    db.session.delete(producto)
    db.session.commit()
    return {"message": "Producto eliminado correctamente."}


def registrar_usuario(data):
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    rol = (data.get("rol") or Role.CONSULTA.value).upper()
    if not nombre:
        abort(400, description="El nombre es obligatorio.")
    if not email:
        abort(400, description="El correo es obligatorio.")
    if len(password or "") < 8:
        abort(400, description="La contraseña debe tener al menos 8 caracteres.")
    if not any(char.isupper() for char in password or ""):
        abort(400, description="La contraseña debe incluir al menos una letra mayúscula.")
    if not any(char.isdigit() for char in password or ""):
        abort(400, description="La contraseña debe incluir al menos un número.")
    if Usuario.query.filter_by(email=email).first():
        abort(409, description="El correo electrónico ya está registrado.")
    if rol == Role.ADMIN.value:
        abort(400, description="No está permitido crear un usuario con el rol ADMIN desde el registro público.")
    if rol not in {Role.CONSULTA.value, Role.EDITOR.value}:
        abort(400, description="El rol no es válido. Use CONSULTA o EDITOR.")

    usuario = Usuario(nombre=nombre, email=email, rol=rol, activo=True)
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()
    return serialize_usuario(usuario)


def autenticar_usuario(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(password):
        abort(401, description="Credenciales inválidas.")
    if not usuario.activo:
        abort(401, description="Usuario inactivo.")
    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"rol": usuario.rol, "user_id": usuario.id},
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": serialize_usuario(usuario),
    }
