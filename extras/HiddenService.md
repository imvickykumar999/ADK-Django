# 🔒 Summary: Hosting Django on Tor

This workflow assumes your Django project is running via **Gunicorn on port 8000** and that Nginx is already installed and set up for your public domain.

### 1\. Prerequisite: Install Tor

Ensure the Tor daemon is installed on your server.

| Command | Purpose |
| :--- | :--- |
| `sudo apt update` | Update package list. |
| `sudo apt install tor` | Install the Tor daemon. |

-----

### 2\. Configure Tor Hidden Service

We need to tell the Tor service where to find its private keys and where to forward the decrypted `.onion` traffic (to Nginx's internal HTTP port 80).

**File:** `/etc/tor/torrc`

| Command | Purpose |
| :--- | :--- |
| `sudo nano /etc/tor/torrc` | Open the config file. |
| `sudo cat /home/repo/vickyme6ywivszfs6c2oekjxgatrl7xykwsc355llydysuj7eexokfyd.onion/hostname` | **Get the `.onion` address** (save this address). |

**Content to Add/Verify in `/etc/tor/torrc`:**

```ini
# --- Hidden Service Configuration ---
# Use the directory containing the hostname and key files:
HiddenServiceDir /home/repo/vickyme6ywivszfs6c2oekjxgatrl7xykwsc355llydysuj7eexokfyd.onion/
# Forward virtual port 80 (Tor traffic) to Nginx's local port 80
HiddenServicePort 80 127.0.0.1:80
```

-----

### 3\. Configure Nginx for the Onion Address

We must add a new `server` block to Nginx to handle traffic specifically coming from the Tor service (which arrives locally on port 80).

**File:** `/etc/nginx/sites-available/adk-django`

| Command | Purpose |
| :--- | :--- |
| `sudo nano /etc/nginx/sites-available/adk-django` | Open the Nginx config file. |

**Final Nginx Configuration (Full Content):**

```nginx
server {
    # Redirects all HTTP traffic for the public domain to HTTPS.
    listen 80;
    server_name adkweb.imvickykumar999.dpdns.org;
    return 301 https://$host$request_uri;
}

# --- TOR HIDDEN SERVICE BLOCK (HTTP over port 80) ---
server {
    # Listen on port 80 for traffic coming from the Tor service
    listen 80; 
    
    # Use the specific Onion address as the server name (e.g., vickyme6yw...)
    server_name vickyme6ywivszfs6c2oekjxgatrl7xykwsc355llydysuj7eexokfyd.onion;

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
        proxy_set_header X-Forwarded-Proto http; 
    }
}


# --- PUBLIC INTERNET BLOCK (HTTPS over port 443) ---
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

-----

### 4\. Correct the Tor Service File

This was the biggest roadblock. We had to fix the Systemd definition to run the actual Tor daemon instead of the dummy service.

**File:** `/lib/systemd/system/tor.service`

| Command | Purpose |
| :--- | :--- |
| `sudo nano /lib/systemd/system/tor.service` | Open the Tor service file. |

**Key Lines to Verify/Set in `/lib/systemd/system/tor.service`:**
*Note: Make sure to remove the unsupported `--defaults-path` option.*

```ini
[Unit]
Description=Anonymizing overlay network for TCP
# ...

[Service]
Type=simple
User=debian-tor
Group=debian-tor
# CORRECTED: Runs the Tor binary, pointing to the config file
ExecStart=/usr/bin/tor -f /etc/tor/torrc --RunAsDaemon 0
ExecReload=/bin/kill -HUP $MAINPID
# ...

[Install]
# ...
```

-----

### 5\. Final Commands (The Essential Sequence)

After making all file changes, run this sequence to ensure permissions are right and services are restarted:

| Command | Purpose |
| :--- | :--- |
| `sudo chown -R debian-tor:debian-tor /home/repo/vickyme6ywivszfs6c2oekjxgatrl7xykwsc355llydysuj7eexokfyd.onion/` | **CRITICAL:** Gives Tor permission to read its key files. |
| `sudo chmod 700 /home/repo/vickyme6ywivszfs6c2oekjxgatrl7xykwsc355llydysuj7eexokfyd.onion/` | Sets necessary restrictive permissions. |
| `sudo systemctl daemon-reload` | Reload Systemd to register the corrected `tor.service` file. |
| `sudo nginx -t` | **Verify** Nginx syntax (must succeed before proceeding). |
| `sudo systemctl restart nginx` | Apply the new Nginx Tor configuration. |
| `sudo systemctl restart tor` | Start the fully functional Tor daemon. |
| `sudo systemctl status tor` | Confirm the status is **`Active: active (running)`**. |

Your Django application should now be successfully hosted on Tor\!
