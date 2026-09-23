import subprocess
import json
import sys

ROUTE_TABLE_ID = "rtb-02d387dc62f227b9e"
BACKUP_FILE = "backup.json"


def run_aws_command(command):
    """Run AWS CLI command and return JSON output."""
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            return json.loads(result.stdout)

        return None

    except subprocess.CalledProcessError as error:
        print("AWS CLI command failed:")
        print(error.stderr)
        sys.exit(1)


def backup_route_table():
    print("Getting route table information...")

    command = [
        "aws",
        "ec2",
        "describe-route-tables",
        "--route-table-ids",
        ROUTE_TABLE_ID,
        "--output",
        "json"
    ]

    data = run_aws_command(command)

    if not data["RouteTables"]:
        print("Route table not found.")
        sys.exit(1)

    route_table = data["RouteTables"][0]

    backup = {
        "vpc_id": route_table["VpcId"],
        "routes": route_table.get("Routes", []),
        "associations": route_table.get("Associations", [])
    }

    with open(BACKUP_FILE, "w") as file:
        json.dump(backup, file, indent=4)

    print(f"Backup created: {BACKUP_FILE}")


def delete_route_table():
    print(f"Deleting route table: {ROUTE_TABLE_ID}")

    command = [
        "aws",
        "ec2",
        "delete-route-table",
        "--route-table-id",
        ROUTE_TABLE_ID
    ]

    run_aws_command(command)

    print("Route table deleted successfully.")


def restore_route_table():
    print("Reading backup...")

    try:
        with open(BACKUP_FILE, "r") as file:
            backup = json.load(file)

    except FileNotFoundError:
        print("backup.json not found.")
        sys.exit(1)

    vpc_id = backup["vpc_id"]

    print(f"Creating new route table in VPC: {vpc_id}")

    command = [
        "aws",
        "ec2",
        "create-route-table",
        "--vpc-id",
        vpc_id,
        "--output",
        "json"
    ]

    result = run_aws_command(command)

    new_route_table_id = result["RouteTable"]["RouteTableId"]

    print(f"New Route Table ID: {new_route_table_id}")

    # Restore routes
    for route in backup["routes"]:

        destination = route.get("DestinationCidrBlock")

        # Skip AWS-managed local route
        if destination == vpc_cidr_from_backup(backup):
            print("Skipping local route.")
            continue

        command = [
            "aws",
            "ec2",
            "create-route",
            "--route-table-id",
            new_route_table_id
        ]

        if "DestinationCidrBlock" in route:
            command.extend([
                "--destination-cidr-block",
                route["DestinationCidrBlock"]
            ])

        elif "DestinationIpv6CidrBlock" in route:
            command.extend([
                "--destination-ipv6-cidr-block",
                route["DestinationIpv6CidrBlock"]
            ])

        # Restore target
        if "GatewayId" in route:
            command.extend([
                "--gateway-id",
                route["GatewayId"]
            ])

        elif "NatGatewayId" in route:
            command.extend([
                "--nat-gateway-id",
                route["NatGatewayId"]
            ])

        elif "NetworkInterfaceId" in route:
            command.extend([
                "--network-interface-id",
                route["NetworkInterfaceId"]
            ])

        elif "InstanceId" in route:
            command.extend([
                "--instance-id",
                route["InstanceId"]
            ])

        elif "VpcPeeringConnectionId" in route:
            command.extend([
                "--vpc-peering-connection-id",
                route["VpcPeeringConnectionId"]
            ])

        elif "TransitGatewayId" in route:
            command.extend([
                "--transit-gateway-id",
                route["TransitGatewayId"]
            ])

        elif "EgressOnlyInternetGatewayId" in route:
            command.extend([
                "--egress-only-internet-gateway-id",
                route["EgressOnlyInternetGatewayId"]
            ])

        else:
            print(f"Skipping unsupported route: {route}")
            continue

        try:
            run_aws_command(command)
            print(f"Restored route: {destination}")

        except SystemExit:
            print(f"Could not restore route: {destination}")

    # Restore subnet associations
    for association in backup["associations"]:

        subnet_id = association.get("SubnetId")

        if not subnet_id:
            continue

        command = [
            "aws",
            "ec2",
            "associate-route-table",
            "--route-table-id",
            new_route_table_id,
            "--subnet-id",
            subnet_id
        ]

        run_aws_command(command)

        print(f"Associated subnet: {subnet_id}")

    print()
    print("Route table restoration completed.")
    print(f"New Route Table ID: {new_route_table_id}")


def vpc_cidr_from_backup(backup):
    """
    The local route normally matches the VPC CIDR.
    This function is intentionally simple for the beginner lab.
    """

    for route in backup["routes"]:
        if route.get("GatewayId") == "local":
            return route.get("DestinationCidrBlock")

    return None


def main():

    print()
    print("================================")
    print(" AWS Route Table Manager")
    print("================================")
    print()
    print("1. Backup and Delete Route Table")
    print("2. Restore Route Table")
    print("3. Exit")
    print()

    choice = input("Enter your choice: ")

    if choice == "1":

        confirmation = input(
            "WARNING: This will delete the route table. "
            "Continue? (yes/no): "
        )

        if confirmation.lower() == "yes":
            backup_route_table()
            delete_route_table()
        else:
            print("Operation cancelled.")

    elif choice == "2":
        restore_route_table()

    elif choice == "3":
        print("Exiting.")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()