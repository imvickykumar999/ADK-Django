# Deploying My Django App with HTTPS

Here’s a summary of the steps I took, reordered for a more logical deployment flow:

## 1\. Setting Up Gunicorn as a Systemd Service

My first step was to configure **Gunicorn** to run the Django application internally on port **8000**. I created a Systemd service file to manage the process, ensuring it starts on boot and restarts if it fails.

**File Path:** `/etc/systemd/system/gunicorn-django.service`

```ini
[Unit]
Description=Gunicorn instance for ADK-Django
After=network.target

[Service]
User=root
Group=www-data
# Setting the working directory to my project root
WorkingDirectory=/home/repo/ADK-Django

# The core command: running Gunicorn from the virtual environment, 
# binding it internally to port 8000, and pointing it to my Django WSGI file.
ExecStart=/home/repo/ADK-Django/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 myadk.wsgi:application

Restart=always

[Install]
WantedBy=multi-user.target
```

After saving the file, I ran `sudo systemctl daemon-reload`, then enabled and started the service: `sudo systemctl enable gunicorn-django.service` and `sudo systemctl start gunicorn-django.service`.

-----

## 2\. Configuring Nginx (Initial HTTP Block) and Obtaining the SSL Certificate with Certbot

Before I could finalize the HTTPS configuration, I needed the certificates. I started by creating an **initial Nginx configuration** that only defined the domain and listened on port 80, which is necessary for Certbot's domain verification.

### Initial Nginx Setup & Certbot Command

After creating the basic Nginx file, I ran the following command. The Certbot Nginx plugin did the heavy lifting:

```bash
sudo certbot --nginx -d adkweb.imvickykumar999.dpdns.org
```

### What Certbot Did for Me:

1.  **Domain Verification:** Certbot temporarily proved I owned the domain using the existing Nginx configuration.
2.  **File Creation:** It generated the certificate files and automatically created the link folder:
      * **`/etc/letsencrypt/live/adkweb.imvickykumar999.dpdns.org`**: This folder was created, containing symbolic links to the necessary certificate files (`fullchain.pem` and `privkey.pem`).
3.  **Automatic Nginx Update:** Crucially, it automatically modified my Nginx configuration file to include the HTTPS server block and point the SSL directives to the newly created certificate paths.

-----

## 3\. Finalizing the Nginx Server Block Configuration

Finally, I reviewed and finalized the Nginx configuration, ensuring it handled static files correctly and proxied requests to the Gunicorn port **8000**.

**Final File Path:** `/etc/nginx/sites-available/adk-django`

```nginx
server {
    # Forced redirect: This block (often added or modified by Certbot) 
    # ensures all HTTP traffic on port 80 goes to HTTPS.
    listen 80;
    server_name adkweb.imvickykumar999.dpdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name adkweb.imvickykumar999.dpdns.org;

    # SSL paths inserted by Certbot
    ssl_certificate /etc/letsencrypt/live/adkweb.imvickykumar999.dpdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adkweb.imvickykumar999.dpdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Serving Django Static Files directly for performance
    location /static/ {
        alias /home/repo/ADK-Django/staticfiles/;
    }

    # Proxying dynamic requests to my Gunicorn service on port 8000
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

After verifying the final configuration, I ran `nginx -t` and `systemctl restart nginx`. My Django application is now fully deployed and secured over HTTPS\!
