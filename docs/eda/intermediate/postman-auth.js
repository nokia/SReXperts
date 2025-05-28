/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

// This script requests Access Token before every request
// that requires token based auth for EDA API
// It should be added to the collection-scoped Pre-Request script


// skip this if we are getting the EDA secret
if (pm.info.requestName === "Get API Access Token") {
    return
}

if (pm.info.requestName === "Get EDA Client Secret") {
    return
}

// fetch the token
console.info("fetching the access token. Invoked by collection pre-request script")
pm.sendRequest(
    {
        url:
            pm.environment.get("API_SERVER") +
            "/core/httpproxy/v1/keycloak/realms/eda/protocol/openid-connect/token",
        method: "POST",
        header: {
            "content-type": "application/x-www-form-urlencoded",
        },
        body: {
            mode: "urlencoded",
            urlencoded: [
                { key: "scope", value: "openid" },
                { key: "client_id", value: "eda" },
                { key: "client_secret", value: pm.environment.get("EDA_CLIENT_SECRET") },
                { key: "grant_type", value: "password" },
                { key: "username", value: pm.environment.get("EDA_USER") },
                {
                    key: "password",
                    value: pm.environment.get("EDA_USER_PW"),
                },
            ],
        },
    },
    function (err, res) {
        if (err) {
            console.log("error", err);
        }
        console.info("setting the TOKEN", res.json().access_token);
        pm.environment.set("TOKEN", res.json().access_token);
    }
)