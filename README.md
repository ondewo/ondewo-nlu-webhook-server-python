<div align="center">
  <table>
    <tr>
      <td>
        <a href="https://ondewo.com/en/products/natural-language-understanding/">
            <img width="400px" src="https://raw.githubusercontent.com/ondewo/ondewo-logos/master/ondewo_we_automate_your_phone_calls.png"/>
        </a>
      </td>
    </tr>
    <tr>
        <td align="center">
          <a href="https://www.linkedin.com/company/ondewo "><img width="40px" src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png"></a>
          <a href="https://www.facebook.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
          <a href="https://twitter.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733579.png"> </a>
          <a href="https://www.instagram.com/ondewo.ai/"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/174/174855.png"></a>
        </td>
    </tr>
  </table>
  <h1>
  ONDEWO NLU Webhook Server Python
  </h1>
</div>

## Introduction

This repository contains a template to create the webhook server `ondewo-nlu-webhook-server-python`. The server is set
up to receive json-formatted `POST` messages from `ondewo-nlu-cai` when an intent is matched for which the webhook call
is activated.

An example use-case would be a database query for parameter values, which are then sent back to `ondewo-nlu-cai`, or
overwriting specific responses when a certain intent is active.

There are 2 cases for which the webhook call is used:

1. **slot filling** to update contexts and parameter values

2. **response refinement** to update responses, contexts and parameter values

For details on these cases and integration of custom code, refer to the section on **custom code** below.

## Requirements / Packages

To install the required python libraries for running the webhook server, use:

> pip install --no-cache-dir -r requirements.txt

or for development

> make setup_developer_environment_locally

# Deploy Webhook Server

### SSL Certificates

The webhook server is built to be deployed using SSL via envoy. The certificate files `cert.pem` and `key.pem` need to
be provided in the folder `configs/ondewo-ingress/ondewo-ingress-envoy/certs`. The envoy configuration file `envoy.yaml`
is provided in the folder `configs/ondewo-ingress/ondewo-ingress-envoy/envoy.yaml`.

A `Makefile` is included in the repository to generate self-signed certificates sufficient for local deployment. To
generate them run the command `make run_ondewo_nlu_webhook_server_create_ssl_certificates` in the repository's root
directory.

### Docker deployment

The easiest way to deploy the server is `docker`. A ready-to-use Dockerfile as well as `docker-compose.yaml` is provided
in the repo.

To start the docker image, run:

> make run_ondewo_nlu_webhook_server_release_in_container

or as daemon

> make run_ondewo_nlu_webhook_server_release_in_container_daemon

This will deploy the server in a docker container at https://127.0.0.1:5678.

### Local deployment

`server/__main__.py` contains the code for the server. (Local) deployment of the server can be done with `uvicorn`:

```python
import uvicorn

uvicorn.run(
    app="ondewo_nlu_webhook_server.server.__main__:app",
    host="0.0.0.0",
    port=50091,
    reload=False,  # Disable reload in production
    log_level="info",  # Reduce log verbosity
    workers=1,  # Use multiple workers for better concurrency
    access_log=False,  # Disable access logs for speed (enable if needed)
)
```

# Get a public IP address for Webhook Server

When working with local webhook servers a public IP address is often required for external services such as , such as
`ondewo-nlu-cai` or `ondewo-aim` to interact with your webhook server. `ngrok` is a powerful tool that creates secure
tunnels to your local machine, allowing you to expose local servers to the public internet.

## Why use ngrok?

Ngrok is an easy-to-use tool that simplifies the process of exposing your local web server to the internet. By using
ngrok, you don't need to worry about setting up a complex cloud infrastructure or a static public IP address. Ngrok
automatically generates a public URL that redirects to your local server.

## Installation and Setup for Windows

Follow these steps to install and set up ngrok on Windows:

