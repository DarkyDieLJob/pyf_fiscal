import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from threading import Timer
from Traductores.TraductoresHandler import TraductoresHandler, TraductorException
import socket
import json
import logging
import time
import ssl
import ConfigFiscal
import FiscalDiscover

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 2
INTERVALO_IMPRESORA_WARNING = 30.0

#global para el listado de clientes conectados
clients = []
# leer los parametros de configuracion de la impresora fiscal 
# en config.ini 

traductor = TraductoresHandler()

class WebSocketException(Exception):
	pass

 
class WSHandler(tornado.websocket.WebSocketHandler):

	def open(self):
		global clients
		clients.append(self)
		print 'new connection'
	
	def on_message(self, message):
		global traductor
		print("----- - -- - - - ---")
		print message
		try:
			jsonMes = json.loads(message, strict=False)
			response = traductor.json_to_comando( jsonMes )
			self.write_message( response )
		except TypeError:
			response = {"err": "Error parseando el JSON"}
		except TraductorException, e:
			response = {"err": "Traductor Comandos: %s"%str(e)}
		except Exception, e:
			response = {"err": repr(e)+"- "+str(e)}
			import sys, traceback
			traceback.print_exc(file=sys.stdout)

		
 
	def on_close(self):
		global clients
		clients.remove(self)
		print 'connection closed'
 
	def check_origin(self, origin):
		return True




class FiscalServer:
	application = None
	http_server = None

	# thread timer para hacer broadcast cuando hay mensaje de la impresora
	timerPrinterWarnings = None


	def __init__(self):
		print("Iniciando Fiscal Server")
		

		self.application = tornado.web.Application([
			(r'/ws', WSHandler),
		])


		self.configFisc = ConfigFiscal.ConfigFiscal()

		# send discover data to your server if the is no URL configured, so nothing will be sent
		discoverUrl = self.configFisc.config.has_option('SERVIDOR', "discover_url")
		if discoverUrl:
			discoverUrl = self.configFisc.config.get('SERVIDOR', "discover_url")
			fbdiscover = FiscalDiscover.send(discoverUrl);


		
		hasCrt = self.configFisc.config.has_option('SERVIDOR', "ssl_crt_path")
		hasKey = self.configFisc.config.has_option('SERVIDOR', "ssl_key_path")


		if ( hasCrt and hasKey):
			ssl_crt_path = self.configFisc.config.get('SERVIDOR', "ssl_crt_path")
			ssl_key_path = self.configFisc.config.get('SERVIDOR', "ssl_key_path")

			context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
			context.load_cert_chain(certfile=ssl_crt_path, keyfile=ssl_key_path)

			self.http_server = tornado.httpserver.HTTPServer(self.application, ssl_options=context)
			print("iniciando en modo HTTPS")
		else:
			self.http_server = tornado.httpserver.HTTPServer(self.application)
			print("iniciando en modo HTTP")



	def shutdown(self):
		logging.info('Stopping http server')

		logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
		io_loop = tornado.ioloop.IOLoop.instance()

		deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

		if self.timerPrinterWarnings:
			self.timerPrinterWarnings.cancel()

		def stop_loop():
			now = time.time()
			if now < deadline and (io_loop._callbacks or io_loop._timeouts):
				io_loop.add_timeout(now + 1, stop_loop)
			else:
				io_loop.stop()
				logging.info('Shutdown')

		stop_loop()



	def start( self ):

		self.print_printers_resume()
		puerto = self.get_config_port()
		self.http_server.listen( puerto )
		myIP = socket.gethostbyname(socket.gethostname())

		# inicializar intervalo para verificar que la impresora tenga papel
		timerPrinterWarnings = Timer(INTERVALO_IMPRESORA_WARNING, self.send_printer_warnings).start()

		print '*** Websocket Server Started at %s port %s***' % (myIP, puerto)
		tornado.ioloop.IOLoop.instance().start()

		print "Bye!"
		logging.info("Exit...")
			

		

	def get_config_port(self):
		"lee el puerto configurado por donde escuchara el servidor de websockets"
		
		puerto = self.configFisc.config.get('SERVIDOR', "puerto")
		return puerto




	def get_list_of_configured_printers( self ):
		"Listar las impresoras configuradas"
		# el primer indice del array corresponde a info del SERVER,
		# por eso lo omito. El resto son todas impresoras configuradas
		printers = self.configFisc.sections()[1:]
		return printers



	def send_printer_warnings( self ):
	    "enviar un broadcast a los clientes con los warnings de impresora, si existen"
	    global clients
	    global traductor

	    warns = traductor.getWarnings()
	    if warns:
			print warns
	    	# envia broadcast a todos los clientes
			msg = json.dumps( {"msg": warns } )
			for cli in clients:
				cli.write_message( msg )
	    #volver a comprobar segun intervalo seleccionado  
	    self.timerPrinterWarnings = Timer(INTERVALO_IMPRESORA_WARNING, self.send_printer_warnings)
	    self.timerPrinterWarnings.start()




	def print_printers_resume(self):
		printers = self.get_list_of_configured_printers()

		if len(printers) > 1:
			print "Hay %s impresoras disponibles" % len(printers)
		else:
			print "Impresora disponible:"
		for printer in printers:
			print "  - %s" % printer
			modelo = None
			marca = self.configFisc.config.get(printer, "marca")
			driver = self.configFisc.config.get(printer, "driver")
			if self.configFisc.config.has_option(printer, "modelo"):
				modelo = self.configFisc.config.get(printer, "modelo")
			print "      marca: %s, driver: %s" % (marca, driver)
		print "\n"
