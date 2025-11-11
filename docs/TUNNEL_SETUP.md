# Cloudflare Tunnel Setup

This document outlines the steps to correctly configure the `cloudflared` service in this project.

## Configuration

### `docker-compose.yml`

The `cloudflared` service in `docker-compose.yml` should be configured as follows:

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --config /home/nonroot/.cloudflared/config.yml run
    depends_on:
      - rag
    volumes:
      - /home/mark/.cloudflared:/home/nonroot/.cloudflared:ro
```

### `~/.cloudflared/config.yml`

The `config.yml` file in your `~/.cloudflared` directory should be configured as follows:

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /home/nonroot/.cloudflared/<YOUR_TUNNEL_ID>.json
ingress:
  - hostname: rag.keepbreath.ing
    service: http://rag:8000
  - service: http_status:404
```

### File and Directory Permissions

The permissions on your `~/.cloudflared` directory and its contents are critical. The `cloudflared` container runs as a non-root user, so it needs to be able to read the configuration file and credentials.

- The `~/.cloudflared` directory must have `755` permissions (`drwxr-xr-x`).
- The `config.yml` file must have `644` permissions (`-rw-r--r--`).
- The `<YOUR_TUNNEL_ID>.json` credentials file must have `644` permissions (`-rw-r--r--`).

You can set these permissions with the following commands:

```bash
chmod 755 ~/.cloudflared
chmod 644 ~/.cloudflared/config.yml
chmod 644 ~/.cloudflared/<YOUR_TUNNEL_ID>.json
```
