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
import glob
import os.path
import re
import issabel.BaseEndpoint
from issabel.BaseEndpoint import BaseEndpoint
import eventlet
telnetlib = eventlet.import_patched('telnetlib')


class Endpoint(BaseEndpoint):
    _global_serverip = None
    
    def __init__(self, amipool, dbpool, sServerIP, sIP, mac):
        BaseEndpoint.__init__(self, 'Cisco', amipool, dbpool, sServerIP, sIP, mac)
        
        self._timeZone = "SA Eastern Standard Time"

        if Endpoint._global_serverip == None:
            Endpoint._global_serverip = sServerIP
        elif Endpoint._global_serverip != sServerIP:
            logging.warning('global server IP is %s but endpoint %s requires ' + 
                'server IP %s - this endpoint might not work correctly.' %
                (Endpoint._global_serverip, sIP, sServerIP))

    # TODO: might be possible to derive model from MAC range, requires database change


    def setExtraParameters(self, param):
        if not BaseEndpoint.setExtraParameters(self, param): return False
        if 'timeZone' in param: self._timeZone = param['timeZone']
        return True


    def probeModel(self):
        ''' Probe specific model of the Cisco phone
        
        This probe first tries to get the model using telnet. If that fails, 
        it falls back to extracting the model from the web page.
        '''
        sModel = None
        
        sModel = self._probeModelTelnet()
        
        if not sModel:
            sModel = self._probeModelWeb()

        if sModel:
            self._saveModel(sModel)


    def _probeModelTelnet(self):
        '''Probe specific model of the Cisco phone using telnet'''
        sModel = None
        try:
            telnet = telnetlib.Telnet()
            telnet.open(self._ip)
            telnet.get_socket().settimeout(10)
        
            # Attempt login with default credentials
            telnet.read_until('Password :', 10)
            telnet.write('cisco\r\n') # Password            
            
            idx, m, text = telnet.expect([r'Password :', r'> '], 10)
            if idx == 0:
                raise Exception('Telnet login failed.')

            telnet.write('show config\r\n')
            text = telnet.read_until('> ', 10)
            telnet.write('exit\r\n')
            
            m = re.search(r'IP Phone CP-(\w+)', text)
            if m:
                sModel = m.group(1)
        
        except Exception as e:
            logging.error('Endpoint %s@%s connection failure - %s' %
                (self._vendorname, self._ip, str(e)))
        finally:
            telnet.close()

        return sModel

    
    def _probeModelWeb(self):
        '''Probe specific model of the Cisco phone from its web page'''
        sModel = None
        try:
            response = urllib3.urlopen('http://' + self._ip + '/')
            htmlbody = response.read()

            # Search for the text that contains the Cisco phone model
            model_match = re.search(r'IP Phone CP-(\w+)', htmlbody, re.IGNORECASE)

            if model_match:
                sModel = model_match.group(1)
        except Exception as e:
            logging.error('Endpoint %s@%s web connection failure - %s' %
                (self._vendorname, self._ip, str(e)))
        
        return sModel
        

    @staticmethod
    def updateGlobalConfig(serveriplist, amipool, endpoints):
        '''Configuration for Cisco endpoints (global)
        
        SIP global definition goes in /tftpboot/SIPDefault.cnf and has a 
        reference to a firmware file P0S*.sb2. If there are several files, the
        higher version is selected.
        '''
        sFirmwareVersion = None
        for sPathName in glob.glob(issabel.BaseEndpoint.TFTP_DIR + '/P0S*.sb2'):
            sVersion, ext = os.path.splitext(os.path.basename(sPathName))
            if sFirmwareVersion == None or sFirmwareVersion < sVersion:
                sFirmwareVersion = sVersion
        if sFirmwareVersion == None:
            logging.error('Failed to find firmware file P0S*.sb2 in ' + issabel.BaseEndpoint.TFTP_DIR)
            return False
        
        vars = {
            'firmware_version'  : sFirmwareVersion,
            'phonesrv'          : BaseEndpoint._buildPhoneProv(Endpoint._global_serverip, 'Cisco', 'GLOBAL'),
        }
        try:
            sConfigFile = 'SIPDefault.cnf'
            sConfigPath = issabel.BaseEndpoint.TFTP_DIR + '/' + sConfigFile
            BaseEndpoint._writeTemplate('Cisco_global_SIPDefault.tpl', vars, sConfigPath)
            return True
        except IOError as e:
            logging.error('Failed to write global config for Cisco - %s' % (str(e),))
            return False


    def updateLocalConfig(self):
        '''Update local configuration for Cisco endpoints

        The function generates the configuration file for Cisco endpoints based on the phone's MAC address.
        
        For XML compatible models, the configuration file is named SEPXXXXXXXXXXXX.cnf.xml,
        where XXXXXXXXXXXX is the UPPERCASE MAC address of the phone.
        
        For XML incompatible models, the configuration file is named SIPXXXXXXXXXXXX.cnf,
        following the same MAC address format.

        To reboot the phone, it is necessary to issue the AMI command:
        sip notify cisco-check-cfg {$EXTENSION}. Verified with Cisco 7960.
        '''
        try:
            # Check that there is at least one account to configure
            if not self._accounts:
                raise ValueError('Endpoint %s@%s has no accounts to configure' %
                    (self._vendorname, self._ip))

            # Need to calculate UPPERCASE version of MAC address without colons
            uppercase_mac = self._mac.replace(':', '').upper()
            config_file_name ='SEP' + uppercase_mac + '.cnf.xml'
            config_file_template = 'Cisco_local_SEP.tpl'

            if self._is_xml_incompatible():
                config_file_name = 'SIP' + uppercase_mac + '.cnf'
                config_file_template = 'Cisco_local_SIP.tpl'
        
            config_file_path = self._tftpdir + '/' + config_file_name

            vars = self._prepareVarList()
            vars.update({
            'timeZone':self._timeZone,
            'server_port':5060
		    })


            self._writeTemplate(config_file_template, vars, config_file_path)

            # Must execute cisco-check-cfg with extension, not IP
            if self._hasRegisteredExtension():
                self._amireboot('cisco-check-cfg')
            elif self._telnet_password != None and not self._rebootbytelnet():
                return False
            
            self._unregister()
            self._setConfigured()
            return True
        except IOError as e:
            logging.error('Endpoint %s@%s failed to write configuration file - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        except Exception as e:
            logging.error('Endpoint %s@%s failed to update local configuration - %s' %
                      (self._vendorname, self._ip, str(e)))
        return False

    def _is_xml_incompatible(self):
        # Implement logic to determine if the model is XML incompatible
        # For example, check the model name or model number
        # Return True for Cisco models that are XML incompatible, False otherwise
        # For demonstration purposes, assuming models 7960 and 7940 are XML incompatible
        # return self._model in ['7960', '7940']
        return False 

    def _rebootbytelnet(self):
        '''Start reboot of Cisco phone by telnet'''
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

        try:
            # Attempt login with default credentials
            telnet.read_until('Password :', 10)
            if self._telnet_password != None: telnet.write(self._telnet_password.encode() + '\r\n')            
            
            idx, m, text = telnet.expect([r'Password :', r'> '], 10)
            if idx == 0:
                # Login failed
                telnet.close()
                logging.error('Endpoint %s@%s detected ACCESS DENIED on telnet connect' %
                              (self._vendorname, self._ip))
                return False
            telnet.write('reset\r\n')
            telnet.close()
            
            return True
        except socket.error as e:
            logging.error('Endpoint %s@%s connection failure - %s' %
                (self._vendorname, self._ip, str(e)))
            return False
        
