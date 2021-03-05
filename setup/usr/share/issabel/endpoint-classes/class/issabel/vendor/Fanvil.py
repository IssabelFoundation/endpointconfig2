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
import time
from issabel.BaseEndpoint import BaseEndpoint
import issabel.vendor.Atcom
from eventlet.green import socket

class Endpoint(issabel.vendor.Atcom.Endpoint):
    def __init__(self, amipool, dbpool, sServerIP, sIP, mac):
        BaseEndpoint.__init__(self, 'Fanvil', amipool, dbpool, sServerIP, sIP, mac)
        self._bridge = True
        stdtimeZone = BaseEndpoint.getTimezoneOffset() / 60 / 60
        self._timeZone = stdtimeZone * 4

    def probeModel(self):
        '''Probe specific model of the Fanvil phone

        Attempt to fetch /title.htm . This contains the phone model
        '''
        self._http_username = 'admin'
        self._http_password = 'admin'
        htmlres = self._fetchAtcomAuthenticatedPage(('/information.htm', '/title.htm', '/currentstat.htm',))
        if htmlres != None:
            resource, htmlbody = htmlres

            # Fanvil returns /title.htm as the normal case
            if resource == '/title.htm':
                # C56/C56P</span>
                m = re.search(r'((C|X|D|i)\d+S?)(/\w+)?</span>', htmlbody)
                if m != None:
                    self._saveModel(m.group(1))
                    return
            elif resource == '/information.htm':
                # H2S H3 H5
                m = re.search(r'((C|X|D|i|H)\d+S?)(/\w+)?</td>', htmlbody)
                if m != None:
                    self._saveModel(m.group(1))
                    return
            # VopTech VI2007/VI2008 gets misidentified as Fanvil
            elif resource == '/currentstat.htm':
                if 'VOIP PHONE' in htmlbody:
                    self._saveVendor('VOPTech')

                    # TODO: this detection is duplicated in VOPTech.py
                    sipline3 = ('SIP LINE 3' in htmlbody)
                    iax = ('IAX' in htmlbody)
                    if iax and sipline3:
                        self._saveModel('VI2008')
                    elif iax and not sipline3:
                        self._saveModel('VI2007')
                    else:
                        self._saveModel('VI2006')

    def isModelV2(self):
        return (self._model in ('X1', 'X3', 'X3P', 'X4', 'X4P', 'X5', 'X5P', 'X6', 'X6P', 'C400', 'C400P', 'C600', 'C600P', 'D900','i20S', 'H5'))

    def updateLocalConfig(self):
        '''Configuration for Fanvil endpoints

        This phone is essentially a rebranded Atcom AT530+ with slightly
        different configuration directives. Apart from the template, the
        network-level interaction is identical to the AT530.
        '''
        # Check that there is at least one account to configure
        if len(self._accounts) <= 0:
            logging.error('Endpoint %s@%s has no accounts to configure' %
                (self._vendorname, self._ip))
            return False

        if self.isModelV2():
            if (self._model == 'X6') or (self._model == 'X1'):
                configVersion = self._fetchOldConfigVersion(('/default_user_config.txt',))
            else:
                configVersion = self._fetchOldConfigVersion(('/config.txt',))
        else:
            configVersion = self._fetchOldConfigVersion()
        if configVersion == None: return False
        t = str(int(''.join(configVersion.split('.'))) + 1)
        configVersion = t[:1] + '.' + t[1:]
        logging.info('Endpoint %s@%s new config version is %s' %
            (self._vendorname, self._ip, configVersion))

        # Need to calculate lowercase version of MAC address without colons
        sConfigFile = (self._mac.replace(':', '').lower()) + '.cfg'
        self._writeAtcom530Template(configVersion, sConfigFile, 'Fanvil_local.tpl')

        # Force download of new configuration followed by reboot
        if self._transferConfig2Phone(sConfigFile):
            self._unregister()
            self._setConfigured()
            return True
        else:
            return False

    def _transferConfig2Phone(self, sConfigFile):
        if not self.isModelV2():
            return parent._transferConfig2Phone(sConfigFile)

        status = True

        f = open(self._tftpdir + '/' +sConfigFile)
        content = f.read()
        f.close()

        http, nonce = self._setupAtcomAuthentication()
        if http == None: return False

        boundary = '------------------ENDPOINTCONFIG'
        postdata = '--' + boundary + '\r\n' +\
            'Content-Disposition: form-data; name="CONFIG"; filename="/config.txt"\r\n' +\
            'Content-Type: text/plain\r\n' +\
            '\r\n' +\
            content + '\r\n' +\
            '--' + boundary + '--\r\n'
        http.request('POST', '/config.htm', postdata,
            {
                'Content-Type' : ' multipart/form-data; boundary=' + boundary,
                'Connection' : 'keep-alive',
                'Cookie' : 'auth=' + nonce
            })
        try:
            resp = http.getresponse()
            htmlbody = resp.read()
            if resp.status != 200:
                logging.error('Endpoint %s@%s failed to post configuration - got response code %s' %
                    (self._vendorname, self._ip, resp.status))
                status = False
            elif (not 'Submit Success' in htmlbody):
                if not ('Phone in rebooting' in htmlbody):
                    logging.error('Endpoint %s@%s failed to post configuration - unknown body follows: %s' %
                        (self._vendorname, self._ip, htmlbody))
                    status = False

            # TODO: does this race with the phone reboot?
            if not self._cleanupAtcomAuthentication(http, nonce):
                status = False
            return status
        except:
             if self._model == 'X6':
                 status = True
                 return status
             else:    
                 logging.warning('Endpoint %s@%s HTTP Response Time Out' % (self._vendorname, self._ip))
