# EDA REST API

|<nbsp> {: .hide-th .th-full-width } |                                                                          |
| --------------------- | ------------------------------------------------------------------------ |
| **Short Description** | Get to know EDA REST API                                                 |
| **Difficulty**        | Intermediate                                                             |
| **Tools Used**        | Postman                                                                  |
| **Topology Nodes**    | leaf11, leaf12, leaf13, spine11, spine12                                 |
| **References**        | [EDA API Guide][api-guide], [EDA OpenAPI Swagger spec][swagger-spec][^1] |{: .foo}

[api-guide]: https://docs.eda.dev/development/api/
[swagger-spec]: https://github.com/eda-labs/openapi

EDA is an API-first platform where every client, be it the EDA UI, a CLI tool or a higher-level orchestrator talks to EDA via one of its APIs.

The two main north-bound APIs that EDA exposes are EDA REST API and EDA Kubernetes API. With EDA REST API you can write your own automation software or integrate the platform with another system; the API allows to configure all EDA features and components.

In this exercise we will focus on EDA's REST API and use Postman API client to interact with it.

## Objective

The objectives of this challenge are:

- Get to the grips of EDA REST API.
- Find out where API documentation is located and how to use it
- Learn the API authentication process
- Learn how to make API calls using a REST client (Postman in this example)

## Technology Explanation
<!-- --8<-- [start:api-intro] -->
EDA API follows a very similar model as the Kubernetes Resource Model. Every custom resource that gets added through the installation of an App, becomes available through the EDA API in a similar way as custom resources in Kubernetes become available through the Kubernetes API. This model provides that powerful extensibility where a system can be extended on-the-fly, by simply installing the EDA App via the EDA Store, and the app will plug its API to the common API layer of the system.

Based on this, the EDA API may be seen as comprised of the two APIs sets:

1. **Core API**  
    This is the EDA Core system API. Things like Transactions, Alarms, and User management are all part of the this API set.  
    It can not be extended without installing a new version of the EDA Core.
2. **Apps API**  
    Every applications onboarded to the EDA platform (both provided by Nokia or anyone else) will extend the Apps API by adding the applications API to the common API layer.  
    This is how extensibility of the API is achieved in EDA.
<!-- --8<-- [end:api-intro] -->

### API Server

Both Core and Apps API are served by the EDA's API Server implemented as a horizontally scalable `eda-api` deployment running in the EDA's Kubernetes cluster. The API server deployment is exposed via `eda-api` service.

You access the API server using the EDA's external address.

### API Documentation

Detailed information about all of the individual API endpoints and their parameters is available in the OpenAPI (v3) format. The API documentation is provided alongside with your EDA installation and makes is automatically installed with it.

You will find OpenAPI documentation for both EDA Core as well as for every application you have installed in your EDA cluster by using the :octicons-question-24: icon in the top right corner and select API Documentation menu item:

-{{video(url="https://gitlab.com/rdodin/pics/-/wikis/uploads/9cc1e1fa7742e88b6d37292882af14cc/api-web-help.mp4")}}-

When you have the API Documentation UI open, you will find the different applications in the left sidebar. Select an app to browse its API endpoints and the schema for the objects used in the API.

The API documentation UI lists all application, their API endpoints and the details about the requests and responses.

### Authentication

As you would expect, only authorized and authenticated users can make use of the EDA API. For authentication and authorization, EDA uses Keycloak as its backend. Keycloak is a proven and secure solution for Identity and Access management.

The API client directly authenticates with Keycloak, and uses the token received for further API calls to the EDA API. The API client is also responsible for refreshing or renewing their token.

