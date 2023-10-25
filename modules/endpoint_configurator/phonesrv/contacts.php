<?php
/*
  vim: set expandtab tabstop=4 softtabstop=4 shiftwidth=4:
  Codificación: UTF-8
  +----------------------------------------------------------------------+
  | Issabel version 1.0                                                  |
  | http://www.issabel.org                                               |
  +----------------------------------------------------------------------+
  | Copyright (c) 2006 Palosanto Solutions S. A.                         |
  +----------------------------------------------------------------------+
  | The contents of this file are subject to the General Public License  |
  | (GPL) Version 2 (the "License"); you may not use this file except in |
  | compliance with the License. You may obtain a copy of the License at |
  | http://www.opensource.org/licenses/gpl-license.php                   |
  |                                                                      |
  | Software distributed under the License is distributed on an "AS IS"  |
  | basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See  |
  | the License for the specific language governing rights and           |
  | limitations under the License.                                       |
  +----------------------------------------------------------------------+
  | Autores: Alex Villacís Lasso <a_villacis@palosanto.com>              |
  +----------------------------------------------------------------------+
  $Id: contacts.php, Wed 25 Oct 2023 11:46:02 AM EDT, nicolas@issabel.com
*/

define('ISSABEL_BASE', '/var/www/html/');
require_once(ISSABEL_BASE.'libs/misc.lib.php');
require_once(ISSABEL_BASE.'configs/default.conf.php');
require_once(ISSABEL_BASE.'libs/paloSantoDB.class.php');
include_once(ISSABEL_BASE."libs/paloSantoACL.class.php");

load_default_timezone();

if (!isset($_SERVER['PATH_INFO'])) {
    header('HTTP/1.1 404 Not Found');
    print 'No path info for phone resource! Expected /VENDOR/AUTHTOKEN/resource';
	exit;
}
$pathList = explode('/', $_SERVER['PATH_INFO']);
array_shift($pathList);

// Los primeros 2 elementos son VENDOR, AUTHTOKEN
if (count($pathList) < 2) {
    header('HTTP/1.1 404 Not Found');
    print 'No path info for phone resource! Expected /VENDOR/AUTHTOKEN/resource';
    exit;
}

$sManufacturer = array_shift($pathList);
$sAuthToken = array_shift($pathList);

if (!preg_match('/^\w+$/', $sManufacturer)) {
    header('HTTP/1.1 404 Not Found');
    print 'Unimplemented manufacturer';
    exit;
}

$sVendorPath = "vendor/$sManufacturer.class.php";
if (!file_exists($sVendorPath)) {
    header('HTTP/1.1 404 Not Found');
    print 'Unimplemented manufacturer';
    exit;
}
require_once $sVendorPath;

// Conexión a la base de datos
$pdbACL  = new paloDB($arrConf["issabel_dsn"]["acl"]);
$pACL = new paloACL($pdbACL);

$endpoint_id = NULL;
$partes = preg_split("/:/",$sAuthToken);
$exten = $partes[0];
$pass_md5 = md5($partes[1]);
if(!$pACL->authenticateUser($exten, $pass_md5)) {
     header('HTTP/1.1 403 Forbidden');
     print 'Invalid hash';
     exit;
} else {
    $dsn = generarDSNSistema('asteriskuser', 'endpointconfig', ISSABEL_BASE);
    $db = new paloDB($dsn);
    $vendor = new $sManufacturer($db, 'http://'.$_SERVER['SERVER_ADDR'].'/modules/endpoint_configurator/phonesrv/contacts.php/'.$sManufacturer.'/'.$sAuthToken);
    $vendor->handle("exten$exten", $pathList);
}
?>
