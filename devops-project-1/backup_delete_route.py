import subprocess
import json

ROUTE_TABLE_ID = "rtb-0123456789abcdef"
DESTINATION = "10.20.0.0/16"


def run_aws_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("AWS CLI command failed:")
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

print(json.dumps(data, indent=4))