# Git-based Docker deployment

The server deploys Erizon from GitHub, not from a local upload.

- The repository is cloned to `/srv/erizon/repo`.
- Docker Compose runs Gunicorn on `127.0.0.1:8011`.
- Host Nginx listens on `8001`, serves `/static/` and `/images/`, and proxies Django.
- The existing Caddy proxy on `80` routes `erizon.89.168.60.56.sslip.io` to Nginx.
- A systemd timer runs every minute and redeploys when `origin/main` changes.

The SQLite database is intentionally part of the Docker image. A redeploy from a
new commit recreates the container and uses the committed `db.sqlite3`; runtime
database writes are not preserved across redeploys.

Bootstrap or force a deploy:

```bash
sudo /usr/local/bin/erizon-deploy
```

If `/usr/local/bin/erizon-deploy` is not installed yet:

```bash
sudo adduser --system --group --home /srv/erizon erizon || true
sudo install -d -o erizon -g erizon -m 750 /srv/erizon/repo
sudo -u erizon git clone --branch main https://github.com/ErikKytach/Amazon_Copy_Project.git /srv/erizon/repo
sudo install -o root -g root -m 755 /srv/erizon/repo/amazon/deploy/deploy-from-git.sh /usr/local/bin/erizon-deploy
sudo /usr/local/bin/erizon-deploy
```

Useful status commands:

```bash
systemctl status erizon-git-deploy.timer
systemctl status erizon-git-deploy.service
docker compose -p erizon -f /srv/erizon/repo/amazon/compose.yaml ps
```
