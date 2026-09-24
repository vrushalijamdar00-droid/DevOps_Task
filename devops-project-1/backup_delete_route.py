import subprocess
import json

ROUTE_TABLE_ID = "rtb-0ad7b9c996c2e8465"
DESTINATION = "10.20.0.0/16"


def run_aws_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(1)

    return result.stdout


command = [
    "aws",
    "ec2",
    "describe-route-tables",
    "--route-table-ids",
    ROUTE_TABLE_ID,
    "--output",
    "json"
]

output = run_aws_command(command)

data = json.loads(output)

routes = data["RouteTables"][0]["Routes"]

for route in routes:

    destination = (
        route.get("DestinationCidrBlock")
        or route.get("DestinationIpv6CidrBlock")
        or route.get("DestinationPrefixListId")
    )

    if destination == DESTINATION:

        print("Route found:")
        print(json.dumps(route, indent=4))