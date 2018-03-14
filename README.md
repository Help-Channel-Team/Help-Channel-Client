# Help-Channel-Client

Para el uso de este cliente se deben tener credenciales de acceso de usuario registrado ya en el servidor.
La funcionalidad de este cliente es la siguiente:
- Registrarse en el sistema con los datos de usuario.
- Lanzar una solicitud de asistencia.
- Aceptar o rechazar la respuesta de asistencia del técnico.
- Finalizar la realización de la asistencia en cualquier momento.

El cliente que realiza la tarea anterior está realizado en Python, su GUI usando las libreras Qt.
La comunicación con el servidor se realiza mediante servicios web de tipo REST para las tareas de gestión.
La comunicación entre el servidor X11VNC y el servidor se realiza tunelizando la comunicación a través de WebSockets. TCP sobre HTTPS.

Es posible usar cualquier servidor VNC que soporte conexiones en modo repetidor, no tiene que ser forzósamente X11VNC.

Los parámetros a configurar son los siguientes:


El script crea un socket local de escucha al que se conecta el X11VNC en modo repetidor y dicha comunicación es enviada al Websocket del servidor que comunica con la parte servidor del repetidor.

websocket-client 0.47.0 

    https://pypi.python.org/pypi/websocket-client/ 
    
    
pycos 4.6.5

https://pypi.python.org/pypi/pycos


La interfaz gráfica usada es Tkinter, apt-get install python-tk (debian)

    
x11vnc: a VNC server for real X displays 

    http://www.karlrunge.com/x11vnc/

En la carpeta Node Test Client hay un script de node cuyo funcionamiento es el mismo sin GUI para Node

Licensed under the EUPL V.1.1

The license text is available at http://www.osor.eu/eupl