Open a tab with the [authentication docs](https://docs.eda.dev/development/api/#authentication) as you will need it later when we get to running our first API call.

### Sync, Async and Transaction APIs

All REST API endpoints related to the EDA Apps[^2] are being processed by the API server as synchronous requests - a single request when received by the API server will be committed as a transaction and the result will be returned when the transaction is completed. The client, therefore, will be locked until the response is sent by the API server.

To make asynchronous requests, the API clients can use the transaction mechanism provided by the Core API, we often call this set of endpoints - Transaction API.

When using transaction endpoints, a user adds resource/operation objects to the transaction and then commits the transaction. When committing the transaction the client immediately receives the response with the transaction ID, and can proceed doing other work. The client then checks the transaction status by referencing the transaction ID received in the initial response and can react to the status of the transaction.

### Trying Out the API

The API documentation web UI does not only provide a reference to the available APIs and endpoints, but also allows you to run the requests for all available endpoints. The video below shows how to run a `GET` request to fetch configured users in the EDA platform by using the endpoint of the Core API.

-{{video(url="https://gitlab.com/rdodin/pics/-/wikis/uploads/22bb9244757bb1c38a7a4a7d8347b9b4/try-eda-api.mp4")}}-

The request runner in the API documentation web view takes care of the authentication flow on your behalf. You can start running API requests right away.

## Tasks

Now, to turn theory into practice, you will work on a set of tasks that will gradually introduce you to the world of EDA REST API.

/// admonition | Solutions
    type: success
When you get stuck, you can always raise your hand and one of our experts will try to help you out. But if you want to have a look at the solution yourself, you will find the solutions for the API requests in the :material-folder-outline: **__Solutions** folder of the same Postman collection.

The Solutions folder uses the same structure as the root folder.
///

### Install and Setup Postman

We will use Postman as the API client to fire off the requests. If you don't have it installed, make sure to do so by going to the [postman.com/downloads](https://www.postman.com/downloads/) link and selecting the installer for your platform.

When installing Postman you will be asked to login to the Postman.com, you can use any of the existing OpenID providers (google, github). The registration is free and you won't be asked to provide any payment details.

When Postman is installed, grab the Postman Collection that we prepared for this exercise by clicking on this button

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/4909600-0b22527f-4f68-464b-9c74-70c0bb658292?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D4909600-0b22527f-4f68-464b-9c74-70c0bb658292%26entityType%3Dcollection%26workspaceId%3D6bee419c-5db7-440e-a509-f9bb4d460e34#?env%5BHackathon%20instance%5D=W3sia2V5IjoiQVBJX1NFUlZFUiIsInZhbHVlIjoiaHR0cHM6Ly8xMC4xODEuMTMxLjQxOjk0NDMiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCIsInNlc3Npb25WYWx1ZSI6Imh0dHBzOi8vMTAuMTgxLjEzMS40MTo5NDQzIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiJodHRwczovLzEwLjE4MS4xMzEuNDE6OTQ0MyIsInNlc3Npb25JbmRleCI6MH0seyJrZXkiOiJFREFfQ0xJRU5UX1NFQ1JFVCIsInZhbHVlIjoieGoxbkFZWTRMWE9KOUlWMEtWWnppRnY1NE53YWlzNlAiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoic2VjcmV0Iiwic2Vzc2lvblZhbHVlIjoieGoxbkFZWTRMWE9KOUlWMEtWWnppRnY1NE53YWlzNlAiLCJjb21wbGV0ZVNlc3Npb25WYWx1ZSI6InhqMW5BWVk0TFhPSjlJVjBLVlp6aUZ2NTROd2FpczZQIiwic2Vzc2lvbkluZGV4IjoxfSx7ImtleSI6IkVEQV9VU0VSIiwidmFsdWUiOiJhZG1pbiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiYWRtaW4iLCJjb21wbGV0ZVNlc3Npb25WYWx1ZSI6ImFkbWluIiwic2Vzc2lvbkluZGV4IjoyfSx7ImtleSI6IkVEQV9VU0VSX1BXIiwidmFsdWUiOiJhZG1pbiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiYWRtaW4iLCJjb21wbGV0ZVNlc3Npb25WYWx1ZSI6ImFkbWluIiwic2Vzc2lvbkluZGV4IjozfSx7ImtleSI6IlRPS0VOIiwidmFsdWUiOiIiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCIsInNlc3Npb25WYWx1ZSI6IiIsImNvbXBsZXRlU2Vzc2lvblZhbHVlIjoiIiwic2Vzc2lvbkluZGV4Ijo0fSx7ImtleSI6IktDX0FETUlOX1BXIiwidmFsdWUiOiJhZG1pbiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiYWRtaW4iLCJjb21wbGV0ZVNlc3Npb25WYWx1ZSI6ImFkbWluIiwic2Vzc2lvbkluZGV4Ijo1fSx7ImtleSI6IktDX0FETUlOX1RPS0VOIiwidmFsdWUiOiIiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiYW55Iiwic2Vzc2lvblZhbHVlIjoiIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiIiLCJzZXNzaW9uSW5kZXgiOjZ9XQ==)

and selecting the "import a copy" option.

![importcopy](https://gitlab.com/rdodin/pics/-/wikis/uploads/ef5c14f77b30290f8c0ff5a4697db9b2/CleanShot_2025-05-07_at_13.25.43_2x.png){.img-shadow width=60%}

Select your Workspace where you want the collection to be imported in. The prepared collection should be copied to your account and you should see it in your postman application.

#### Environment

In addition to the collection, the environment named "Hackathon instance" that contains the `API_SERVER` variable should appear in the top right corner of the Postman app:

![envpic](https://gitlab.com/rdodin/pics/-/wikis/uploads/05503a8ac4221aab026181e2af4db8c5/CleanShot_2025-05-07_at_14.28.08_2x.png){.img-shadow width=50%}

Make sure to select it.

Then edit the imported environment and change the **Current Value** of the `API_SERVER` variable to match the EDA Web UI address you have been provided with.

This video shows the full process:

-{{video(url="https://gitlab.com/rdodin/pics/-/wikis/uploads/eaa3f138e7b2d0b8aaebdaa08a66ff17/import-collection.mp4")}}-

### Authentication

Now that you have the collection and the environment dialed in, you need to sort the authentication out. Remember, only the authenticated users can leverage the API.

The authentication process boils down to acquiring the API token from the Keycloak service that runs as part of the EDA deployment, but to get the authentication token you first need to get the `client_secret` from Keycloak. Sounds a bit cryptic? Check out the [authentication docs](https://docs.eda.dev/development/api/#authentication) to understand the flow better; there we also explain how to get the `client_secret` using the Keycloak UI.

Once you get the `client_secret` string from Keycloak, set its value in the [Postman Environment](#environment) as the **Current value** of the `EDA_CLIENT_SECRET` variable. Done?

Now to test if you got it all right, execute the :material-folder-outline: **Auth** → **Issue API Access Token** request.

The request should execute without errors, and in the postman output panel you should see various tokens received:

```
{
    "access_token": "somevalue",
    "expires_in": 300,
    "refresh_expires_in": 1800,
    "refresh_token": "somevalue",
    "token_type": "Bearer",
    "id_token": "somevalue",
    "not-before-policy": 0,
    "session_state": "75f07837-51b1-4306-995b-11798fc1b802",
    "scope": "openid profile email"
}
```

This is a typical OpenID/OAuth2.0 response with an access token and auxiliary information. What is important, is that the POST request we just executed has a Post-Request script attached to it, that parses the returned payload and stores the `.access_token` value in the `{{TOKEN}}` variable. That way, every other request in our collection can make use of the acquired token, without specifying the value directly.

### List Users

First "real" task - fetch all users configured in the EDA system.

We have prepared for you the canvas, the :material-folder-outline: **Core** → :material-folder-outline: **Admin** → **Get Users** request in your Postman collection. But it looks a bit empty, the API endpoint URL is missing. Can you fill it in?

/// details | Hint
    type: subtle-question
Use API documentation and look for the EDA Core API. One of its endpoints can show you configured users; you can even find it being displayed in the [video above](#trying-out-the-api).

You need to add authentication and the request URL parts.
///

If you entered the data correctly, you should get a list of users, which normally would contain just the `admin` user, unless you created more:

```json
[
    {
        "uuid": "f2a75035-56a5-4ba0-be9b-53e1351259be",
        "username": "admin",
        "enabled": true,
        "firstName": "EDA",
        "lastName": "admin user",
        "groups": [
            "5aefa9bb-6459-491e-994a-794c9a04a6e3"
        ],
        "status": {
            "lastSuccessfulLogin": "2025-05-07T15:23:29Z"
        }
    }
]
```

Congratulations, you have completed the first task!

### Get Interface

In the previous task you listed all objects of the same kind, to be precise - all users. Now the task is to retrieve the details of a particular Interface object from EDA, namely, `leaf11-ethernet-1-49`.

To complete this task you will use the **Interface** application API, as interfaces are not part of the EDA core, but an extension brought in by the [Interface application](https://docs.eda.dev/apps/interfaces/).

Using the knowledge on how to navigate the API documentation, try to complete the :material-folder-outline: **Interface** → **Interface** request so that the EDA returns everything it knows about the `leaf11-ethernet-1-49`.

/// details | Hint
    type: subtle-question
Interface is a namespaced resource, hence your URL will contain a namespace element in it to target a resource in the namespace. In our hackathon lab we use the default `eda` namespace for everything.
///

### Create Banner

Next challenge. You need to create a new login banner message across all switches in your fabric that will say the following:

```
This device is used in the best workshop ever - the SReXperts Hackathon 2025.
```

A free hint for you - the Banner resource is part of the **Site Information** application. You will find it under its name in the API docs.

In alignment with HTTP verbs adopted by REST, the creation of a new resource is a task for a POST request. Have a look at the API documentation for the Site Information app and focus on the available POST requests. It won't take you long to spot this:

![create-banner](https://gitlab.com/rdodin/pics/-/wikis/uploads/67b3cd5d79ad5417e4c618e19df494ea/CleanShot_2025-05-07_at_20.02.20_2x.png){.img-shadow}

We have prepared for you a blank POST request under the :material-folder-outline: **Site Information** → **Banners** POST request, but this request has an empty body. What to put in?

Again, the answer can be derived from the API documentation site, if you zoom in the POST request body in the API docs UI, you will see that it lists the full body template:

```json
{
  "apiVersion": "siteinfo.eda.nokia.com/v1alpha1",
  "kind": "Banner",
  "metadata": {
    "annotations": {
      "additionalProp1": "string"
    },
    "labels": {
      "additionalProp1": "string"
    },
    "name": "somelongname",
    "namespace": "string"
  },
  "spec": {
    "loginBanner": "string",
    "motd": "string",
    "nodeSelector": [
      "string"
    ],
    "nodes": [
      "string"
    ]
  }
}
```

This JSON blob is templated by the API documentation engine from the OpenAPI specification for this resource, and it can also be seen in the EDA UI if you open the **Site Information** → **Banners** form and try to create the resource in the UI.

Now it is up to you to figure out what to fill in to make the login banner string to be configured on all the switches in our fabric.

If you get all the pieces right, the POST request will return the exact body you submitted in HTTP 201 response, but if something goes wrong, you'll get HTTP 400.

How to ensure that your banner has been provisioned on all of the nodes? You can connect to them via SSH and see the login banner in the terminal, or you can run this [EQL](../beginner/declarative-intents.md#query-interfaces-with-eql):

```
.namespace.node.srl.system.banner
```

![eqlresult](https://gitlab.com/rdodin/pics/-/wikis/uploads/15f4b8fe937655d23eb7955df27354cf/CleanShot_2025-05-08_at_08.22.18_2x.png)

### Create a Transaction

Now, to the real deal. So far we have been working in a synchronous way. Our requests were run-to-completion, with each request getting a response. This works fine for single-shot tasks, but don't sleep on the value the transaction brings to the table.

Transactions shine when:

1. A change set you want to commit spans multiple resources or contains operations of different types (create, update, delete)
2. You want to validate your transaction before trying to apply it
3. Your transaction can take time and you want to make sure the API client can do something else (asynchronous mode)

You are tasked with planning and applying a change that will combine two actions:

1. remove the banner we just added
2. change the description on `leaf11-ethernet-1-49` and `leaf12-ethernet-1-49` interfaces to "description changed via REST API"

Instead of firing off two API requests each targeting one action, we will use the transaction API endpoints to achieve change validation (aka dry run) and asynchronous application.

#### Transaction API

The API endpoints that you are interested in are all part of the EDA Core API set, which you already have looked at when we listed users.

The endpoints of interest are:

- `/core/transaction/v2` - Run a transaction (with or without Dry Run)
- `/core/transaction/v2/result/execution/{transactionId}` - Get the execution details of the posted transaction.

#### Dry Run

The planning part of this change would assume that you want to run a verification step via API to make sure your change set is valid, and only after having a green light from EDA applying the change.

Have a look at the `/core/transaction/v2` API endpoint documentation and its body example:

```json linenums="1" hl_lines="5 22 31 48 68"
{
  "crs": [
    {
      "type": {
        "create": {
          "value": {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
              "annotations": {
                "additionalProp1": "string"
              },
              "labels": {
                "additionalProp1": "string"
              },
              "name": "somevalue",
              "namespace": "string"
            },
            "spec": {}
          }
        },
        "delete": {
          "gvk": {
            "group": "string",
            "kind": "string",
            "version": "string"
          },
          "name": "string",
          "namespace": "string"
        },
        "modify": {
          "value": {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
              "annotations": {
                "additionalProp1": "string"
              },
              "labels": {
                "additionalProp1": "string"
              },
              "name": "somevalue",
              "namespace": "string"
            },
            "spec": {}
          }
        },
        "patch": {
          "patchOps": [
            {
              "from": "string",
              "op": "string",
              "path": "string",
              "value": {},
              "x-permissive": true
            }
          ],
          "target": {
            "gvk": {
              "group": "string",
              "kind": "string",
              "version": "string"
            },
            "name": "string",
            "namespace": "string"
          }
        },
        "replace": {
          "value": {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
              "annotations": {
                "additionalProp1": "string"
              },
              "labels": {
                "additionalProp1": "string"
              },
              "name": "somevalue",
              "namespace": "string"
            },
            "spec": {}
          }
        }
      }
    }
  ],
  "description": "string",
  "dryRun": true,
  "resultType": "string", // normal | debug | errors only
  "retain": true
}
```

The highlighted lines denote different types that the request can contain, and you can easily see how they are mapped to the operations:

- `create`
- `delete`
- `modify`
- `patch`
- `replace`

To remove the Banner you created earlier, you would have use the `delete` operation type and provide group/version/kind of the Banner resource and its name and namespace it is in.

And to change the description of the two Interface resources you could use either `patch`, `modify` or `replace`, they all would work, but have slightly different semantics and purposes.

/// details | Hint
    type: subtle-note
If you will opt in using the `patch` operation type, not that it uses the JSON Patch (RFC 6902) format[^3].

When you use the `modify` operation type, the `value` should contain all required fields of a resource.
///

The Dry Run mode is enabled with the `dryRun` field in the request set to the `true` value; this will result in transaction being synthetically tested by the platform, without touching the network elements.

Can you crack this?[^4]

#### Transaction results

When you run your transaction with or without the Dry Run flag set, you will immediately receive back... Not much. Just a transaction ID.

Why is that? That's the asynchronous pattern and its behavior. You get back the transaction identifier immediately and your client is then free to do whatever, or check the transaction status/results. There are several result providing endpoints, but the one we want you to have a look is:

`/core/transaction/v2/result/execution/{{TX_ID}}`

A call to this endpoint will provide you with the information about the transaction execution results. You will see the changed resources, the nodes that were targeted by this change and much more.

#### Apply

If your dry run has succeeded, you can flip the switch `"dryRun": false` and apply the transaction. It should be applied to your network in an instant.

You can call the transaction results API again or verify it in the EDA UI. You can finish off with checking that the login banner is gone by running the same EQL query we did before.

## Summary

EDA's REST API is a fundamental interface for interacting with the EDA platform programmatically. The abstracted declarative intents (EDA Apps) make it easy to automate complex networks with as little input as possible and a close tie-in with the business requirements. Everything your EDA app has to offer becomes available to the API server.

By completing this challenge you learned a lot of things about EDA API including:

1. **API-First Architecture**: You discovered that EDA is an API-first platform where all clients (UI, CLI tools, orchestrators) interact with EDA through its APIs.

2. **API Structure**: You learned about the two main components of the EDA API:
   - **Core API**: The built-in system API for managing transactions, alarms, topology nodes, and users
   - **Apps API**: Extensible APIs provided by installed applications

3. **Kubernetes-like Resource Model**: You understood how EDA's API follows a similar model to Kubernetes, where custom resources can be added through applications.

4. **Authentication Flow**: You learned how EDA uses Keycloak for authentication and how to obtain and use access tokens for API requests.

5. **Transaction Types**: You explored both synchronous and asynchronous API patterns, including the Transaction API for complex operations.

[^1]: The [eda-labs/openapi][swagger-spec] doc site is a community-supported site with the swagger-based web ui for the openapi specs.
[^2]: These are the ones served under the `${EDA_ADDRESS}/apps/` URL.
[^3]: https://spacelift.io/blog/kubectl-patch-command#how-to-use-the-kubectl-patch-command-with-different-types-of-kubernetes-patching-strategies
[^4]: If you're stuck, ask for help or have a look at the `__Solutions` folder in the collection.
