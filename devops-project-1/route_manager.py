import subprocess


ROUTE_TABLE_ID = "rtb-0123456789abcdef"
DESTINATION = "0.0.0.0/0"
GATEWAY_ID = "igw-0123456789abcdef"


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

    try:
        subprocess.run(command, check=True)
        print("Route deleted successfully.")

    except subprocess.CalledProcessError:
        print("Failed to delete route.")


def restore_route():
    command = [
        "aws",
        "ec2",
        "create-route",
        "--route-table-id",
        ROUTE_TABLE_ID,
        "--destination-cidr-block",
        DESTINATION,
        "--gateway-id",
        GATEWAY_ID
    ]

    try:
        subprocess.run(command, check=True)
        print("Route restored successfully.")

    except subprocess.CalledProcessError:
        print("Failed to restore route.")


def main():
    print("Route Table Manager")
    print("-------------------")
    print("1. Delete route")
    print("2. Restore route")

    choice = input("Enter your choice: ")

    if choice == "1":
        delete_route()

    elif choice == "2":
        restore_route()

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()