#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using the Cisco Meraki REST API to create/update
webhooks. The webhook data is read in from a JSON file,
and this script automatically trigger test webhooks.
"""

import sys
import time
import json
from meraki_helpers import get_devnet_network_id, req


def main(net_name):
    """
    Execution begins here.
    """

    # Find the network ID for our reserved instance
    net_id = get_devnet_network_id(net_name)

    # Load in the webhooks to add from the JSON file
    with open("add_webhooks.json", "r") as handle:
        webhooks = json.load(handle)

    # For each webhook to add
    for webhook in webhooks:

        # Add each webhook server individually
        print(f"adding webhook '{webhook['name']}'")
        if not webhook["url"].lower().startswith("https"):
            print(" url is not 'https', skipping")
            continue
        add_http = req(
            f"networks/{net_id}/httpServers", method="post", json=webhook
        ).json()

        # Print JSON structure of response for troubleshooting
        # print(json.dumps(add_http, indent=2))

        # Send a test webhook to each server based on URL
        # after waiting a few seconds to reduce race condition likelihood
        print(f"testing webhook '{webhook['name']}'")
        test_http = req(
            f"networks/{net_id}/httpServers/webhookTests",
            method="post",
            json={"url": webhook["url"]},
        ).json()

        # Ensure the webhooks are enqueued (ie, started successfully)
        if test_http["status"] != "enqueued":
            raise ValueError("webhook creation failed: {test_http['status']}")

        # Wait until the state changes from "enqueued"
        while test_http["status"] == "enqueued":

            # Print JSON structure of response for troubleshooting
            # print(json.dumps(test_http, indent=2))

            # Rewrite "test_http" to update the status every few seconds
            time.sleep(2)
            test_http = req(
                f"networks/{net_id}/httpServers/webhookTests/{test_http['id']}",
            ).json()

        # The final status should be "delivered"; if not, raise error
        # For additional confirmation, check the webhook receivers too
        if test_http["status"] != "delivered":
            raise ValueError("webhook delivery failed: {test_http['status']}")

    # Collect the current webhooks and print them as confirmation
    net_http = req(f"networks/{net_id}/httpServers").json()
    print(f"Current webhook receivers for {net_name}:")
    print(json.dumps(net_http, indent=2))


if __name__ == "__main__":
    # Ensure there are exactly 2 CLI args (file name, net name)
    if len(sys.argv) != 2:
        print("usage: python build_network.py <net_name>")
        sys.exit(1)

    # Pass in the arguments into main()
    main(sys.argv[1])
