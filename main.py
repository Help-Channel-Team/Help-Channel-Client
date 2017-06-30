#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import json
import subprocess
import threading
from tkMessageBox import showerror
import urllib2
import ConfigParser
import gettext
import platform
import os
import os.path
import urllib

import socket

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

config = ConfigParser.ConfigParser()

config.read(BASE_DIR + "/config.ini")


# Function to get dictionary with the values of one section of the configuration file
def config_section_map(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1


def build_rest_url(relative_path, params={}):
    """
    Builds a valid REST URI

    :param relative_path: The relative path to the REST service
    :type params: A dictionary of parameters to be set in the URI. Default empty
    """
    url_params = {'access-token': user_access_token, 'connection_code': connection_code}
    url_params.update(params)

    complete_params = urllib.urlencode(url_params)

    return rest_base + relative_path + '?' + complete_params


def do_rest_request(url, params={}):
    """
    Performs a REST request

    :param url: the relative url
    """
 
    proxy_host = config_section_map("ServerConfig")['proxy_host']
    proxy_port = config_section_map("ServerConfig")['proxy_port']
    proxy_username = config_section_map("ServerConfig")['proxy_username']
    proxy_password = config_section_map("ServerConfig")['proxy_password']
    #proxy_auth_mode = config_section_map("ServerConfig")['proxy_auth_mode']

    proxy_connection_string = 'http://' + proxy_username + ":" + proxy_password + "@" + proxy_host + ":" + proxy_port
	
    if proxy_host:
	print "Proxy mode"
    	proxy = urllib2.ProxyHandler()
    	auth = urllib2.HTTPBasicAuthHandler()
   	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
    	urllib2.install_opener(opener)
  
    urllib2.urlopen(build_rest_url(url, params))

    return


# Global variables start

# Global variable to check if we have already found a technician or we need to keep searching
alive = False

# REST connection parameters
user_access_token = ""
connection_code = ""

# REST base url
rest_base = config_section_map("ServerConfig")['rest_base_url']

# Global variables end


# Set default locale
language = config_section_map("i18nConfig")['language'] or 'es'
lang = gettext.translation(language, localedir=BASE_DIR + '/locale', languages=[language])
lang.install(unicode=1)


class HelpChannel(Tk):
    """
    Main application class. It's responsible for showing and hide¡ing the frames.
    """

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        # The container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.wm_title("Help Channel")

        self.frames = {}
        for F in (LoginFrame,):
            frame = F(self.container, self)
            self.frames[F] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            self.frame = frame
        self.show_frame(LoginFrame)

    def show_frame(self, c):
        """
        Function that call the first frame of the application. In this case, the Login screen

        :param c: The first frame of the application.
        :type c: LoginFrame
        """
        frame = self.frames[c]
        frame.tkraise()
        self.frame = frame

    def show_wait_tec_frame(self):
        """
        Shows the 'Waiting technicians' screen
        :return:None
        """
        frame = WaitTecFrame(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        self.frame = frame

    def show_established_connection(self, subproc):
        """
        Shows the 'Established connection' screen
        :param subproc: Launched process by the application for handle the applicant's remote desktop
        :type subproc: Subprocess
        """
        global alive
        alive = False

        frame = EstablishedConnection(self.container, self, subproc)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        self.frame = frame

    def show_finished_connection(self):
        frame = FinishedConnection(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        self.frame = frame


class LoginFrame(Frame):
    """
    Class that represent the 'Login' screen
    """

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        name = StringVar()
        password = StringVar()

        padtop = 50
        length_entry = 50

        Label(self, text=_('Username:')).grid(row=0, column=0, pady=(padtop, 0), sticky=S)
        Entry(self, textvariable=name, width=length_entry).grid(row=0, column=1, pady=(padtop, 0))

        Label(self, text=_('Password:')).grid(row=1, column=0, pady=(0, padtop))
        Entry(self, textvariable=password, show="*", width=length_entry).grid(row=1, column=1, pady=(0, padtop))

        Button(self, text=_("Login"), command=lambda: self.do_login(name.get(), password.get(), controller)).grid(row=2,
                                                                                                                  columnspan=2)

    def do_login(self, username, password, controller):
        """
        Function to perform user login into the application.
        :param username: User name
        :type username: str
        :param password: Password
        :type password: str
        :param controller: Frame's handler
        :type controller: HelpChannel
        """

        req_url = rest_base + '/user/login?username=%s&password=%s&machine_name=%s' % (
            username, password, platform.node(),)

        json_return = json.load(urllib2.urlopen(req_url))
        return_status = json_return['status']

        if return_status == 'error':
            showerror(_('Login error'), _('Wrong username or password'))
        else:

            global user_access_token
            user_access_token = json_return['access_token']

            global connection_code
            connection_code = json_return['connection_code']

            controller.show_wait_tec_frame()


class WaitTecFrame(Frame):
    """
    Class that represent the 'Waiting technicians' screen
    """

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        global alive
        alive = True

        label = Label(self, text=_('Waiting for assistance...'))
        label.pack()

        bottom = Frame(self, bg="white")
        bottom.pack(side=BOTTOM, fill=X)

        self.work(bottom, label)

        accept_button = Button(self, text=_('Accept'), command=lambda: self.open_connection(controller))
        accept_button.pack(in_=bottom, side=LEFT, fill=BOTH, expand=True)

        refuse_button = Button(self, text=_('Reject'), command=lambda: self.search_again(bottom, label))
        refuse_button.pack(in_=bottom, side=LEFT, fill=BOTH, expand=True)

    def open_connection(self, controller):
        """
        Function to open connection with de applicant
        :param controller: Frame's handler
        :type controller: HelpChannel
        """
        repeaterWS2 = config_section_map("ServerConfig")['repeater_ws']
        localTunnelPort = config_section_map("ServerConfig")['local_tunnel_port']
        repeater = config_section_map("ServerConfig")['repeater']
        port = config_section_map("ServerConfig")['port']
        system_path = config_section_map("x11vncConfig")['system_path']

        #connect_parameter = "python ./hctunnel.py %s %s" % (localTunnelPort, repeaterWS2)
	#commandTunnel = [system_path, connect_parameter]
	#print connect_parameter     
	#tunnelSubProc = subprocess.Popen(commandTunnel, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)	
        #print "Después de lanzar el tunel\n" 

        connect_parameter = "repeater=ID:%s+%s:%s" % (connection_code, repeater, port,)	

        command = [system_path, "-connect", connect_parameter]
        subproc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

        # Rest to accept connection
        do_rest_request('/connection/accept')

        controller.show_established_connection(subproc)

    def search_again(self, button_frame, label):
        """
        Function to find technicians again when user refuses a request.
        :param button_frame: Container of buttons 'Accept' and 'Refuse'
        :type button_frame: tk.Frame
        :param label: Text with the message 'Waiting technicians...'
        :type label: tk.Label
        """

        global alive
        alive = True

        do_rest_request('/connection/reject')

        label.config(text=_('Waiting for assistance...'))

        button_frame.pack_forget()

    def work(self, buttonsFrame, label):
        """
        Function than search availables technicians every 'polling_interval'(view config.ini) seconds.
        :param buttonsFrame: Container of buttons 'Accept' and 'Refuse'
        :type buttonsFrame: tk.Frame
        :param label: Text with the message 'Waiting technicians...'
        :type label: tk.Label
        """

        req_url = build_rest_url('/connection/fetch')

        json_return = json.load(urllib2.urlopen(req_url))

        has_tech = json_return['has_tech']
        tech_name = json_return['tech_name']
        polling_interval = config_section_map("ServerConfig")['polling_interval']

        if has_tech == '0':
            buttonsFrame.pack_forget()
        else:
            global alive
            alive = False
            buttonsFrame.pack(side=BOTTOM, fill=X)
            label.config(text=tech_name + ' ' + _("wants to help you"))

        if alive:
            threading.Timer(float(polling_interval), self.work, (buttonsFrame, label)).start()


class EstablishedConnection(Frame):
    """
    Class that represent the 'Established connection' screen
    """

    def __init__(self, parent, controller, subproc=NONE):
        Frame.__init__(self, parent)

        bottom = Frame(self)
        bottom.pack(side=BOTTOM, fill=X)

        self.check_alive(subproc, controller)

        label = Label(self, text=_('Connection established'), bg="white")

        label.pack(side=LEFT, fill=BOTH, expand=True)

        finish_button = Button(self, text=_('End connection'), command=lambda: self.finish_connection(controller, subproc))
        finish_button.pack(in_=bottom, side=LEFT, fill=BOTH, expand=True)

    def finish_connection(self, controller, subproc):
        """
        Function to close the connection
        :param controller: Handler's frame
        :type controller: HelpChannel
        """
        subproc.kill()
        do_rest_request('/connection/finish', {'finisher': 'user'})
        app.destroy()

    def check_alive(self, subproc, controller):
        """
        Check if the connection is still alive. This checking performs every X seconds.
        The amount of seconds are provided in config.ini
        :param subproc: Launched process by the application for handles the applicant's remote desktop
        :type subproc: subprocess
        """
        seconds = float(config_section_map("x11vncConfig")['process_polling_interval'])

        if subproc.poll() == 0:
            do_rest_request('/connection/finish', {'finisher': 'tech'})
            controller.show_finished_connection()

        threading.Timer(seconds, self.check_alive, (subproc, controller,)).start()


class FinishedConnection(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text=_('Connection finished'))
        label.pack()


class CustomAskOkCancel:
    def __init__(self, parent, window_title, ok_message, cancel_message, label_message):
        self.response = False

        top = self.top = Toplevel(parent)
        Label(top, text=label_message).pack()
        top.wm_title(_(window_title))

        bottom = Frame(top)
        bottom.pack(side=BOTTOM, fill=X, pady=(30, 0))

        button_ok = Button(top, text=ok_message, command=self.ok)
        button_ok.pack(in_=bottom, side=LEFT, fill=BOTH, expand=True, pady=(0, 0))

        button_cancel = Button(top, text=cancel_message, command=self.top.destroy)
        button_cancel.pack(in_=bottom, side=LEFT, fill=BOTH, expand=True, pady=(0, 0))

    def ok(self):
        self.response = True;
        self.top.destroy()


if __name__ == "__main__":
    x11vnc_path = config_section_map("x11vncConfig")['system_path']
    if not os.path.isfile(x11vnc_path):
        #x11vnc not found
       showerror(_('Error'), _('x11vnc not found at %s. Please, check it and try again.') % x11vnc_path)
       sys.exit(0)

    app = HelpChannel()


    def custom_ask_ok_cancel(windows_title, ok_message, cancel_message, label_message):
        dialog = CustomAskOkCancel(app, windows_title, ok_message, cancel_message, label_message)
        app.wait_window(dialog.top)
        return dialog.response


    def on_closing():
        """
        Function to catch the clic event generated by application's close button.
        """

        if not app.frame.__class__.__name__ == "LoginFrame" and  not app.frame.__class__.__name__ == "FinishedConnection":
            if custom_ask_ok_cancel(_('Close connection'), _('Ok'), _('Cancel'),
                                    _('Are you sure you want to close the connection?')):
                do_rest_request('/connection/close')
                app.destroy()
        else:
            app.destroy()


    app.protocol('WM_DELETE_WINDOW', on_closing)
    app.mainloop()
