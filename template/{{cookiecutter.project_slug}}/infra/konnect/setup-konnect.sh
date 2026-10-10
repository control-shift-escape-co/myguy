#!/usr/bin/env bash
# Provision a Kong Konnect AI Gateway control plane for this app.
#
# Needs: KONNECT_TOKEN (personal access token from https://cloud.konghq.com)
#        LLM_API_KEY — the provider key the data plane forwards
# Optional: KONNECT_REGION (default: us), KONNECT_CP_NAME
#
# What it does:
#   1. Creates a Konnect control plane
#   2. Issues a data-plane client certificate (saved to infra/konnect/dp-*.pem)
#   3. Syncs infra/gateway/kong.yaml to the control plane (if `deck` is installed)
#   4. Prints a ready-to-run data-plane docker command — no copy-paste of certs
set -euo pipefail

REGION="${KONNECT_REGION:-us}"
API="https://${REGION}.api.konghq.com/v2"
TOKEN="${KONNECT_TOKEN:?Set KONNECT_TOKEN (cloud.konghq.com → personal access token)}"
CP_NAME="${KONNECT_CP_NAME:-{{ cookiecutter.project_slug }}-ai-gw}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

json_field() { # crude JSON field grab — avoids a jq dependency
  grep -o "\"$2\":\"[^\"]*\"" <<<"$1" | head -1 | cut -d'"' -f4 | sed 's/\\n/\n/g'
}

echo "→ Creating Konnect control plane: $CP_NAME"
RESP=$(curl -sf -X POST "$API/control-planes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$CP_NAME\", \"description\": \"AI Gateway for {{ cookiecutter.project_name }} (myg)\", \"cluster_type\": \"CLUSTER_TYPE_CONTROL_PLANE\"}")
CP_ID=$(json_field "$RESP" "id")
echo "✓ Control plane: $CP_ID"

echo "→ Issuing data-plane client certificate"
CERT_RESP=$(curl -sf -X POST "$API/control-planes/$CP_ID/dp-client-certificates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')
json_field "$CERT_RESP" "cert" > "$HERE/dp-cert.pem"
json_field "$CERT_RESP" "key"  > "$HERE/dp-key.pem"
chmod 600 "$HERE/dp-cert.pem" "$HERE/dp-key.pem"
echo "✓ Certificates saved to infra/konnect/dp-{cert,key}.pem (git-ignored?)"

if command -v deck >/dev/null 2>&1; then
  echo "→ Syncing infra/gateway/kong.yaml to the control plane (decK)"
  : "${LLM_API_KEY:?Set LLM_API_KEY — the provider key Kong forwards to}"
  RENDERED=$(mktemp)
  sed "s|__LLM_API_KEY__|${LLM_API_KEY}|g" "$ROOT/infra/gateway/kong.yaml" > "$RENDERED"
  deck gateway sync "$RENDERED" \
      --konnect-token "$TOKEN" \
      --konnect-addr "https://${REGION}.api.konghq.com" \
      --konnect-control-plane-name "$CP_NAME"
  echo "✓ AI Gateway route + ai-proxy plugin live on $CP_NAME"
else
  cat <<EOF
! decK not found — skipping config sync.
  Install it (https://docs.konghq.com/deck/), then:
    sed "s|__LLM_API_KEY__|\$LLM_API_KEY|g" infra/gateway/kong.yaml > /tmp/kong.rendered.yaml
    deck gateway sync /tmp/kong.rendered.yaml \\
      --konnect-token \$KONNECT_TOKEN \\
      --konnect-addr https://${REGION}.api.konghq.com \\
      --konnect-control-plane-name $CP_NAME
EOF
fi

cat <<EOF

→ Last step — run a data plane so the control plane can serve traffic:

   docker run -d --name kong-dp \\
     -e KONG_ROLE=data_plane \\
     -e KONG_CLUSTER_CERT="\$(cat infra/konnect/dp-cert.pem)" \\
     -e KONG_CLUSTER_CERT_KEY="\$(cat infra/konnect/dp-key.pem)" \\
     -e KONG_LUA_SSL_TRUSTED_CERTIFICATE=system \\
     -e KONG_CLUSTER_CONTROL_PLANE="${CP_ID}.cp0.${REGION}.konghq.com:443" \\
     -e KONG_CLUSTER_TELEMETRY_ENDPOINT="${CP_ID}.tp0.${REGION}.konghq.com:443" \\
     -p 8000:8000 kong:3.9

Then point the agent at it: LLM_BASE_URL=http://localhost:8000/llm
EOF
