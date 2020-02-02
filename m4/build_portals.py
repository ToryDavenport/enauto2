#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using the Cisco Meraki REST API to create/update
external captive portal (excap) settings on Meraki SSIDs.
"""

import json
import sys
from meraki_helpers import get_network_id, req


def main(org_name, net_name):
    """
    Execution begins here.
    """

    # Find the network ID for our reserved instance (or personal org)
    net_id = get_network_id(net_name, org_name)

    with open("add_portals.json", "r") as handle:
        portals = json.load(handle)

    for ssid_number, body in portals.items():

        # Assemble the SSID base URL and the HTTP PUT request payload
        ssid_base = f"networks/{net_id}/ssids/{ssid_number}"

        # Issue the PUT request to update the SSID general parameters
        print(f"Updating SSID {ssid_number} for {body['ssid_body']['name']}")
        update_ssid = req(ssid_base, method="put", json=body["ssid_body"])

        # Debugging statement to check the updated SSID information
        # print(json.dumps(update_ssid.json(), indent=2))

        # Issue the PUT request to update the splash page parameters if they exist
        if body["splash_body"]:
            print(f"Update SSID {ssid_number} excap to {body['splash_body']['splashUrl']}")
            update_splash = req(
                f"{ssid_base}/splashSettings", method="put", json=body["splash_body"]
            )

        # Debugging statement to check the updated splash information
        # print(json.dumps(update_splash.json(), indent=2))


if __name__ == "__main__":
    # Ensure there are exactly 3 CLI args (file name, org name, net name)
    if len(sys.argv) != 3:
        print("usage: python splash.py <org_name> <net_name>")
        sys.exit(1)

    # Pass in the arguments into main()
    main(sys.argv[1], sys.argv[2])
    # python splash.py "Loop Free Consulting" "Home Wireless"
