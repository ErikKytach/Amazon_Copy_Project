# Parallel production deployment

This configuration runs Erizon independently of an existing site:

- Gunicorn listens only on `127.0.0.1:8011`.
- Nginx exposes this application at `http://89.168.60.56:8001`.
- Code, virtual environment, and SQLite database live under `/srv/erizon`.
- The systemd service has a distinct name: `erizon.service`.

The service intentionally uses one Gunicorn worker because the application
uses SQLite for writes. Do not point it at the other application's database.

On an Ubuntu server, install and enable the supplied files after checking that
ports `8001` and `8011` are unused:

```bash
sudo adduser --system --group --home /srv/erizon erizon
sudo mkdir -p /srv/erizon/app /etc/erizon
sudo chown -R erizon:erizon /srv/erizon

# Upload this project's contents into /srv/erizon/app, then:
sudo -u erizon python3 -m venv /srv/erizon/venv
sudo -u erizon /srv/erizon/venv/bin/pip install --upgrade pip
sudo -u erizon /srv/erizon/venv/bin/pip install -r /srv/erizon/app/requirements.txt
sudo install -o root -g erizon -m 640 deploy/erizon.env.example /etc/erizon/erizon.env
# Edit /etc/erizon/erizon.env and replace DJANGO_SECRET_KEY before continuing.
sudo -u erizon /srv/erizon/venv/bin/python manage.py migrate
sudo -u erizon /srv/erizon/venv/bin/python manage.py collectstatic --noinput

sudo install -o root -g root -m 644 deploy/erizon.service /etc/systemd/system/erizon.service
sudo install -o root -g root -m 644 deploy/nginx-erizon.conf /etc/nginx/sites-available/erizon
sudo ln -s /etc/nginx/sites-available/erizon /etc/nginx/sites-enabled/erizon
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now erizon
sudo systemctl reload nginx
sudo ufw allow 8001/tcp
```

If a domain is available, prefer a separate hostname plus TLS instead of a
raw IP and port. This project uses root-relative paths, so mounting it under
a URL prefix such as `/erizon/` would require application changes.
