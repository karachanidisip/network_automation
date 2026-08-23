from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH


def main():
    device_db = NetmikoDeviceDB(NETMIKO_DB_PATH)
    device_db.create_db_and_table()

    while True:
        print("""
1. Add device
2. Update device
3. Delete device
4. Get one device
5. Get all devices
6. Get multiple devices
7. Exit
""")

        try:
            choice = int(input("Choice: "))
        except ValueError:
            print("Enter a number.")
            continue

        if choice == 1:
            device_db.add_device(
                input("Host: ").strip(),
                input("Device type: ").strip(),
                input("Username: ").strip(),
                input("Password: ").strip(),
                input("Secret: ").strip(),
            )

        elif choice == 2:
            host = input("Host to update: ").strip()
            device_db.update_device(
                host,
                input("Device type: ").strip(),
                input("Username: ").strip(),
                input("Password: ").strip(),
                input("Secret: ").strip(),
            )

        elif choice == 3:
            device_db.delete_device(input("Host: ").strip())

        elif choice == 4:
            print(device_db.get_one_device(input("Host: ").strip()))

        elif choice == 5:
            for d in device_db.get_all_devices():
                print(d)

        elif choice == 6:
            hosts_input = input("Hosts (comma-separated): ").strip()
            host_list = []
            for h in hosts_input.split(","):
                h = h.strip()
                if h and h not in host_list:
                    host_list.append(h)
            for d in device_db.get_multiple_devices(host_list):
                print(d)

        elif choice == 7:
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()


"""
### DEVICES DB ###
NetmikoDeviceDB(NETMIKO_DB_PATH).create_db_and_table()

NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.1", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.2", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.3", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.4", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.5", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.6", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.7", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.8", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.9", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.10", "cisco_ios_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.11", "cisco_xr_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.12", "cisco_xr_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.13", "cisco_xr_telnet", "AUTO", "PASS", "SECRET")
NetmikoDeviceDB(NETMIKO_DB_PATH).add_device("10.0.0.14", "cisco_xr_telnet", "AUTO", "PASS", "SECRET")
"""
