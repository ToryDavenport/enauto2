#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using the Cisco Meraki REST API to collect video
footage from MV sense cameras.
"""

import sys
import time
import requests
from meraki_helpers import get_network_id, req


def main(org_name, net_name):
    """
    Execution begins here.
    """

    # Find the network ID for the specified org and network
    net_id = get_network_id(net_name, org_name)

    # Collect a list of cameras within this network
    cameras = req(f"networks/{net_id}/devices").json()

    # Print the list of cameras collected
    # import json; print(json.dumps(cameras, indent=2))

    # Iterate over the cameras collected
    for camera in cameras:
        sn = camera["serial"]

        # Get the live video link. Note that accessing this link requires
        # you to log into the Meraki dashboard
        video_link = req(f"networks/{net_id}/cameras/{sn}/videoLink").json()

        # Print the retrieved video link response
        # import json; print(json.dumps(video_link, indent=2))
        print(f"Video link for camera {sn}:\n{video_link['url']}")

        # TODO need to figure out a smart timestamp approach
        timestamp = None
        if timestamp:
            params = {"timestamp": timestamp}
        else:
            params = None

        # Generate a new snapshot at the given timestamp, or if one isn't
        # specified, at the current time
        snapshot_link = req(
            f"networks/{net_id}/cameras/{sn}/snapshot",
            method="post",
            params=params,
        ).json()

        # Print the retrieved snapshot link response
        # import json; print(json.dumps(snapshot_link, indent=2))

        # It takes some time for the snapshot to be available, usually
        # 2 seconds, so wait for a short time until the process completes
        time.sleep(5)

        # Perform a low-level GET request to the snapshot URL which does not
        # use the Meraki dashboard API, nor does it require authentication.
        image = requests.get(snapshot_link["url"])
        image.raise_for_status()

        # Open a new jpg file for writing bytes (not text) and includ
        # the HTTP content as bytes (not text)
        # TODO need to create this directory first
        with open(f"camera_snapshots/{sn}.jpg", "wb") as handle:
            handle.write(image.content)

        print(f"Snapshot for camera {sn} saved")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python splash.py <org_name> <net_name>")
        sys.exit(1)

    # Pass in the arguments into main()
    main(sys.argv[1], sys.argv[2])
    # python cameras.py "Loop Free Consulting" "Home Camera"
