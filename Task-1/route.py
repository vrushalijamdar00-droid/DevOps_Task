import subprocess
import json
import sys
import os


# ============================================================
# CONFIGURATION
# ============================================================

ROUTE_TABLE_ID = "rtb-09ecaca15d6cd017c"
DESTINATION = "0.0.0.0/0"

BACKUP_FILE = "route_backup.json"

# ============================================================
# RUN AWS CLI COMMAND
# ============================================================

def run_aws_command(command):

    print("\nExecuting:")
    print(" ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print("\nAWS command failed:")
        print(result.stderr)

        return None

    return result.stdout


# ============================================================
# FIND ROUTE
# ============================================================

def find_route():

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

    if output is None:
        return None

    data = json.loads(output)

    route_tables = data.get("RouteTables", [])

    if not route_tables:
        print("Route table not found.")
        return None

    routes = route_tables[0].get("Routes", [])

    for route in routes:

        destination = route.get("DestinationCidrBlock")

        if destination == DESTINATION:

            print("\nRoute found:")
            print(json.dumps(route, indent=4))

            return route

    print(f"\nRoute {DESTINATION} not found.")

    return None


# ============================================================
# BACKUP ROUTE
# ============================================================

def backup_route(route):

    backup_data = {
        "RouteTableId": ROUTE_TABLE_ID,
        "Destination": DESTINATION,
        "Route": route
    }

    with open(BACKUP_FILE, "w") as file:

        json.dump(
            backup_data,
            file,
            indent=4
        )

    print(f"\nBackup created: {BACKUP_FILE}")

    print(
        json.dumps(
            backup_data,
            indent=4
        )
    )

    return True


# ============================================================
# DELETE ROUTE
# ============================================================

def delete_route():

    command = [
        "aws",
        "ec2",
        "delete-route",
        "--route-table-id",
        ROUTE_TABLE_ID,
        "--destination-cidr-block",
        DESTINATION
    ]

    output = run_aws_command(command)

    if output is None:

        print("\nRoute deletion failed.")

        return False

    print("\nRoute deleted successfully.")

    return True


# ============================================================
# VERIFY ROUTE EXISTS
# ============================================================

def route_exists():

    route = find_route()

    if route:

        return True

    return False


# ============================================================
# DELETE WORKFLOW
# ============================================================

def delete_workflow():

    print("\n========================================")
    print("        DELETE ROUTE WORKFLOW")
    print("========================================")

    # Step 1: Find route

    route = find_route()

    if route is None:

        print("\nNothing to delete.")

        return


    # Safety check:
    # Never delete the local route

    if route.get("GatewayId") == "local":

        print("\nERROR:")
        print("This is the VPC local route.")
        print("The script will NOT delete it.")

        return


    # Step 2: Backup

    print("\nCreating route backup...")

    backup_success = backup_route(route)

    if not backup_success:

        print("\nBackup failed.")
        print("Route will NOT be deleted.")

        return


    # Step 3: Confirm backup exists

    if not os.path.exists(BACKUP_FILE):

        print("\nBackup file does not exist.")
        print("Route will NOT be deleted.")

        return


    print("\nBackup verified.")

    # Step 4: Delete

    delete_success = delete_route()

    if not delete_success:

        return


    # Step 5: Verify deletion

    print("\nVerifying route deletion...")

    if route_exists():

        print("\nWARNING:")
        print("Route still exists.")

    else:

        print("\nSUCCESS:")
        print("Route has been deleted.")


# ============================================================
# RESTORE ROUTE
# ============================================================

def restore_route():

    print("\n========================================")
    print("        RESTORE ROUTE WORKFLOW")
    print("========================================")


    # Step 1: Check backup

    if not os.path.exists(BACKUP_FILE):

        print("\nBackup file not found.")

        print(
            f"Create {BACKUP_FILE} by running:"
        )

        print(
            "python3 backup_delete_route.py delete"
        )

        return


    # Step 2: Read backup

    with open(BACKUP_FILE, "r") as file:

        backup_data = json.load(file)


    route = backup_data["Route"]

    route_table_id = backup_data["RouteTableId"]

    destination = route.get("DestinationCidrBlock")


    print("\nBackup information:")

    print(
        json.dumps(
            backup_data,
            indent=4
        )
    )


    # Step 3: Check whether route already exists

    print("\nChecking whether route already exists...")

    existing_route = find_route()

    if existing_route:

        print("\nRoute already exists.")

        print("Restore will NOT create another route.")

        return


    # Step 4: Build restore command

    command = [
        "aws",
        "ec2",
        "create-route",
        "--route-table-id",
        route_table_id,
        "--destination-cidr-block",
        destination
    ]


    # ========================================================
    # Detect original route target
    # ========================================================

    if "GatewayId" in route:

        gateway_id = route["GatewayId"]

        command.extend([
            "--gateway-id",
            gateway_id
        ])


    elif "NatGatewayId" in route:

        nat_gateway_id = route["NatGatewayId"]

        command.extend([
            "--nat-gateway-id",
            nat_gateway_id
        ])


    elif "VpcPeeringConnectionId" in route:

        peering_id = route["VpcPeeringConnectionId"]

        command.extend([
            "--vpc-peering-connection-id",
            peering_id
        ])


    elif "TransitGatewayId" in route:

        transit_gateway_id = route["TransitGatewayId"]

        command.extend([
            "--transit-gateway-id",
            transit_gateway_id
        ])


    elif "NetworkInterfaceId" in route:

        network_interface_id = route["NetworkInterfaceId"]

        command.extend([
            "--network-interface-id",
            network_interface_id
        ])


    else:

        print("\nERROR:")
        print("Unknown route target type.")

        print(
            json.dumps(
                route,
                indent=4
            )
        )

        return


    # Step 5: Restore

    output = run_aws_command(command)

    if output is None:

        print("\nRoute restoration failed.")

        return


    print("\nRoute restored successfully.")


    # Step 6: Verify

    print("\nVerifying route restoration...")

    restored_route = find_route()

    if restored_route:

        print("\n========================================")
        print("       RESTORATION SUCCESSFUL")
        print("========================================")

        print("\nRestored route:")

        print(
            json.dumps(
                restored_route,
                indent=4
            )
        )

    else:

        print("\nWARNING:")
        print("Route was not found after restore.")


# ============================================================
# SHOW ROUTE
# ============================================================

def show_route():

    print("\n========================================")
    print("             CURRENT ROUTE")
    print("========================================")

    route = find_route()

    if route:

        print("\nRoute exists.")

    else:

        print("\nRoute does not exist.")


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) != 2:

        print("\nUsage:")

        print(
            "python3 backup_delete_route.py show"
        )

        print(
            "python3 backup_delete_route.py delete"
        )

        print(
            "python3 backup_delete_route.py restore"
        )

        sys.exit(1)


    action = sys.argv[1]


    if action == "show":

        show_route()


    elif action == "delete":

        delete_workflow()


    elif action == "restore":

        restore_route()


    else:

        print("\nInvalid option.")

        print("\nUse:")

        print(
            "python3 backup_delete_route.py show"
        )

        print(
            "python3 backup_delete_route.py delete"
        )

        print(
            "python3 backup_delete_route.py restore"
        )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()