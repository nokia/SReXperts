#!/bin/bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


export EDA_API_URL="${EDA_API_URL:-https://${INSTANCE_ID}.eda.srexperts.net:443}"
export KC_KEYCLOAK_URL="${EDA_API_URL}/core/httpproxy/v1/keycloak/"
export KC_REALM="master"
export KC_CLIENT_ID="admin-cli"
export KC_USERNAME="${KC_USERNAME:-admin}"
export KC_PASSWORD="${KC_PASSWORD:-SReXperts2026!}"
export EDA_REALM="eda"
export API_CLIENT_ID="eda"

# Get access token
KC_ADMIN_ACCESS_TOKEN=$(curl -sk \
  -X POST "$KC_KEYCLOAK_URL/realms/$KC_REALM/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=$KC_CLIENT_ID" \
  -d "username=$KC_USERNAME" \
  -d "password=$KC_PASSWORD" \
  | jq -r '.access_token')

if [ -z "$KC_ADMIN_ACCESS_TOKEN" ]; then
  echo "Failed to obtain keycloak admin token"
  exit 1
fi


# Fetch all clients in the 'eda-realm'
KC_CLIENTS=$(curl -sk \
  -X GET "$KC_KEYCLOAK_URL/admin/realms/$EDA_REALM/clients" \
  -H "Authorization: Bearer $KC_ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json")

# Get the `eda` client's ID
EDA_CLIENT_ID=$(echo "$KC_CLIENTS" | jq -r ".[] | select(.clientId==\"${API_CLIENT_ID}\") | .id")

if [ -z "$EDA_CLIENT_ID" ]; then
  echo "Client 'eda' not found in realm 'eda-realm'"
  exit 1
fi

# Fetch the client secret
EDA_CLIENT_SECRET=$(curl -sk \
  -X GET "$KC_KEYCLOAK_URL/admin/realms/$EDA_REALM/clients/$EDA_CLIENT_ID/client-secret" \
  -H "Authorization: Bearer $KC_ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  | jq -r '.value')

if [ -z "$EDA_CLIENT_SECRET" ]; then
  echo "Failed to fetch client secret"
  exit 1
fi

echo "$EDA_CLIENT_SECRET"