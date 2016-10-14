var https = require('https');
var HttpsProxyAgent = require('https-proxy-agent');
//var shell = global.shell = require('./lib/shell');
var tunnel = require('./lib/tunnel');

// Dirección servidor Helpchannel
var remoteHost = 'helpchannel.ingenieriacreativa.es:443/wsServer';
// Puerto local desde el que conectar el servidor VNC
var localPort = "6000";
// Puerto remoto del repetidor de VNC
var repeater = "127.0.0.1:6000";
// Código de acceso para la sesión de VNC
var codigo = "1234";
var credentials, tunnels = [];

// Proxy
var proxy = 'http://177.99.190.140:3128';
var proxymode = false;

if(process.argv[2] == "proxy")
{
	proxymode = true;
	shell.prompt('Usuario proxy: ', function(user) {
    	 	shell.prompt('Password proxy: ', function(password) {
     	 		credentials = user + ':' + password;
			ready();
		});
	});

}
else
{
	credentials = ':';
	ready();
}

var agent = new HttpsProxyAgent(proxy);

////////////////////////////////////////////////////////////////////////////

function ready()
{
	authenticate(function() {
  		//shell.prompt();
	});
}

function createTunnelHTTPS()
{

    tunnel.createTunnel(remoteHost, credentials,localPort,repeater,proxymode,agent, function(err, server) {
      if (err) {
        console.log(String(err));
      } else {
        var id = tunnels.push(server);
        console.log('Tunnel created with id: ' + id);
        
        connectX11VNC();
      }
      //shell.prompt();
});

}


function connectX11VNC()
{

// Ejecuta X11VNC, si la ruta no está definida en el PATH hay poner la absoluta en el exec
var sys = require('sys')
var exec = require('child_process').exec;
function puts(error, stdout, stderr) { sys.puts(stdout) }
	exec("x11vnc -connect repeater=ID:"+codigo+"+127.0.0.1:"+localPort, puts);
}


function authenticate(callback) {
 
      console.log('Authenticating ...');
 
      createTunnelHTTPS();
      console.log('Tunel Creado.');
	
      callback();
	

/*     checkAuth(function(success) {
        if (success) {
          shell.echo('Authenticated Successfully.');

          //Si autenticado correctamente, crea el tunnel 
	  createTunnelHTTPS();
          callback();
        } else {
          shell.echo('Error: invalid credentials.');
          authenticate(callback);
        }
      });*/
}


// Comprueba conectividad y autentica con la comunicación, como credenciales hay que pasar el token
function checkAuth(callback) {

console.log("En CheckAuth");

var encoded = new Buffer(String(credentials)).toString('base64');

  if(proxymode)
  {		
	  var opts = {
	    path: '/auth',
	    headers: {'Authorization': 'Basic ' + encoded},
	    rejectUnauthorized: false,  // Certificado Self Signed 
	    agent : agent,
	    port: 443,	
	    host: remoteHost,	
	  };
  }
  else
  {
          var opts = {
	    path: '/auth',
	    headers: {'Authorization': 'Basic ' + encoded},
	    rejectUnauthorized: false,  // Certificado Self Signed 
	    port: 443,	
	    host: remoteHost,	
	  };

  }

		  
  var req = https.request(opts, function(res) {
    callback(res.statusCode == 204);
  });
  req.on('error', function(err) {
    shell.echo('Unable to authenticate.');
    shell.echo(String(err));
    shell.exit();
  });
  req.end();
}
