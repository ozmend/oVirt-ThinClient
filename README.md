# INSTALL on CentOS7

## On Server site
- Install oVirt_Server according to your requirements
- Make a destkop OS templates
- On template OS enable QLX, Spice remote access option
- Enable USB redirection and Sound feedback

---

### Client Site

- "#	yum install epel-release -y"  

- "#	yum install python36 python36-devel python36-setuptools gcc gcc-c++ libcurl-devel libxml2-devel virt-viewer -y"  

- "#	easy_install-3.6 pip"

- "$	export PYCURL_SSL_LIBRARY=nss"

- "$	pip3.6 install --user -r requirements.txt"


** Copy ovirt_vdi files where ever you want and run oVirt_Client-beta.py file **

- "$ copy ovirt_vdi.tar.gz ~/"
- "$ tar -xzvf  ovirt_vdi.tar.gz"
- "$ cd ovirt_vdi"
- "$ ./oVirt_Client-beta.py"

** Edit config.cfg **

** Add new ovirt-ca.pem into conf/pki/ **

---

# ThinClient Image (CloneZilla)

I made a custom OS by using CentOS7 minimal.  
It contains, minimal linux, Xorg and Python libraries.  
Also, I applied OS hardening.  
Plus, i used usbguard to increase security. It block all usb devices until root user let it.  
You can use this as central usb deviceses management system.  

https://drive.google.com/open?id=1WwNMvczXPC40V2QlosyMm6tm1Nmr51jb  

This link has Clonezilla file. Extract it into wherever you want access from(ssh, samba, usb etc.)  
It's size is about 3,25GB(250MB /boot, 3GB /, NO SWAP)  
Use Clonezilla, and restore entire disk to your pc, vm etc.  
** To fit all partitions into your hdd, in expert mode choose "Don't check destination disk size" option **  
After cloning, change ssh public key for root user. Because password ssh is forbidden.  
Edit chg_hostname.sh file according to your system.  
Replace ovirt-ca.pem file with yours. It is under /home/tclient/ovirt_vdi/conf/pki/  

## It is ready...