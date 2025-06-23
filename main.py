from wsgiref.simple_server import make_server
from spyne.server.wsgi import WsgiApplication
from spyne import Application
from app.service import ServicioSOAP
from spyne.protocol.soap import Soap11

application = Application(
    [ServicioSOAP],
    tns='soap.servicio.productos',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    print("Servicio SOAP corriendo en http://localhost:8000")
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
