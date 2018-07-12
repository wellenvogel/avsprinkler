FritzBox 
* always same IP for raspberry
* port forward to 444
* myFritz Konto


Setup SSL certs/lighttpd

openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -config ca.conf -extensions v3_ca -out rootCA.pem
openssl req -new -key device.key -out device.csr
openssl x509 -req -in device.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out device.crt -days 500 -sha256 -extfile <(printf "subjectAltName=DNS:*.myfritz.net")
#use *.myfritz.net for the CommonName
cat device.crt rootCA.pem > bundle.crt

#import rootCA.pem in android (just start a webserver on this dir)
#IOS still to be done
#should work - but does not seem to accept our certificate

Beim Erzeugen des CA-Zertifikates muss ein common name angegeben werden, damit IOS es akzeptiert - siehe https://stackoverflow.com/questions/49422164/how-to-install-self-signed-certificates-in-ios-11
