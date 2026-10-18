#!/usr/bin/env bash
# famguard bootstrap: copies env, starts the stack, prints next steps.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example"
  echo "==> Edit .env and set TUNNEL_TOKEN (Cloudflare Zero Trust > Networks > Tunnels),"
  echo "==> then point your hostname to http://adguard:3000 and http://portal:8080."
  echo "==> After that run: docker compose --profile live up -d"
  exit 0
fi

echo "==> Starting AdGuard Home + enrollment portal..."
docker compose up -d --build

echo ""
echo "==> AdGuard Home admin UI : http://127.0.0.1:3000  (first visit = setup wizard)"
echo "==> Enrollment portal      : http://127.0.0.1:8080"
echo ""
echo "==> To expose via Cloudflare Tunnel (encrypted, no open ports):"
echo "      docker compose --profile live up -d"
echo "==> Then share https://your-domain with the family — one tap per device."
