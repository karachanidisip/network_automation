import sqlite3
from pathlib import Path


# Paths
NETMIKO_DB_PATH = Path(__file__).resolve().parent / "netmiko_devices.db"
SCRAPLI_DB_PATH = Path(__file__).resolve().parent / "scrapli_devices.db"

class NetmikoDeviceDB:
    TABLE_NAME = "netmiko_devices_table"

    def __init__(self, db_path):
        self.db_path = db_path

    def create_db_and_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                    host TEXT PRIMARY KEY,
                    device_type TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    secret TEXT NOT NULL
                )
            """)
            print("[OK] Database/table ready.")

    def add_device(self, host, device_type, username, password, secret):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR IGNORE INTO {self.TABLE_NAME}
                (host, device_type, username, password, secret)
                VALUES (?, ?, ?, ?, ?)
            """, (host, device_type, username, password, secret))

            if cursor.rowcount == 0:
                print(f"[INFO] Device '{host}' already exists.")
            else:
                print(f"[OK] Device '{host}' inserted.")

    def update_device(self, host, device_type, username, password, secret):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {self.TABLE_NAME}
                SET
                    device_type=?,
                    username=?,
                    password=?,
                    secret=?
                WHERE host=?
            """, (device_type, username, password, secret, host))

            if cursor.rowcount == 0:
                print(f"[INFO] No device '{host}' found.")
            else:
                print(f"[OK] Device '{host}' updated.")

    def delete_device(self, host):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE host=?",
                (host,)
            )

            print("[OK] Deleted." if cursor.rowcount else "[INFO] Device not found.")

    def get_one_device(self, host):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE host=?",
                (host,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_devices(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME}"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_multiple_devices(self, host_list):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            devices = []
            for host in host_list:
                cursor = conn.execute(
                    f"SELECT * FROM {self.TABLE_NAME} WHERE host = ?", (host,)
                )
                devices.extend(dict(row) for row in cursor.fetchall())
            return devices

class ScrapliDeviceDB:
    TABLE_NAME = "scrapli_devices_table"

    def __init__(self, db_path):
        self.db_path = db_path

    def create_db_and_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                    host TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    auth_username TEXT NOT NULL,
                    auth_password TEXT NOT NULL,
                    auth_secondary TEXT NOT NULL
                )
            """)
            print("[OK] Database/table ready.")

    def add_device(self, host, platform, auth_username, auth_password, auth_secondary):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR IGNORE INTO {self.TABLE_NAME}
                (host, platform, auth_username, auth_password, auth_secondary)
                VALUES (?, ?, ?, ?, ?)
            """, (host, platform, auth_username, auth_password, auth_secondary))

            if cursor.rowcount == 0:
                print(f"[INFO] Device '{host}' already exists.")
            else:
                print(f"[OK] Device '{host}' inserted.")

    def update_device(self, host, platform, auth_username, auth_password, auth_secondary):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {self.TABLE_NAME}
                SET
                    platform=?,
                    auth_username=?,
                    auth_password=?,
                    auth_secondary=?
                WHERE host=?
            """, (platform, auth_username, auth_password, auth_secondary, host))

            if cursor.rowcount == 0:
                print(f"[INFO] No device '{host}' found.")
            else:
                print(f"[OK] Device '{host}' updated.")

    def delete_device(self, host):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE host=?",
                (host,)
            )

            print("[OK] Deleted." if cursor.rowcount else "[INFO] Device not found.")

    def get_one_device(self, host):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE host=?",
                (host,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_devices(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME}"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_multiple_devices(self, host_list):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            devices = []
            for host in host_list:
                cursor = conn.execute(
                    f"SELECT * FROM {self.TABLE_NAME} WHERE host = ?", (host,)
                )
                devices.extend(dict(row) for row in cursor.fetchall())
            return devices
