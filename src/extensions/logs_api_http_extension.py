#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import sys
from pathlib import Path
lib_folder = Path(__file__).parent / "lib"
sys.path.insert(0,str(lib_folder))
from logs_api_http_extension.http_listener import http_server_init, RECEIVER_PORT
from logs_api_http_extension.logs_api_client import LogsAPIClient
from logs_api_http_extension.extensions_api_client import ExtensionsAPIClient
from logs_api_http_extension.firehose_agent import Producer
from queue import Queue

class LogsAPIHTTPExtension():
    def __init__(self, agent_name, registration_body, subscription_body):
        print(f"Initializing LogsAPIExternalExtension {agent_name}")
        self.agent_name = agent_name
        self.queue = Queue()
        self.logs_api_client = LogsAPIClient()
        self.extensions_api_client = ExtensionsAPIClient()

        # Register early so Runtime could start in parallel
        self.agent_id = self.extensions_api_client.register(self.agent_name, registration_body)

        # Start listening before Logs API registration
        http_server_init(self.queue)
        self.logs_api_client.subscribe(self.agent_id, subscription_body)
        delivery_stream = (os.environ['FIREHOSE_DELIVERY_STREAM'])
        self.firehose_agent  = Producer(delivery_stream=delivery_stream)

    def run_forever(self):
        print(f"Serving LogsAPIHTTPExternalExtension {self.agent_name}")
        while True:
            resp = self.extensions_api_client.next(self.agent_id)
            self.firehose_agent.put_records(resp)
            while not self.queue.empty():
                batch = self.queue.get_nowait()
                self.firehose_agent.put_records(batch)

# Register for the INVOKE events from the EXTENSIONS API
_REGISTRATION_BODY = {
    "events": ["INVOKE", "SHUTDOWN"],
}

# Subscribe to platform logs and receive them on ${local_ip}:4243 via HTTP protocol.

TIMEOUT_MS = 1000 # Maximum time (in milliseconds) that a batch would be buffered.
MAX_BYTES = 262144 # Maximum size in bytes that the logs would be buffered in memory.
MAX_ITEMS = 10000 # Maximum number of events that would be buffered in memory.

_SUBSCRIPTION_BODY = {
    "destination":{
        "protocol": "HTTP",
        "URI": f"http://sandbox:{RECEIVER_PORT}",
    },
    "types": ["platform", "function"],
    "buffering": {
        "timeoutMs": TIMEOUT_MS,
        "maxBytes": MAX_BYTES,
        "maxItems": MAX_ITEMS
    }
}

def main():
    print(f"Starting Extensions {_REGISTRATION_BODY} {_SUBSCRIPTION_BODY}")
    # Note: Agent name has to be file name to register as an external extension
    ext = LogsAPIHTTPExtension(os.path.basename(__file__), _REGISTRATION_BODY, _SUBSCRIPTION_BODY)
    ext.run_forever()

if __name__ == "__main__":
    main()
