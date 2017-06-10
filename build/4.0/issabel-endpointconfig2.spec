%define modname endpointconfig2

Summary: Issabel Endpoint Configurator Module
Name:    issabel-%{modname}
Version: 4.0.0
Release: 1
License: GPL
Group:   Applications/System
Source0: %{modname}_%{version}-%{release}.tgz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Requires: issabelPBX >= 2.8.1-12
Requires: issabel-framework >= 4.0.0-1
Requires: issabel-agenda >= 4.0.0-1
Requires: py-Asterisk
Requires: python-eventlet
Requires: python-tempita
Requires: pyOpenSSL
Requires: python-daemon
Requires: MySQL-python
Requires: python-cjson
Requires: php-simplepie
Requires: python-paramiko >= 1.7.6-2
Requires: nmap
Requires(pre): tftp-server
Conflicts: elastix-pbx <= 2.4.0-15

Obsoletes: issabel-endpointconfig2

%description
The Issabel Endpoint Configurator is a complete rewrite and reimplementation of
the elastix-pbx module known as the Endpoint Configurator. This rewrite
addresses several known design flaws in the old Endpoint Configurator and should
eventually be integrated as the new standard configurator in issabel-pbx.

User-visible features:
- Supports assignment of multiple accounts to a single endpoint.
- Automatic model detection implemented for most supported manufacturers.
- Improved user interface written with Ember.js.
- Network parameters can be updated onscreen in addition to being uploaded.
- Endpoint network scan is cancellable.
- The configuration of every endpoint is executed in parallel, considerably
  shortening the potential wait until all endpoints are configured.
- A log of the actual endpoint configuration can be displayed for diagnostics.
- Supports two additional download formats in addition to the download format of
  the old endpoint configurator - required for multiple account support.
- Custom properties can be assigned to the endpoint and per account, until GUI
  support is properly added.
- Can be installed alongside the old endpoint configurator.
- For supported phones, the module provides an HTTP resource to serve remote
  services, such as a phonebook browser, for better integration with Issabel.

For developers:
- The architecture of the module is plugin-friendly. Each vendor implementation
  (written in Python) has been completely encapsulated and no vendor-specific
  logic remains in the module core itself. To add a new vendor, it is enough to
  write a new implementation class in Python, add new templates if necessary,
  and add database records for MACs. Patching of the core is no longer required.
- Foundation for replacing the standard configurator dialog with a
  vendor-specific one (not yet used).

%prep
%setup -n %{name}_%{version}-%{release}

%install
rm -rf $RPM_BUILD_ROOT

# Files provided by all Issabel modules
mkdir -p                        $RPM_BUILD_ROOT/var/www/html/
mv modules/                     $RPM_BUILD_ROOT/var/www/html/

# Additional (module-specific) files that can be handled by RPM
mkdir -p $RPM_BUILD_ROOT/etc/
mv setup/etc/httpd/ $RPM_BUILD_ROOT/etc/

mv setup/usr/ $RPM_BUILD_ROOT/
mkdir -p $RPM_BUILD_ROOT/usr/local/share/issabel/endpoint-classes/tpl

rm -rf setup/build/

# ** /tftpboot path ** #
# ** files tftpboot for endpoints configurator ** #
mkdir -p $RPM_BUILD_ROOT/tftpboot
unzip setup/tftpboot/P0S3-08-8-00.zip  -d     $RPM_BUILD_ROOT/tftpboot/
rm setup/tftpboot/P0S3-08-8-00.zip
mv setup/tftpboot/*                           $RPM_BUILD_ROOT/tftpboot/
rmdir setup/tftpboot

# The following folder should contain all the data that is required by the installer,
# that cannot be handled by RPM.
mkdir -p    $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mv setup/   $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mv menu.xml $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/

%pre
mkdir -p /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
touch /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
if [ $1 -eq 2 ]; then
    rpm -q --queryformat='%{VERSION}-%{RELEASE}' %{name} > /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
fi


%post
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"

# Run installer script to fix up ACLs and add module to Elastix menus.
issabel-menumerge /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/menu.xml

pathSQLiteDB="/var/www/db"
mkdir -p $pathSQLiteDB
preversion=`cat $pathModule/preversion_%{modname}.info`

if [ $1 -eq 1 ]; then #install
  # The installer database
    issabel-dbprocess "install" "$pathModule/setup/db"

  # Restart apache to disable HTTPS redirect on phonesrv script
  /sbin/service httpd restart
elif [ $1 -eq 2 ]; then #update
    issabel-dbprocess "update"  "$pathModule/setup/db" "$preversion"
fi
rm -f $pathModule/preversion_%{modname}.info

# Remove old endpointconfig2 menu item
issabel-menuremove endpointconfig2

# Prepare tftpboot for use by module
chmod 777 /tftpboot/
cat /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/setup/etc/xinetd.d/tftp > /etc/xinetd.d/tftp


%clean
rm -rf $RPM_BUILD_ROOT

%preun
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"
if [ $1 -eq 0 ] ; then # Validation for desinstall this rpm
  echo "Delete distributed dial plan menus"
  issabel-menuremove "%{modname}"

  echo "Dump and delete %{name} databases"
  issabel-dbprocess "delete" "$pathModule/setup/db"
fi


%files
%defattr(-, root, root)
%{_localstatedir}/www/html/*
/usr/share/issabel/module_installer/*
/usr/share/issabel/endpoint-classes
/usr/local/share/issabel/endpoint-classes
/tftpboot/*
%defattr(644, root, root)
/etc/httpd/conf.d/issabel-endpointconfig.conf
%defattr(755, root, root)
/usr/bin/*
/usr/share/issabel/privileged/*

%changelog
