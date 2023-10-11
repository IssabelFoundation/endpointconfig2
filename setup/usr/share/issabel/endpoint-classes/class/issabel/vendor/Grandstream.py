# vim: set fileencoding=utf-8 :
# vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
# Codificación: UTF-8
# +----------------------------------------------------------------------+
# | Issabel version 4.0.4                                                |
# | http://www.issabel.org                                               |
# +----------------------------------------------------------------------+
# | Copyright (c) 2006 Palosanto Solutions S. A.                         |
# +----------------------------------------------------------------------+
# | Cdla. Nueva Kennedy Calle E 222 y 9na. Este                          |
# | Telfs. 2283-268, 2294-440, 2284-356                                  |
# | Guayaquil - Ecuador                                                  |
# | http://www.palosanto.com                                             |
# +----------------------------------------------------------------------+
# | The contents of this file are subject to the General Public License  |
# | (GPL) Version 2 (the "License"); you may not use this file except in |
# | compliance with the License. You may obtain a copy of the License at |
# | http://www.opensource.org/licenses/gpl-license.php                   |
# |                                                                      |
# | Software distributed under the License is distributed on an "AS IS"  |
# | basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See  |
# | the License for the specific language governing rights and           |
# | limitations under the License.                                       |
# +----------------------------------------------------------------------+
# | The Initial Developer of the Original Code is PaloSanto Solutions    |
# +----------------------------------------------------------------------+
# $Id: dialerd,v 1.2 2008/09/08 18:29:36 alex Exp $
import logging
import re
import struct
import eventlet
import urllib3
from eventlet.green import socket, urllib, os
from eventlet.green.urllib.parse import urlencode
import errno
import json
from issabel.BaseEndpoint import BaseEndpoint
telnetlib = eventlet.import_patched('telnetlib')
import http.cookiejar
import time
import http.client
paramiko = eventlet.import_patched('paramiko')