1. **Download ngrok**:
    - Go to the [ngrok download page](https://download.ngrok.com/windows?tab=download).
    - Select and download the appropriate version for **Windows**.

2. **Setup ngrok**:
    - Follow the instructions on the official ngrok [Setup Page](https://dashboard.ngrok.com/get-started/setup).

3. **Get Your ngrok Auth Token**:
    - After logging into your ngrok account, go
      to [ngrok's Auth Token page](https://dashboard.ngrok.com/get-started/your-authtoken) to get your unique
      authentication token.

4. **Add Your Auth Token to ngrok**:
    - Open your terminal and run the following command to add the auth token to your ngrok installation:
      ```bash
         ngrok.exe config add-authtoken <MY_AUTHTOKEN>
      ```
    - This command will create a public URL for your local server on port 50091.
5. **Start the ngrok tunnel**: Ngrok generates a random public address in free mode, and it may change each time you
   start a new session.
   This will create a public URL that points to your SSL-encrypted local server.
    - For a local server without SSL encryption:
      ```bash
         ngrok.exe http http://localhost:50091
      ```
      This will create a public URL that points to your local server running without SSL-encryption.
    - For a local server wit SSL encryption:
      ```bash
         ngrok.exe http https://localhost:50091
      ```
      This will create a public URL that points to your SSL-encrypted local server.

## Installation and Setup for Linux

Follow these steps to install and set up ngrok on linux:

1. **Download ngrok**:
    - Go to the [ngrok linux download page](https://download.ngrok.com/linux?tab=download).
    - Select and download the appropriate version for **Linux**.

2. **Setup ngrok**:
    - Follow the instructions on the official ngrok [Setup Page](https://dashboard.ngrok.com/get-started/setup).

3. **Get Your ngrok Auth Token**:
    - After logging into your ngrok account, go
      to [ngrok's Auth Token page](https://dashboard.ngrok.com/get-started/your-authtoken) to get your unique
      authentication token.

4. **Add Your Auth Token to ngrok**:
    - Open your terminal and run the following command to add the auth token to your ngrok installation:
      ```bash
         ngrok config add-authtoken <MY_AUTHTOKEN>
      ```
    - This command will create a public URL for your local server on port 50091.
5. **Start the ngrok tunnel**: Ngrok generates a random public address in free mode, and it may change each time you
   start a new session.
   This will create a public URL that points to your SSL-encrypted local server.
    - For a local server without SSL encryption:
      ```bash
         ./ngrok http http://localhost:50091
      ```
      This will create a public URL that points to your local server running without SSL-encryption.
    - For a local server wit SSL encryption:
      ```bash
         ./ngrok http https://localhost:50091
      ```
      This will create a public URL that points to your SSL-encrypted local server.

# Extend the Webhook Server with Custom Code

Custom code can be added to `ondewo_nlu_webhook_server_custom_integration/custom_integration.py`.

All intents for which the webhook call is activated need to be listed in `active_intents` at the top of the file. Either
the `displayName` or the `intent ID` can be specified. Both `slot_filling()` and `response_refinement()` will not be
called if the intent name is not found in the list. In this case the request message will be relayed back without
changes, with the relevant fields of the request copied to the response.

After running either `slot_filling()` or `response_refinement()`, the response message is constructed from the returns
and then validated. If validation fails, a `ValidationError` will be raised.

There are different functionalities available depending on the call:

## slot_filling

Slot filling is called by `ondewo-nlu-cai` when a webhook call as well as slot filling is activated for a matched
intent. The goal is to supply `ondewo-nlu-cai` with parameter values and additional context information (or context
deletion).
The POST message is sent to `[server-IP]/slot_filling`

The following functionality is available in `slot_filling()` in **CUSTOM_CODE.py**:

- changes to parameter values (global or context-specific)

- changes to active contexts

## response_refinement

Response refinement is called by `ondewo-nlu-cai` when a webhook call is activated for a matched intent. The goal is to
have
a last chance at changing the fulfillment messages that were generated by `ondewo-nlu-cai`. The POST message is sent
to `[server-IP]/response_refinement`.

The following functionality is available in `response_refinement()` in **CUSTOM_CODE.py**:

- changes to fulfillment messages (changes, deletions, additions)

Information about active contexts and parameter values are supplied to the function, but they cannot be changed here.

# Test Webhook Server

The tests are conducted by containerizing the server and sending test requests to it. Apart from the python
packages, `docker` and `docker-compose` need to be available, as well as the `docker` python sdk.

## Docker Deployment During Testing

- **Automatic Server Deployment**: The tests trigger the automatic deployment of the server using Docker. This includes
  building the Docker image and running the server in a container during the test execution.
- **Cleanup**: Once the tests have been executed and passed, the Docker container is stopped, and the associated images
  are removed to ensure a clean environment for future tests.

## Unit and Integration Tests

The file
`[tests/ondewo_nlu_webhook_server/server/test_server_unit.py](tests/ondewo_nlu_webhook_server/server/test_server_unit.py)`
contains unit tests that ensure the proper deployment and functionality of the webhook server. These tests verify that
the server can establish a connection, respond correctly, and handle custom code functionality. The server is
automatically deployed using Docker (build and run) when the tests are executed. After the tests complete successfully,
the container is shut down, and any associated Docker images are removed.

## E2E Tests

The following tests are executed:

1. **`test_server_connection`**:
    - **Purpose**: This test checks whether the server can accept and respond to HTTP requests.
    - **Action**: Sends an HTTP GET request to the server and waits for a response.
    - **Expected Outcome**: The server responds without errors, confirming that the connection is established
      successfully.

2. **`test_custom_code("slot_filling")`**:
    - **Purpose**: This test validates the slot filling functionality of the server by sending a sample POST request to
      the server.
    - **Action**: The test calls the `slot_filling()` function in the **CUSTOM_CODE.py** file.
    - **URL**: `https://localhost:5678/slot_filling`
    - **Expected Outcome**: The server should return the correct response, and the return value of the `slot_filling()`
      function should be validated.

3. **`test_custom_code("response_refinement")`**:
    - **Purpose**: Similar to the `slot_filling` test, this test validates the response refinement functionality of the
      server.
    - **Action**: Sends a sample POST request to the server and validates the return value of the
      `response_refinement()` function in **CUSTOM_CODE.py**.
    - **URL**: `https://localhost:5678/response_refinement`
    - **Expected Outcome**: The server should return the correct response, and the return value of the
      `response_refinement()` function should be validated.
