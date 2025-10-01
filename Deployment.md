# Deploying a Flask App with HTTPS using Cloudflare and Nginx

Deploying a Flask application with HTTPS involves setting up a web server, configuring DNS, and securing the connection. This guide walks you through deploying a Flask app on a VM, configuring Nginx with Gunicorn, setting up DNS records on Cloudflare, and enabling HTTPS with Let's Encrypt. We'll also cover debugging fixes encountered along the way.

## Prerequisites
- A Flask app running on a VM (e.g., at `http://157.254.189.17/`).
- Cloudflare DNS management for your domain (e.g., `imvickykumar999.dpdns.org`).
- Root access to the VM.

## Step 1: Initial Server Setup
Start by configuring Nginx and Gunicorn to serve your Flask app.

### Create Nginx Configuration
Edit the Nginx configuration file:
```
nano /etc/nginx/sites-available/adk-flask
```
Add the following:
```
server {
    listen 80;
    server_name 157.254.189.17;
    location / {
        proxy_pass http://0.0.0.0:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /static/ {
        alias /home/repo/ADK-Flask/static/;
    }
}
```
Enable the config and test:
```
ln -s /etc/nginx/sites-available/adk-flask /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Create Gunicorn Service
Edit the Gunicorn service file:
```
nano /etc/systemd/system/gunicorn.service
```
Add:
```
[Unit]
Description=Gunicorn instance for ADK-Flask
After=network.target
[Service]
User=root
Group=www-data
WorkingDirectory=/home/repo/ADK-Flask
ExecStart=/home/repo/ADK-Flask/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always
[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```
systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn
```

## Step 2: Configure DNS on Cloudflare
To deploy on `https://adk.imvickykumar999.dpdns.org`, update your DNS records.

### Add A Record
Log into [dash.cloudflare.com](https://dash.cloudflare.com), select `imvickykumar999.dpdns.org`, and go to **DNS > Records**.
Click **Add record** and set:
- **Type**: `A`
- **Name**: `adk`
- **IPv4 address**: `157.254.189.17`
- **Proxy status**: `DNS only` (grey cloud) for initial setup
- **TTL**: `Auto`
Save and wait for propagation. Verify with:
```
nslookup adk.imvickykumar999.dpdns.org
```
or
```
dig adk.imvickykumar999.dpdns.org
```

### Debug Fix: NXDOMAIN Error
If Certbot fails with an NXDOMAIN error (indicating the domain can't be resolved), ensure the A record is correctly added and propagated. Switch Proxy status to `DNS only` temporarily, as Cloudflare's proxy can interfere with Let's Encrypt's HTTP challenge.

## Step 3: Enable HTTPS with Let's Encrypt
Install Certbot and obtain a certificate:
```
apt update
apt install certbot python3-certbot-nginx
certbot --nginx -d adk.imvickykumar999.dpdns.org
```
Follow the prompts, entering your email (e.g., `imvickykumar999@gmail.com`) and agreeing to the Terms of Service. If it fails with a DNS issue, double-check the A record and retry.

### Update Nginx for HTTPS
After Certbot succeeds, certificates are in `/etc/letsencrypt/live/adk.imvickykumar999.dpdns.org/`. Edit the Nginx config:
```
nano /etc/nginx/sites-available/adk-flask
```
Update to:
```
server {
    listen 80;
    server_name adk.imvickykumar999.dpdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name adk.imvickykumar999.dpdns.org;
    ssl_certificate /etc/letsencrypt/live/adk.imvickykumar999.dpdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adk.imvickykumar999.dpdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://0.0.0.0:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/repo/ADK-Flask/static/;
    }
}
```
Test and reload:
```
nginx -t
systemctl reload nginx
```

### Set Up Auto-Renewal
Test renewal:
```
certbot renew --dry-run
```

## Step 4: Final Verification
- Visit `https://adk.imvickykumar999.dpdns.org` to confirm the app is live.
- Optionally, re-enable Cloudflare's proxy (set to `Proxied`) for CDN benefits, as Certbot will handle SSL locally.

## Troubleshooting
- **NXDOMAIN Fix**: Ensure DNS records are correct and propagated.
- **Certbot Failure**: Check firewall settings (open ports 80 and 443) and ensure Nginx is running.
- **Nginx Errors**: Use `nginx -t` to debug config issues.

This setup secures your Flask app with HTTPS and leverages Cloudflare for DNS management. Happy deploying!