class Endpoint(BaseEndpoint):
    def __init__(self, amipool, dbpool, sServerIP, sIP, mac):
        BaseEndpoint.__init__(self, 'Grandstream', amipool, dbpool, sServerIP, sIP, mac)

        # Calculate timezone, 'auto' or GMT offset in minutes +720
        #self._timeZone = BaseEndpoint.getTimezoneOffset() / 60 + 720
        self._timeZone = 'auto'
        self._language = 'es'


    def setExtraParameters(self, param):
        if not BaseEndpoint.setExtraParameters(self, param): return False
        if 'timezone' in param: self._timeZone = param['timezone']
        if 'language' in param: self._language = param['language']
        return True

    def probeModel(self):
        '''Probe specific model of the Grandstream phone
        
        To probe for the specific model, a telnet session is tried first. The 
        login banner exposes the phone model. If the telnet session is refused,
        an attempt is made to invoke the manager URL through HTTP.
        '''
        bTelnetFailed = False
        try:
            telnet = telnetlib.Telnet()
            telnet.open(self._ip)
            telnet.get_socket().settimeout(5)
        except socket.timeout as e:
            logging.error('Endpoint %s@%s failed to telnet - timeout (%s)' %
                (self._vendorname, self._ip, str(e)))
            return
        except socket.error as e:
            logging.info('Endpoint %s@%s failed to telnet - %s. Trying HTTP...' %
                (self._vendorname, self._ip, str(e)))
            bTelnetFailed = True

        
        sModel = None
        # If telnet failed to connect, the model might still be exposed through HTTP
        if bTelnetFailed:
            try:
                # Try detecting GXP2200 or similar
                conn = http.client.HTTPConnection(self._ip)
                conn.request('GET', '/manager?action=product&time=0')
                response = conn.getresponse()
                if response.status == 200:
                    htmlbody = response.read().decode('utf-8')
                    m = re.search(r'Product=(\w+)', htmlbody)
                    if m != None: sModel = m.group(1)
                else:
                    pass

                # Try detecting Elastix LXP200 with updated firmware
                try:
                    conn = http.client.HTTPConnection(self._ip)
                    conn.request('GET', '/cgi-bin/api.values.get?request=phone_model:1395')
                    response = conn.getresponse()
                    if response.status == 200:
                        jsonvars = self._parseBotchedJSONResponse(response)
                        if jsonvars != None and 'body' in jsonvars:    
                            logging.info('3 Endpoint %s@%s connection correct - %s' %
                                          (self._vendorname, self._ip, jsonvars['body']['phone_model']))
                            if '1395' in jsonvars['body'] and jsonvars['body']['1395'] == 'Elastix':
                                self._saveVendor('Elastix')
                            if 'phone_model' in jsonvars['body']:
                                sModel = jsonvars['body']['phone_model']
                                logging.info('4 Endpoint %s@%s connection correct, model - %s' %
                                              (self._vendorname, self._ip, sModel))
                except http.client.HTTPException:
                    # Ignore 404 error
                    pass

            except Exception as e:
                pass
        else:
            try:
                idx, m, text = telnet.expect([r'Password:'], 10)
                telnet.close()
                
                # This is known to detect GXV3140, GXP2120
                m = re.search(r'Grandstream (\S+)\s', text)
                if m != None:
                    sModel = m.group(1)
                
                # If this matches, this is an Elastix phone (rebranded Grandstream)
                m = re.search(r'Elastix (\S+)\s', text)
                if m != None:
                    self._saveVendor('Elastix')
                    sModel = m.group(1)
                
                #if sModel == None:
                #    print text
            except socket.error as e:
                logging.error('5 Endpoint %s@%s connection failure - %s' %
                    (self._vendorname, self._ip, str(e)))
                return False
        
        if sModel != None: self._saveModel(sModel)

    def updateLocalConfig(self):
        '''Configuration for Grandstream endpoints (local):
        
        The file cfgXXXXXXXXXXXX contains the SIP configuration. Here 
        XXXXXXXXXXXX is replaced by the lowercase MAC address of the phone. 
        Grandstream is special in that the file is not text but a binary 
        encoding, which is generated by _encodeGrandstreamConfig().
        
        To reboot the phone, it is necessary to issue the AMI command:
        For GXP280,GXV3140,GXV3175: "sip notify cisco-check-cfg {$EXTENSION}"
        '''
        # Check that there is at least one account to configure
        if len(self._accounts) <= 0:
            logging.error('Endpoint %s@%s has no accounts to configure' %
                (self._vendorname, self._ip))
            return False

        # Need to calculate lowercase version of MAC address without colons
        sConfigFile = 'cfg' + (self._mac.replace(':', '').lower())
        sConfigPath = self._tftpdir + '/' + sConfigFile
        
        vars = self._hashTableGrandstreamConfig()

        try:
            self._writeContent(sConfigPath, self._encodeGrandstreamConfig(vars))
        except IOError as e:
            logging.error('Endpoint %s@%s failed to write configuration file - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        
        # Attempt to send configuration via HTTP to phone. This is required for
        # static provisioning
        if not self._enableStaticProvisioning(vars):
            return False
        
        # Check if there is at least one registered extension. This is required
        # for sip notify to work
        if self._hasRegisteredExtension():
            # GXV3175 wants check-sync, not sys-control
            #self._amireboot('grandstream-check-cfg')
            self._amireboot('cisco-check-cfg')
        elif self._telnet_password != None and not self._rebootbytelnet():
            return False            
        elif self._ssh_password != None and not self._rebootbyssh():
            return False
        elif self._http_password != None and not self._rebootbyhttp():
            return False
        
        self._unregister()
        self._setConfigured()
        return True

    def _enableStaticProvisioning(self, vars):

        def make_request(url, method='GET'):
            try:
                conn = http.client.HTTPConnection(self._ip)
                conn.request(method, url)
                response = conn.getresponse()
                body = response.read().decode('utf-8')
                headers = dict(response.getheaders())
                return body, headers
            except http.client.HTTPException as e:
                logging.error('HTTPException: %s' % str(e))
                return None, None
            except Exception as e:
                logging.error('An error occurred: %s' % str(e))
                return None, None

        # Detect what kind of HTTP interface is required
        staticProvImpls = [
            # Interface for newer GXP140x firmware - JSON based
            ('GXP140x JSON', '/cgi-bin/api.values.post', self._enableStaticProvisioning_GXP140x),
    
            # Interface for old BT200 firmware or similar
            ('BT200', '/update.htm', self._enableStaticProvisioning_BT200),
    
            # Interface for GXVxxxx firmware or similar
            ('GXVxxxx', '/manager', self._enableStaticProvisioning_GXV),
    
            # Interface for GXP1450 firmware or similar
            ('GXP1450', '/cgi-bin/update', self._enableStaticProvisioning_GXP1450),
        ]

        for impl in staticProvImpls:
            url = 'http://' + self._ip + impl[1]
            body, headers = make_request(url)
    
            if headers and 'Content-Type' in headers:
                if headers['Content-Type'] == 'text/plain' and impl[0] != 'GXVxxxx':
                    continue
    
            if body:
                logging.info('Endpoint %s@%s appears to have %s interface...' %
                             (self._vendorname, self._ip, impl[0]))
                return impl[2](vars)
            else:
                logging.error('Failed to detect %s' % impl[0])
                return False

        logging.warning('Endpoint %s@%s cannot identify HTTP interface, static provisioning might not work.' %
                        (self._vendorname, self._ip))
        return True

    def _parseBotchedJSONResponse(self, response):
        body = response.read().decode('utf-8')
        logging.info(body)
        jsonvars = json.loads(body)
        return jsonvars


    def _enableStaticProvisioning_BT200(self, vars):
        try:
            # Login into interface
            cookiejar = http.cookiejar.CookieJar(http.cookiejar.DefaultCookiePolicy(rfc2965=True))
            opener = urllib3.PoolManager(cert_reqs='CERT_NONE', ca_certs=False)
            response = opener.request('POST', 'http://' + self._ip + '/dologin.htm',
                fields={'Login': 'Login', 'P2': self._http_password, 'gnkey': '0b82'})
            body = response.data
            if b'dologin.htm' in body:
                logging.error('Endpoint %s@%s BT200 - dologin failed login' %
                    (self._vendorname, self._ip))
                return False
    
            # Force cookie version to 0
            for cookie in cookiejar:
                cookie.version = 0
    
            response = opener.request('POST', 'http://' + self._ip + '/update.htm',
                fields={**vars, 'gnkey': '0b82'})
            body = response.data
            if b'dologin.htm' in body:
                logging.error('Endpoint %s@%s BT200 - dologin failed to keep session' %
                    (self._vendorname, self._ip))
                return False
    
            return True
        except urllib3.exceptions.HTTPError as e:
            logging.error('Endpoint %s@%s BT200 failed to send vars to interface - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s BT200 failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
 
    def _enableStaticProvisioning_BT200_old(self, vars):
        try:
            # Login into interface
            cookiejar = cookielib.CookieJar(cookielib.DefaultCookiePolicy(rfc2965=True))
            opener = urllib3.build_opener(urllib3.HTTPCookieProcessor(cookiejar))
            response = opener.open('http://' + self._ip + '/dologin.htm',
                urlencode({'Login' : 'Login', 'P2' : self._http_password, 'gnkey' : '0b82'}))
            body = response.read()
            if 'dologin.htm' in body:
                logging.error('Endpoint %s@%s BT200 - dologin failed login' %
                    (self._vendorname, self._ip))
                return False

            # Force cookie version to 0
            for cookie in cookiejar:
                cookie.version = 0
            
            response = opener.open('http://' + self._ip + '/update.htm',
                urlencode(vars) + '&gnkey=0b82')
            body = response.read()
            if 'dologin.htm' in body:
                logging.error('Endpoint %s@%s BT200 - dologin failed to keep session' %
                    (self._vendorname, self._ip))
                return False

            return True
        except urllib3.HTTPError as e:
            logging.error('Endpoint %s@%s BT200 failed to send vars to interface - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s BT200 failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False


    def _enableStaticProvisioning_GXP140x(self, vars):
        try:
            # Login into interface and get SID. Check proper Content-Type
            conn = http.client.HTTPConnection(self._ip)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = urlencode({'password': self._http_password})
            conn.request('POST', '/cgi-bin/dologin', body=payload, headers=headers)
            response = conn.getresponse()

            body = response.read().decode('utf-8')

            content_type = response.headers.get('Content-Type', '').split(';', 1)[0]
            if content_type != 'application/json':
                logging.error('Endpoint %s@%s GXP140x - dologin answered not application/json but %s' %
                              (self._vendorname, self._ip, content_type))
                return False

            # Check successful login and get sid
            jsonvars = json.loads(body)
            if not ('body' in jsonvars and 'sid' in jsonvars['body']):
                logging.error('Endpoint %s@%s GXP140x - dologin failed login' %
                              (self._vendorname, self._ip))
                return False
            sid = jsonvars['body']['sid']

            # Post vars with sid
            vars.update({'sid': sid})
            payload = urlencode(vars)
            conn.request('POST', '/cgi-bin/api.values.post', body=payload, headers=headers)
            response = conn.getresponse()

            jsonvars = self._parseBotchedJSONResponse(response)
            if jsonvars is None:
                logging.error('jsonvars vacio %s@%s GXP140x - vars rejected by interface - %s - %s - %s' %
                              (self._vendorname, self._ip, urlencode(vars), 'N/A', sid))
                return False

            if not ('response' in jsonvars and jsonvars['response'] == 'success'
                    and 'body' in jsonvars and 'status' in jsonvars['body'] and jsonvars['body']['status'] == 'right'):
                logging.error('Endpoint %s@%s GXP140x - vars rejected by interface - %s - %s - %s' %
                              (self._vendorname, self._ip, urlencode(vars), jsonvars['body'], sid))
                return False

            return True
        except json.JSONDecodeError as e:
            logging.error('Endpoint %s@%s GXP140x received invalid JSON - %s' %
                          (self._vendorname, self._ip, str(e)))
            return False
        except http.client.HTTPException as e:
            logging.error('Endpoint %s@%s GXP140x failed to send vars to interface - %s' %
                          (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s GXP140x failed to connect - %s' %
                          (self._vendorname, self._ip, str(e)))
            return False


    def _enableStaticProvisioning_GXV(self, vars):
        try:
            # Login into interface
            http = urllib3.PoolManager()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
            }
            response = http.request('GET', 'http://' + self._ip + '/manager?' + urlencode({
                'action': 'login',
                'Username': self._http_username,
                'Secret': self._http_password,
                'time': int(time.time())
            }), headers=headers)
            body = response.data
            if b'Error' in body:
                logging.error('Endpoint %s@%s GXV - dologin failed login' %
                              (self._vendorname, self._ip))
                return False

            # For this interface, the variables are translated as follows: The
            # source key of the form Pxxxx produces a variable var-dddd where
            # dddd is a counter. The corresponding value produces a variable
            # val-dddd with the same counter
            varcount = 0
            submitvars = {
                'action': 'put',
                'time': int(time.time())
            }
            for pk in vars:
                varkey = 'var-' + ('%04d' % (varcount,))
                varval = 'val-' + ('%04d' % (varcount,))
                submitvars[varkey] = pk[1:]
                submitvars[varval] = vars[pk]
                varcount += 1

            headers = {
                'User-Agent': headers['User-Agent'],
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = http.request('POST', 'http://' + self._ip + '/manager', fields=submitvars, headers=headers)
            body = response.data
            if not b'Success' in body:
                logging.error('Endpoint %s@%s GXV - dologin failed to keep session' %
                              (self._vendorname, self._ip))
                return False

            # Phonebook programming is a special case.
            submitvars = {
                'action': 'putdownphbk',
                'time': int(time.time()),
                'url': vars['P331'],
                'mode': 2,  # HTTP
                'clear-old': 1,
                'flag': 1,  # 1 forces download right now
                'interval': vars['P332'],
                'rm-redup': 1
            }

            response = http.request('POST', 'http://' + self._ip + '/manager', fields=submitvars, headers=headers)
            body = response.data
            if not b'Success' in body:
                logging.error('Endpoint %s@%s GXV - could not reprogram phonebook' %
                              (self._vendorname, self._ip))

            return True
        except http.client.HTTPException as e:
            logging.info('Endpoint %s@%s GXV failed to send vars to interface - %s' %
                         (self._vendorname, self._ip, str(e)))
            return True
        except urllib3.exceptions.HTTPError as e:
            logging.error('Endpoint %s@%s GXV failed to send vars to interface - %s' %
                          (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s GXV failed to connect - %s' %
                          (self._vendorname, self._ip, str(e)))
            return False

    def _enableStaticProvisioning_GXV_old(self, vars):
        try:
            # Login into interface
            opener = urllib3.build_opener(urllib3.HTTPCookieProcessor())
            headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            }
            opener.addheaders = headers.items()
            response = opener.open('http://' + self._ip + '/manager?' + urlencode({
                'action': 'login',
                'Username' : self._http_username,
                'Secret' : self._http_password,
                'time':     (int)(time.time())}))
            body = response.read()
            if 'Error' in body:
                logging.error('Endpoint %s@%s GXV - dologin failed login' %
                    (self._vendorname, self._ip))
                return False

            # For this interface, the variables are translated as follows: The
            # source key of the form Pxxxx produces a variable var-dddd where
            # dddd is a counter. The corresponding value produces a variable
            # val-dddd with the same counter
            varcount = 0
            submitvars = {
                'action'    : 'put',
                'time'      :   (int)(time.time())
            }
            for pk in vars:
                varkey = 'var-' + ('%04d' % (varcount,))
                varval = 'val-' + ('%04d' % (varcount,))
                submitvars[varkey] = pk[1:]
                submitvars[varval] = vars[pk]
                varcount += 1
            response = opener.open('http://' + self._ip + '/manager?' + urlencode(submitvars))
            body = response.read()
            if not ('Success' in body):
                logging.error('Endpoint %s@%s GXV - dologin failed to keep session' %
                    (self._vendorname, self._ip))
                return False

            # Phonebook programming is a special case.
            submitvars = {
                'action'    :   'putdownphbk',
                'time'      :   (int)(time.time()),
                'url'       :   vars['P331'],
                'mode'      :   2,  # HTTP
                'clear-old' :   1,
                'flag'      :   1,  # 1 forces download right now
                'interval'  :   vars['P332'],
                'rm-redup'  :   1                
            }
            # This generates problems with GXV3240
            # logging.info('Endpoint %s@%s GXV failed to send vars to interface - %s' %
            #    (self._vendorname, self._ip, 'http://' + self._ip + '/manager?' + urlencode(submitvars)))
            # response = opener.open('http://' + self._ip + '/manager?' + urlencode(submitvars))
            # body = response.read()
            # if not ('Success' in body):
            #    logging.error('Endpoint %s@%s GXV - could not reprogram phonebook' %
            #        (self._vendorname, self._ip))
                    
            return True
        except http.client.HTTPException as e:
            logging.info('Endpoint %s@%s GXV failed to send vars to interface - %s' %
                (self._vendorname, self._ip, str(e)))
            return True
        except urllib3.HTTPError as e:
            logging.error('Endpoint %s@%s GXV failed to send vars to interface - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s GXV failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False

    def _enableStaticProvisioning_GXP1450(self, vars):
        try:
            # Login into interface
            http = urllib3.PoolManager()
            response = http.request('POST', 'http://' + self._ip + '/cgi-bin/dologin',
                fields={'Login': 'Login', 'P2': self._http_password, 'gnkey': '0b82'})
            body = response.data
            if b'dologin' in body:
                logging.error('Endpoint %s@%s GXP1450 - dologin failed login' %
                    (self._vendorname, self._ip))
                return False
    
            response = http.request('POST', 'http://' + self._ip + '/cgi-bin/update',
                fields={**vars, 'gnkey': '0b82'})
            body = response.data
            if b'dologin' in body:
                logging.error('Endpoint %s@%s GXP1450 - dologin failed to keep session' %
                    (self._vendorname, self._ip))
                return False

            return True
        except socket.error as e:
            logging.error('Endpoint %s@%s GXP1450 failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False

    def _enableStaticProvisioning_GXP1450_old(self, vars):
        try:
            # Login into interface
            opener = urllib3.build_opener(urllib3.HTTPCookieProcessor())
            response = opener.open('http://' + self._ip + '/cgi-bin/dologin',
                urlencode({'Login' : 'Login', 'P2' : self._http_password, 'gnkey' : '0b82'}))
            body = response.read()
            if 'dologin' in body:
                logging.error('Endpoint %s@%s GXP1450 - dologin failed login' %
                    (self._vendorname, self._ip))
                return False

            response = opener.open('http://' + self._ip + '/cgi-bin/update',
                urlencode(vars) + '&gnkey=0b82')
            body = response.read()
            if 'dologin' in body:
                logging.error('Endpoint %s@%s GXP1450 - dologin failed to keep session' %
                    (self._vendorname, self._ip))
                return False
            return True
        except socket.error as e:
            logging.error('Endpoint %s@%s GXP1450 failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
       
 

    def _rebootbytelnet(self):
        '''Start reboot of Grandstream phone by telnet'''
        try:
            telnet = telnetlib.Telnet()
            telnet.open(self._ip)
            telnet.get_socket().settimeout(10)
        except socket.timeout as e:
            logging.error('Endpoint %s@%s failed to telnet - timeout (%s)' %
                (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s failed to telnet - %s' %
                (self._vendorname, self._ip, str(e)))
            return False

        # The Grandstream GXV3175 needs to have a wait of at least 1 second with
        # the stream open after the reboot command before the reboot command 
        # will actually take effect. We let the timeout close the telnet stream.
        telnetwaitmodels = ('GXV3140', 'GXV3175', 'GXP2120', 'GXP1400', 'GXP1405', 'GXP1450')
        deliberatetimeout = False
        
        # Attempt to login into admin telnet
        try:
            #telnet.read_until('Login:')
            if self._telnet_username != None: telnet.write(self._telnet_username.encode() + '\r\n')
            telnet.read_until('Password:', 10)
            if self._telnet_password != None: telnet.write(self._telnet_password.encode() + '\r\n')

            # Wait for either prompt or login prompt
            idx, m, text = telnet.expect([r'Password:', r'>\s?'], 10)
            if idx == 0:
                telnet.close()
                logging.error('Endpoint %s@%s detected ACCESS DENIED on telnet connect' %
                              (self._vendorname, self._ip))
                return False
            else:
                if self._model in ('GXV3140', 'GXV3175'):
                    rebootcommand = 'reboot'
                else:
                    # GXP280 accepts just a 'r'
                    rebootcommand = 'reboot'
                telnet.write(rebootcommand + '\r\n')
                idx, m, text = telnet.expect([r'Rebooting', r'reboot'], 10)
                if self._model in telnetwaitmodels:
                    telnet.get_socket().settimeout(1)
                    deliberatetimeout = True
                    logging.info('Endpoint %s@%s waiting 1 second for reboot to take effect' %
                        (self._vendorname, self._ip))
                    telnet.read_all()
                else:
                    # For other models, reboot takes effect immediately
                    telnet.close()
        except socket.timeout as e:
            telnet.close()
            if not deliberatetimeout:
                logging.error('1 Endpoint %s@%s connection failure - %s' %
                    (self._vendorname, self._ip, str(e)))
                return False
        except socket.error as e:
            logging.error('2 Endpoint %s@%s connection failure - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        return True        

    def _rebootbyssh(self):
        '''Start reboot of Grandstream phone by ssh'''
        oldtimeout = socket.getdefaulttimeout()
        #oldtimeout = 15
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh.connect(self._ip, username=self._ssh_username, password=self._ssh_password, allow_agent=False,look_for_keys=False, timeout=15)
            stdin, stdout, stderr = ssh.exec_command('reboot')            

            logging.info('Endpoint %s@%s - about to set timeout of %d on stdout' % (self._vendorname, self._ip, oldtimeout,))
            stdout.channel.settimeout(15)
            try:
                s = stdout.read()
                logging.info('Endpoint %s@%s - answer follows:\n%s' % (self._vendorname, self._ip, s,))
            except socket.error as e:
                pass
            finally:
                ssh.close()
            return True

        except paramiko.AuthenticationException as e:
            logging.error('Endpoint %s@%s failed to authenticate ssh - %s (%s:%s)' %
                (self._vendorname, self._ip, str(e), self._ssh_username, self._ssh_password))
        except paramiko.SSHException as e:
            logging.warning('Endpoint %s@%s failed to authenticate ssh - %s (%s:%s)' %
                (self._vendorname, self._ip, str(e), self._ssh_username, self._ssh_password))
            return False
        except urllib3.URLError as e:
            logging.error('Endpoint %s@%s failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        except socket.error as e:
            logging.error('Endpoint %s@%s failed to connect - %s' %
                (self._vendorname, self._ip, str(e)))
            return False

    def _rebootbyhttp(self):
        try:
            # Establish a connection to the server
            conn = http.client.HTTPConnection(self._ip)
            url = f'/cgi-bin/api-sys_operation?passcode={self._http_password}&request=REBOOT'
    
            # Send an HTTP GET request
            conn.request('GET', url)
    
            # Get the response
            response = conn.getresponse()
    
            # Read the response data and decode it
            data = response.read().decode('utf-8')
    
            # Parse the response as JSON
            jsonvars = json.loads(data)
    
            if not ('response' in jsonvars and jsonvars['response'] == 'success'):
                logging.error('Endpoint %s@%s unimplemented reboot by HTTP' %
                              (self._vendorname, self._ip))
                return False
    
            return True
        except Exception as e:
            logging.error(f'An error occurred: {str(e)}')
            return False

    def _hashTableGrandstreamConfig(self):
        stdvars = self._prepareVarList()
        
        # Remove 'http://' from begingging of string
        stdvars['phonesrv'] = stdvars['phonesrv'][7:]
        
        o = stdvars['server_ip'].split('.')
        vars = {
            'P6767' :   '0', # Firmware Upgrade Via 0 - TFTP,  1 - HTTP, 2 - HTTPS
            'P192'  :   stdvars['server_ip'], # Firmware Server Path
            'P237'  :   stdvars['server_ip'], # Config Server Path
            'P212'  :   '0',            # Firmware Upgrade. 0 - TFTP Upgrade,  1 - HTTP Upgrade.
            'P290'  :   '{ x+ | *x+ | *x | *xx*x+ }', # (GXV3175 specific) Dialplan string

            'P30'   :   stdvars['server_ip'], # NTP server
            'P64'   :   self._timeZone,
            'P144'  :   '0',    # Allow DHCP 42 to override NTP server?
            'P143'  :   '1',    # Allow DHCP to override timezone setting.

            'P8'    :   '0',            # DHCP=0 o static=1
            'P41': o[0], 'P42': o[1], 'P43': o[2], 'P44': o[3], # TFTP Server
            
            'P330'  :   1,    # 0-Disable phonebook download 1-HTTP 2-TFTP 3-HTTPS
            'P331'  :   stdvars['phonesrv'],
            'P332'  :   20,   # Minutes between XML phonebook fetches, or 0 to disable,
            
            'P1376' :   '1',  # Enable automatic attended transfer
        
            # TODO: inherit server language
            'P1362' :   self._language, # Phone display language
        }
        
        # Do per-model variable adjustments
        self._updateVarsByModel(stdvars, vars)
        
        if not self._dhcp:
            vars.update({
                'P8'     :  '1',    # DHCP=0 o static=1
            })
            if stdvars['static_ip'] != None:
                # IP Address
                o = stdvars['static_ip'].split('.')
                vars.update({'P9':  o[0], 'P10': o[1], 'P11': o[2], 'P12': o[3],})
            if stdvars['static_mask'] != None:
                # Subnet Mask
                o = stdvars['static_mask'].split('.')
                vars.update({'P13': o[0], 'P14': o[1], 'P15': o[2], 'P16': o[3],})
            if stdvars['static_gateway'] != None:
                # Gateway
                o = stdvars['static_gateway'].split('.')
                vars.update({'P17': o[0], 'P18': o[1], 'P19': o[2], 'P20': o[3],})
            if stdvars['static_dns1'] != None:
                # DNS Server 1
                o = stdvars['static_dns1'].split('.')
                vars.update({'P21': o[0], 'P22': o[1], 'P23': o[2], 'P24': o[3],})
            if stdvars['static_dns2'] != None:
                # IP Address
                o = stdvars['static_dns2'].split('.')
                vars.update({'P25': o[0], 'P26': o[1], 'P27': o[2], 'P28': o[3],})
        
        varmap = self._grandstreamvarmap()

        # Blank out all variables prior to assignment
        for i in range(0, min(len(varmap), stdvars['max_sip_accounts'])):
            vars[varmap[i]['enable']] = 0
            vars[varmap[i]['sipserver']] = stdvars['server_ip'] + ':' + stdvars['sip'][0].server_port
            vars[varmap[i]['outboundproxy']] = stdvars['server_ip'] + ':' + stdvars['sip'][0].server_port
            vars[varmap[i]['sipserver']] = stdvars['server_ip']
            vars[varmap[i]['outboundproxy']] = stdvars['server_ip']
            vars[varmap[i]['accountname']] = ''
            vars[varmap[i]['displayname']] = ''
            vars[varmap[i]['sipid']] = ''
            vars[varmap[i]['authid']] = ''
            vars[varmap[i]['secret']] = ''
            vars[varmap[i]['autoanswercallinfo']] = 1
        
        for i in range(0, min(len(varmap), len(stdvars['sip']))):
            vars[varmap[i]['enable']] = 1
            vars[varmap[i]['accountname']] = stdvars['sip'][i].description
            vars[varmap[i]['displayname']] = stdvars['sip'][i].description
            vars[varmap[i]['sipid']] = stdvars['sip'][i].extension
            vars[varmap[i]['authid']] = stdvars['sip'][i].account
            vars[varmap[i]['secret']] = stdvars['sip'][i].secret
        return vars

    # Should override this method if the model for the new vendor requires
    # additional variable modification.
    def _updateVarsByModel(self, stdvars, vars):
        if self._model in ('GXP280',):
            vars.update({'P73' : '1'})  # Send DTMF. 8 - in audio, 1 - via RTP, 2 - via SIP INFO

        if self._model in ('GXP2160',):
            # Set wallpaper
            vars.update({'P2916' : '1'})
            vars.update({'P2917' : 'tftp://' + stdvars['server_ip'] + '/backgrounds/grandstream/gxp21xx.jpg'})
            # Set Voicemail access number
            vars.update({'P33' : '*97'})

        if self._model in ('GXP1625',):
            # Set Voicemail access number
            vars.update({'P33' : '*97'})
 

    def _grandstreamvarmap(self): 
        varmap = [
            {'enable'               :   'P271', # Enable account
             'accountname'          :   'P270', # Account Name
             'sipserver'            :   'P47',  # SIP Server
             'sipid'                :   'P35',  # SIP User ID
             'authid'               :   'P36',  # Authenticate ID
             'secret'               :   'P34',  # Authenticate password
             'displayname'          :   'P3',   # Display Name (John Doe)
             'outboundproxy'        :   'P48',  # Outbound Proxy
             'autoanswercallinfo'   :   'P298', # Enable auto-answer by Call-Info
            },
            {'enable'               :   'P401', # Enable account
             'accountname'          :   'P417', # Account Name
             'sipserver'            :   'P402', # SIP Server
             'sipid'                :   'P404', # SIP User ID
             'authid'               :   'P405', # Authenticate ID
             'secret'               :   'P406', # Authenticate password
             'displayname'          :   'P407', # Display Name (John Doe)
             'outboundproxy'        :   'P403', # Outbound Proxy
             'autoanswercallinfo'   :   'P438', # Enable auto-answer by Call-Info
            },
            {'enable'               :   'P501', # Enable account
             'accountname'          :   'P517', # Account Name
             'sipserver'            :   'P502', # SIP Server
             'sipid'                :   'P504', # SIP User ID
             'authid'               :   'P505', # Authenticate ID
             'secret'               :   'P506', # Authenticate password
             'displayname'          :   'P507', # Display Name (John Doe)
             'outboundproxy'        :   'P503',  # Outbound Proxy
             'autoanswercallinfo'   :   'P538', # Enable auto-answer by Call-Info
            },
            {'enable'               :   'P601', # Enable account
             'accountname'          :   'P617', # Account Name
             'sipserver'            :   'P602', # SIP Server
             'sipid'                :   'P604', # SIP User ID
             'authid'               :   'P605', # Authenticate ID
             'secret'               :   'P606', # Authenticate password
             'displayname'          :   'P607', # Display Name (John Doe)
             'outboundproxy'        :   'P603', # Outbound Proxy
             'autoanswercallinfo'   :   'P638', # Enable auto-answer by Call-Info
            },
            {'enable'               :   'P1701',# Enable account
             'accountname'          :   'P1717',# Account Name
             'sipserver'            :   'P1702',# SIP Server
             'sipid'                :   'P1704',# SIP User ID
             'authid'               :   'P1705',# Authenticate ID
             'secret'               :   'P1706',# Authenticate password
             'displayname'          :   'P1707',# Display Name (John Doe)
             'outboundproxy'        :   'P1703',# Outbound Proxy
             'autoanswercallinfo'   :   'P1738',# Enable auto-answer by Call-Info
            },
            {'enable'               :   'P1801',# Enable account
             'accountname'          :   'P1817',# Account Name
             'sipserver'            :   'P1802',# SIP Server
             'sipid'                :   'P1804',# SIP User ID
             'authid'               :   'P1805',# Authenticate ID
             'secret'               :   'P1806',# Authenticate password
             'displayname'          :   'P1807',# Display Name (John Doe)
             'outboundproxy'        :   'P1803',# Outbound Proxy
             'autoanswercallinfo'   :   'P1838',# Enable auto-answer by Call-Info
            },
        ]
        
        return varmap

    def _encodeGrandstreamConfig(self, vars):
        # Encode configuration variables. The gnkey must be the last item in
        # order to prevent other variables from being followed by a null byte.
        payload = urlencode(vars) + '&gnkey=0b82'
        if (len(payload) & 1) != 0:
            payload += '\x00'

        # Calculate block length in words, plus checksum
        length = 8 + len(payload) // 2

        # Convert mac address to bytes
        binmac_no_colons = self._mac.replace(':', '').lower()
        binmac = bytes.fromhex(binmac_no_colons)

        # Pack the data into bytes
        bindata = struct.pack('>LH6s' + str(len(payload)) + 's', length, 0, binmac, payload.encode('utf-8'))
        #bindata = struct.pack('>LH6s', length, 0, binmac) + b'\x0d\x0a\x0d\x0a' + payload
  
        wordsize = len(bindata) // 2
        checksum = 0x10000 - (sum(struct.unpack('>' + str(wordsize) + 'H', bindata)) & 0xFFFF)

        # Repack the data with the correct checksum
        bindata = struct.pack('>LH6s', length, checksum, binmac) + b'\x0d\x0a\x0d\x0a' + payload.encode('utf-8')

        return bindata  
