FritzBox 
========
* always same IP for raspberry
* port forward to 444
* myFritz Konto - get hostname from there


Setup SSL certs/lighttpd
========================

openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -config ca.conf -extensions v3_ca -out rootCA.pem
openssl genrsa -out device.key 2048
openssl req -new -key device.key -out device.csr
openssl x509 -req -in device.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out device.crt -days 500 -sha256 -extfile <(printf "subjectAltName=DNS:*.myfritz.net")
#use *.myfritz.net for the CommonName
cat device.crt device.key > device.pem
#copy the device.pem to /etc/lighttpd/certs/lighttpd.pem


#import rootCA.pem in android/IOS - just send a mail containing the certs
#for IOS additional enable necessary: 
#https://stackoverflow.com/questions/49422164/how-to-install-self-signed-certificates-in-ios-11

Setup lighttpd
==============
install: 
apt-get install lighttpd
systemctl enable lighttpd
#copy lighttpd_sprinkler.conf to /etc/lighttpd/conf-enabled
systemctl restart lighttpd
#generate password to /home/pi/sprinkler/passwd - e.g. using http://www.htaccesstools.com/htpasswd-generator/