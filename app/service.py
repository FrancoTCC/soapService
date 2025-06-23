from spyne import ServiceBase, rpc, Unicode, Integer, Float, Iterable
from app.models import Usuario, Producto, Pedido, PedidoDetalle
from app.database import Session

class ServicioSOAP(ServiceBase):

    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def crear_usuario(ctx, nombre, correo, tipo):
        session = Session()
        if tipo not in ('admin', 'cliente'):
            return "Tipo de usuario inválido"
        user = Usuario(nombre=nombre, correo=correo, tipo=tipo)
        session.add(user)
        session.commit()
        return f"Usuario {nombre} creado"

    @rpc(Unicode, Unicode, Float, Integer, Unicode, _returns=Unicode)
    def crear_producto(ctx, nombre, descripcion, precio, stock, categoria):
        session = Session()
        producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock, categoria=categoria)
        session.add(producto)
        session.commit()
        return f"Producto {nombre} creado"

    @rpc(_returns=Iterable(Unicode))
    def listar_productos(ctx):
        session = Session()
        productos = session.query(Producto).all()
        return [f"{p.id} - {p.nombre} ({p.categoria}): {p.precio} USD. Stock: {p.stock}" for p in productos]

    @rpc(Integer, Iterable(Integer), Iterable(Integer), _returns=Unicode)
    def crear_pedido(ctx, usuario_id, producto_ids, cantidades):
        session = Session()

        # Verificar si el usuario es válido y es un cliente
        usuario = session.get(Usuario, usuario_id)
        if not usuario or usuario.tipo != 'cliente':
            return "Usuario inválido o no autorizado"

        # Verificar que las listas de producto_ids y cantidades tienen la misma longitud
        if len(producto_ids) != len(cantidades):
            return "La cantidad de productos no coincide con la cantidad de cantidades"

        # Crear el pedido
        pedido = Pedido(usuario_id=usuario_id, total=0)

        total_pedido = 0
        for producto_id, cantidad in zip(producto_ids, cantidades):
            producto = session.get(Producto, producto_id)

            if not producto:
                return f"Producto con ID {producto_id} no encontrado"
            if producto.stock < cantidad:
                return f"Stock insuficiente para el producto {producto.nombre}"

            # Crear el detalle del pedido
            detalle = PedidoDetalle(
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            pedido.detalles.append(detalle)

            # Actualizar el stock del producto
            producto.stock -= cantidad

            # Sumar al total del pedido
            total_pedido += producto.precio * cantidad

        # Establecer el total del pedido
        pedido.total = total_pedido

        # Agregar el pedido a la base de datos
        session.add(pedido)
        session.commit()

        return f"Pedido {pedido.id} creado con {len(producto_ids)} productos"


    @rpc(Integer, _returns=Unicode)
    def cancelar_pedido(ctx, pedido_id):
        session = Session()
        pedido = session.get(Pedido, pedido_id)
        if not pedido:
            return "Pedido no encontrado"
        if pedido.confirmado:
            return "No se puede cancelar un pedido confirmado"

        for detalle in pedido.detalles:
            producto = session.get(Producto, detalle.producto_id)
            producto.stock += detalle.cantidad

        session.delete(pedido)
        session.commit()
        return "Pedido cancelado correctamente"

    @rpc(Integer, _returns=Unicode)
    def confirmar_pedido(ctx, pedido_id):
        session = Session()
        pedido = session.get(Pedido, pedido_id)
        if not pedido:
            return "Pedido no encontrado"
        pedido.confirmado = True
        session.commit()
        return "Pedido confirmado"
