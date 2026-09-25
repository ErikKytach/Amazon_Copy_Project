#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-erizon}"
APP_HOME="${APP_HOME:-/srv/erizon}"
REPO_DIR="${REPO_DIR:-$APP_HOME/repo}"
REPO_URL="${REPO_URL:-https://github.com/ErikKytach/Amazon_Copy_Project.git}"
BRANCH="${BRANCH:-main}"
PROJECT_DIR="$REPO_DIR/amazon"
DEPLOYED_REVISION_FILE="$APP_HOME/.deployed-revision"
PUBLIC_HOST="${PUBLIC_HOST:-erizon.89.168.60.56.sslip.io}"
PUBLIC_IP="${PUBLIC_IP:-89.168.60.56}"
APP_PORT="${APP_PORT:-8001}"
GUNICORN_PORT="${GUNICORN_PORT:-8011}"
CHECK_ONLY=false
REF="${1:-origin/$BRANCH}"

if [ "${1:-}" = "--if-changed" ]; then
    CHECK_ONLY=true
    REF="${2:-origin/$BRANCH}"
fi

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Run as root, for example: sudo $0 $*" >&2
        exit 1
    fi
}

upsert_env() {
    local key="$1"
    local value="$2"
    local file="$3"

    if grep -q "^${key}=" "$file"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    else
        printf '%s=%s\n' "$key" "$value" >> "$file"
    fi
}

ensure_user_and_dirs() {
    if ! id -u "$APP_USER" >/dev/null 2>&1; then
        adduser --system --group --home "$APP_HOME" "$APP_USER"
    fi

    install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$APP_HOME"
    install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$APP_HOME/backups"
    install -d -o root -g "$APP_USER" -m 750 /etc/erizon
}

ensure_env() {
    local env_file="/etc/erizon/erizon.env"

    if [ ! -f "$env_file" ]; then
        {
            printf 'DJANGO_SETTINGS_MODULE=amazon.production_settings\n'
            printf 'DJANGO_SECRET_KEY=%s\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
            printf 'DJANGO_ALLOWED_HOSTS=%s,%s\n' "$PUBLIC_IP" "$PUBLIC_HOST"
            printf 'DJANGO_SECURE_SSL_REDIRECT=false\n'
            printf 'DJANGO_SESSION_COOKIE_SECURE=false\n'
            printf 'DJANGO_CSRF_COOKIE_SECURE=false\n'
        } > "$env_file"
        chown root:"$APP_USER" "$env_file"
        chmod 640 "$env_file"
    else
        upsert_env "DJANGO_SETTINGS_MODULE" "amazon.production_settings" "$env_file"
        upsert_env "DJANGO_ALLOWED_HOSTS" "$PUBLIC_IP,$PUBLIC_HOST" "$env_file"
        upsert_env "DJANGO_SECURE_SSL_REDIRECT" "false" "$env_file"
        upsert_env "DJANGO_SESSION_COOKIE_SECURE" "false" "$env_file"
        upsert_env "DJANGO_CSRF_COOKIE_SECURE" "false" "$env_file"
        chown root:"$APP_USER" "$env_file"
        chmod 640 "$env_file"
    fi
}

ensure_repo() {
    if [ ! -d "$REPO_DIR/.git" ]; then
        if [ -e "$REPO_DIR" ] && find "$REPO_DIR" -mindepth 1 -print -quit | grep -q .; then
            mv "$REPO_DIR" "$APP_HOME/backups/repo.$(date +%Y%m%d%H%M%S)"
        fi

        install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$REPO_DIR"
        rmdir "$REPO_DIR"
        sudo -u "$APP_USER" git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
    fi

    sudo -u "$APP_USER" git -C "$REPO_DIR" remote set-url origin "$REPO_URL"
    sudo -u "$APP_USER" git -C "$REPO_DIR" fetch --prune origin "+refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"
}

checkout_revision() {
    local target_revision
    target_revision="$(sudo -u "$APP_USER" git -C "$REPO_DIR" rev-parse "$REF")"

    if [ "$CHECK_ONLY" = true ] && [ -f "$DEPLOYED_REVISION_FILE" ] && [ "$(cat "$DEPLOYED_REVISION_FILE")" = "$target_revision" ]; then
        echo "Already deployed $target_revision"
        exit 0
    fi

    sudo -u "$APP_USER" git -C "$REPO_DIR" reset --hard "$target_revision"
    sudo -u "$APP_USER" git -C "$REPO_DIR" clean -fd -e amazon/staticfiles
    install -d -o "$APP_USER" -g "$APP_USER" -m 775 "$PROJECT_DIR/staticfiles"
    printf '%s\n' "$target_revision" > "$DEPLOYED_REVISION_FILE.next"
}

install_nginx_config() {
    install -o root -g root -m 644 "$PROJECT_DIR/deploy/nginx-erizon.conf" /etc/nginx/sites-available/erizon
    ln -sfn /etc/nginx/sites-available/erizon /etc/nginx/sites-enabled/erizon
    rm -f /etc/nginx/sites-enabled/default
    usermod -aG "$APP_USER" www-data || true
    nginx -t
}

disable_legacy_service() {
    if systemctl list-unit-files erizon.service >/dev/null 2>&1; then
        systemctl disable --now erizon.service || true
    fi
}

deploy_container() {
    disable_legacy_service
    docker compose -p erizon -f "$PROJECT_DIR/compose.yaml" up -d --build --force-recreate --remove-orphans
}

install_timer_units() {
    install -o root -g root -m 755 "$PROJECT_DIR/deploy/deploy-from-git.sh" /usr/local/bin/erizon-deploy
    install -o root -g root -m 644 "$PROJECT_DIR/deploy/erizon-git-deploy.service" /etc/systemd/system/erizon-git-deploy.service
    install -o root -g root -m 644 "$PROJECT_DIR/deploy/erizon-git-deploy.timer" /etc/systemd/system/erizon-git-deploy.timer
    systemctl daemon-reload
    systemctl enable --now erizon-git-deploy.timer
}

healthcheck() {
    systemctl enable --now nginx
    systemctl reload nginx

    for _ in $(seq 1 30); do
        if curl -fsS -H "Host: $PUBLIC_HOST" "http://127.0.0.1:${APP_PORT}/en/" >/dev/null; then
            return 0
        fi
        sleep 2
    done

    echo "Health check failed for http://127.0.0.1:${APP_PORT}/en/" >&2
    docker compose -p erizon -f "$PROJECT_DIR/compose.yaml" logs --tail 80 web >&2 || true
    return 1
}

main() {
    require_root "$@"
    ensure_user_and_dirs
    ensure_env
    ensure_repo
    checkout_revision
    install_timer_units
    install_nginx_config
    deploy_container
    healthcheck
    mv "$DEPLOYED_REVISION_FILE.next" "$DEPLOYED_REVISION_FILE"
    echo "Deployed $(cat "$DEPLOYED_REVISION_FILE")"
}

main "$@"
