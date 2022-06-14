# Wildcard certificates with SiteHost DNS 

A set of Certbot hooks for SiteHost DNS validation of wildcard LetsEncrypt certificates.

You will need a SiteHost API key for this. You can generate these in the SiteHost Control Panel by following the instructions here: 

https://kb.sitehost.nz/developers/api

# Setup

Create a DNS Zone in the SiteHost control panel for your domain and make sure your SiteHost API key has access to it.

Install CertBot using the instructions for your environment:

https://certbot.eff.org/instructions

Clone the repo and install the python requirements.

```
git clone git@github.com:EvolvedAwesome/sitehost-wildcard-le.git
cd sitehost-wildcard-le
pip3 install -r requirements.txt
```

Edit `dns_change.py` to include your SiteHost API key:

```
def get_api_key():
    # API KEY 
    return "XXXXXXXX"
```

Run CertBot in manual mode and follow the prompts:

```
certbot certonly --preferred-challenges=dns --manual --manual-auth-hook ./create_dns.sh --manual-cleanup-hook ./cleanup_dns.sh -d *.example.com,example.com
```

**Note**: A wildcard certificate `*.example.com` does not include the certificate `example.com`, so you need to generate both together for most purposes.

On successfully running, this will start a daemon to automatically renew your certificate before expiring.

```
> systemctl status snap.certbot.renew.timer
● snap.certbot.renew.timer - Timer renew for snap application certbot.renew
     Loaded: loaded (/etc/systemd/system/snap.certbot.renew.timer; enabled; vendor preset: enabled)
     Active: active (waiting) since xxx; x days ago
    Trigger: xxx
   Triggers: ● snap.certbot.renew.service
```

Then use your newly created certificate in your web services. E.g. for apache

```
<VirtualHost 0.0.0.0:443>
    ...
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/cert.pem
    SSLCertificateChainFile /etc/letsencrypt/live/example.com/fullchain.pem
</VirtualHost> 
```

It's common to symlink or mount the certificates in your application if required:

```
docker run -d -v /etc/letsencrypt/live/example.com:/certs:ro rabbitmq:3
```

or use a TLS terminating proxy like Traefik: 

```
version: '3.0'

services:
  traefik:
    image: traefik:v2.0
    command:
      - --providers.docker
      - --providers.file.directory=/etc/traefik/dynamic
      - --providers.file.watch=true
      - --entryPoints.web.address=:80
      - --entryPoints.websecure.address=:443
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $PWD/certs-traefik.yaml:/etc/traefik/dynamic/certs-traefik.yaml
      - /etc/letsencrypt/live/:/certs:ro 
```

`certs-traefik.yaml`:
```
# Dynamic configuration
tls:
  stores:
    default:
      defaultCertificate:
        certFile: /certs/example.com/cert.crt
        keyFile: /certs/example.com/cert.key
```