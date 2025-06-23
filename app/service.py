from spyne import ServiceBase, rpc, Unicode, Integer, Float, Iterable, Dict
from app.models import Usuario, Producto, Pedido, PedidoDetalle
from app.database import Session

class ServicioSOAP(ServiceBase):

    # Método para crear un usuario
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def crear_usuario(ctx, nombre, correo, tipo):
        session = Session()
        if tipo not in ('admin', 'cliente'):
            return "Tipo de usuario inválido"
        user = Usuario(nombre=nombre, correo=correo, tipo=tipo)
        session.add(user)
        session.commit()
        return f"Usuario {nombre} creado"

    # Método para crear un producto
    @rpc(Unicode, Unicode, Float, Integer, Unicode, _returns=Unicode)
    def crear_producto(ctx, nombre, descripcion, precio, stock, categoria):
        session = Session()
        producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock, categoria=categoria)
        session.add(producto)
        session.commit()
        return f"Producto {nombre} creado"

    # Método para listar productos
    @rpc(_returns=Iterable(Unicode))
    def listar_productos(ctx):
        session = Session()
        productos = session.query(Producto).all()
        return [f"{p.id} - {p.nombre} ({p.categoria}): {p.precio} USD. Stock: {p.stock}" for p in productos]

    # Método para crear un pedido con múltiples productos
    @rpc(Integer, Iterable(Dict(Integer, Integer)), _returns=Unicode)
    def crear_pedido(ctx, usuario_id, productos):
        session = Session()
        usuario = session.get(Usuario, usuario_id)
        if not usuario or usuario.tipo != 'cliente':
            return "Usuario inválido o no autorizado"
        
        total = 0
        pedido = Pedido(usuario_id=usuario_id, confirmado=False)
        
        for producto_data in productos:
            producto_id = producto_data['producto_id']
            cantidad = producto_data['cantidad']
            
            producto = session.get(Producto, producto_id)
            if not producto or producto.stock < cantidad:
                return f"Producto {producto_id} no disponible o stock insuficiente"
            
            total += producto.precio * cantidad
            
            detalle = PedidoDetalle(
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            pedido.detalles.append(detalle)
            producto.stock -= cantidad
        

        pedido.total = total
        session.add(pedido)
        session.commit()
        
        return f"Pedido {pedido.id} creado con {len(productos)} productos"

    # Método para cancelar un pedido
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

    # Método para confirmar un pedido
    @rpc(Integer, _returns=Unicode)
    def confirmar_pedido(ctx, pedido_id):
        session = Session()
        pedido = session.get(Pedido, pedido_id)
        if not pedido:
            return "Pedido no encontrado"
        pedido.confirmado = True
        session.commit()
        return "Pedido confirmado"
