"""
LABly - Laboratory Reservation and Resource Management System
Console application for students/users and administrators.
"""

from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk


class LABlySystem:
    LAB_INTERVALS = (
        "7:45AM-8:35AM",
        "8:40AM-9:30AM",
        "9:45AM-10:35AM",
        "10:40AM-11:30AM",
        "12:30PM-1:00PM",
        "1:00PM-1:50PM",
        "1:55PM-2:45PM",
        "2:50PM-3:40PM",
        "3:45PM-4:35PM",
    )

    def __init__(self):
        self.users = {}
        self.admins = {
            "admin": {"password": "admin123", "name": "Main Administrator"},
        }

        self.laboratories = [
            {"id": "LAB-001", "name": "Chemistry Laboratory 1", "date": "Every day",
             "time": "All fixed intervals", "capacity": 6, "booked": 0},
            {"id": "LAB-002", "name": "Chemistry Laboratory 2", "date": "Every day",
             "time": "All fixed intervals", "capacity": 6, "booked": 0},
            {"id": "LAB-003", "name": "Computer Laboratory", "date": "Every day",
             "time": "All fixed intervals", "capacity": 6, "booked": 0},
        ]
        self.blocked_laboratory_dates = {}
        self.blocked_laboratory_sessions = {}
        self.equipment = [
            {"id": "EQ-001", "name": "Microscope", "category": "Science",
             "available": 10, "total": 10},
            {"id": "EQ-003", "name": "Digital Multimeter", "category": "Electrical",
             "available": 8, "total": 8},
            {"id": "EQ-004", "name": "Beaker Set", "category": "Science",
             "available": 20, "total": 20},
        ]
        self.reservations = []
        self.accountability = []
        self.logbook = []
        self.next_reservation_id = 1

    @staticmethod
    def pause():
        input("\nPress Enter to continue...")

    @staticmethod
    def read_choice(prompt="Please choose a number: "):
        return input(prompt).strip()

    @staticmethod
    def search_rows(rows, fields):
        keyword = input("\nSearch (leave blank to show all): ").strip().lower()
        if not keyword:
            return rows
        return [
            row for row in rows
            if any(keyword in str(row.get(field, "")).lower() for field in fields)
        ]

    @staticmethod
    def insertion_sort(rows, key=lambda value: str(value).lower(), reverse=False):
        sorted_rows = list(rows)
        for index in range(1, len(sorted_rows)):
            current = sorted_rows[index]
            current_key = key(current)
            position = index - 1

            while position >= 0:
                previous_key = key(sorted_rows[position])
                should_move = previous_key < current_key if reverse else previous_key > current_key
                if not should_move:
                    break
                sorted_rows[position + 1] = sorted_rows[position]
                position -= 1

            sorted_rows[position + 1] = current
        return sorted_rows

    @staticmethod
    def sort_rows(rows, fields):
        print("\nSort by:")
        for index, field in enumerate(fields, 1):
            print(f"{index}. {field.replace('_', ' ').title()}")
        choice = LABlySystem.read_choice("Select field: ")
        if choice.isdigit() and 1 <= int(choice) <= len(fields):
            field = fields[int(choice) - 1]
            direction = LABlySystem.read_choice("1. Ascending  2. Descending: ")
            reverse = direction == "2"
            try:
                return LABlySystem.insertion_sort(
                    rows,
                    key=lambda row: str(row.get(field, "")).lower(),
                    reverse=reverse,
                )
            except AttributeError:
                return rows
        return rows

    def login(self):
        print("\n========================================")
        print("          LABly - Secure Login")
        print("========================================")
        print("1. User")
        print("2. Administrator")

        role_choice = self.read_choice("Select role: ")
        if role_choice == "1":
            role = "user"
        elif role_choice == "2":
            role = "admin"
        else:
            print("Invalid role.")
            return None

        if role == "user":
            accounts = self.users
        else:
            accounts = self.admins

        username = self.read_choice("Username: ").lower()
        password = input("Password: ")

        if username not in accounts or accounts[username]["password"] != password:
            print("Invalid username or password.")
            return None

        print(f"\nLogin successful. Welcome, {accounts[username]['name']} ({role.title()}).")
        return role, username

    def register_user(self):
        print("\n========================================")
        print("          LABly - Create Account")
        print("========================================")

        name = self.read_choice("Full name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        username = self.read_choice("Choose username: ").strip().lower()
        if not username:
            print("Username cannot be empty.")
            return
        if username in self.users:
            print("Username already exists.")
            return

        password = input("Choose password: ")
        confirm_password = input("Confirm password: ")
        if not password:
            print("Password cannot be empty.")
            return
        if password != confirm_password:
            print("Passwords do not match.")
            return

        self.users[username] = {"password": password, "name": name}
        self.add_log(username, "Created a user account")
        print(f"Account created successfully. You can now log in as '{username}'.")

    def add_log(self, username, action):
        self.logbook.append({"username": username, "action": action,
                             "date": "2026-11-24", "time": "09:00"})

    def laboratory_block_reason(self, lab_name, reservation_date, interval=None):
        reason = self.blocked_laboratory_dates.get(("__ALL__", reservation_date))
        if reason:
            return reason
        reason = self.blocked_laboratory_dates.get((lab_name, reservation_date))
        if reason or interval is None:
            return reason
        reason = self.blocked_laboratory_sessions.get(
            ("__ALL__", reservation_date, interval)
        )
        if reason:
            return reason
        return self.blocked_laboratory_sessions.get(
            (lab_name, reservation_date, interval)
        )

    def request_laboratory(self, username):
        print("\n--- Available Laboratory Reservations ---")
        if not self.laboratories:
            print("No laboratories are currently configured.")
            return

        reservation_date = self.read_choice("Reservation date (YYYY-MM-DD): ").strip()
        try:
            date.fromisoformat(reservation_date)
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")
            return

        all_date_block = self.blocked_laboratory_dates.get(("__ALL__", reservation_date))
        if all_date_block:
            print(f"This date is not available for laboratory conduct. Reason: {all_date_block}")
            return

        print("\nSelect laboratory:")
        for index, lab in enumerate(self.laboratories, 1):
            print(f"{index}. {lab['id']} - {lab['name']} (Capacity: {lab['capacity']})")

        lab_choice = self.read_choice("Laboratory number: ")
        if not lab_choice.isdigit() or not 1 <= int(lab_choice) <= len(self.laboratories):
            print("Invalid selection.")
            return
        lab = self.laboratories[int(lab_choice) - 1]

        lab_date_block = self.blocked_laboratory_dates.get(
            (lab["name"], reservation_date)
        )
        if lab_date_block:
            print(f"{lab['name']} is unavailable on this date. Reason: {lab_date_block}")
            return

        print("\nAvailable intervals:")
        for index, interval in enumerate(self.LAB_INTERVALS, 1):
            print(f"{index}. {interval}")

        interval_choice = self.read_choice(
            "Select interval number(s), separated by commas: "
        )
        interval_numbers = [part.strip() for part in interval_choice.split(",")]
        if not interval_numbers or any(
            not number.isdigit() or not 1 <= int(number) <= len(self.LAB_INTERVALS)
            for number in interval_numbers
        ):
            print("Invalid interval selection.")
            return

        selected_intervals = []
        for number in interval_numbers:
            interval = self.LAB_INTERVALS[int(number) - 1]
            if interval not in selected_intervals:
                selected_intervals.append(interval)

        created = []
        skipped = []
        for selected_time in selected_intervals:
            block_reason = self.laboratory_block_reason(
                lab["name"], reservation_date, selected_time
            )
            if block_reason:
                skipped.append(f"{selected_time} (blocked: {block_reason})")
                continue

            duplicate = any(
                reservation["username"] == username
                and reservation["type"] == "Laboratory"
                and reservation["resource"] == lab["name"]
                and reservation["date"] == reservation_date
                and reservation["time"] == selected_time
                for reservation in self.reservations
            )
            if duplicate:
                skipped.append(f"{selected_time} (already reserved)")
                continue

            booked = sum(
                1 for reservation in self.reservations
                if reservation["type"] == "Laboratory"
                and reservation["resource"] == lab["name"]
                and reservation["date"] == reservation_date
                and reservation["time"] == selected_time
            )
            if booked >= lab["capacity"]:
                skipped.append(f"{selected_time} (full)")
                continue

            reservation_id = f"RES-{self.next_reservation_id:04d}"
            self.next_reservation_id += 1
            self.reservations.append({
                "id": reservation_id,
                "username": username,
                "type": "Laboratory",
                "resource": lab["name"],
                "date": reservation_date,
                "time": selected_time,
                "quantity": 1,
                "status": "Requested",
            })
            created.append((reservation_id, selected_time))
            self.add_log(username, f"Requested laboratory reservation {reservation_id}")

        for reservation_id, interval in created:
            print(f"Reservation requested successfully: {reservation_id} | {interval}")
        for reason in skipped:
            print(f"Skipped: {reason}")

    def request_equipment(self, username):
        print("\n--- Request Equipment Reservation ---")
        matches = self.search_rows(self.equipment, ["id", "name", "category"])
        matches = [item for item in matches if item["available"] > 0]
        if not matches:
            print("No matching equipment is available.")
            return

        for index, item in enumerate(matches, 1):
            print(f"{index}. {item['id']} - {item['name']} ({item['category']}) "
                  f"| Available: {item['available']}")

        choice = self.read_choice("Select equipment number: ")
        if not choice.isdigit() or not 1 <= int(choice) <= len(matches):
            print("Invalid selection.")
            return

        quantity_text = self.read_choice("Quantity: ")
        if not quantity_text.isdigit():
            print("Quantity must be a number.")
            return
        quantity = int(quantity_text)
        item = matches[int(choice) - 1]
        if quantity < 1 or quantity > item["available"]:
            print("Invalid quantity.")
            return

        date = self.read_choice("Use date (YYYY-MM-DD): ")
        reservation_id = f"RES-{self.next_reservation_id:04d}"
        self.next_reservation_id += 1
        self.reservations.append({
            "id": reservation_id,
            "username": username,
            "type": "Equipment",
            "resource": item["name"],
            "date": date,
            "time": "Not specified",
            "quantity": quantity,
            "status": "Requested",
        })
        item["available"] -= quantity
        self.add_log(username, f"Requested equipment reservation {reservation_id}")
        print(f"Equipment reservation requested successfully ({reservation_id}).")

    def cancel_reservation(self, username):
        own = [reservation for reservation in self.reservations
               if reservation["username"] == username]
        if not own:
            print("You have no reservations to cancel.")
            return

        print("\n--- Your Reservations ---")
        for reservation in own:
            print(f"{reservation['id']} | {reservation['type']} | "
                  f"{reservation['resource']} | {reservation['date']} | "
                  f"{reservation['status']}")

        reservation_id = self.read_choice("Enter reservation ID to cancel: ").upper()
        reservation = next((item for item in own if item["id"] == reservation_id), None)
        if reservation is None:
            print("Reservation not found.")
            return

        if reservation["type"] == "Equipment":
            item = next((item for item in self.equipment
                         if item["name"] == reservation["resource"]), None)
            if item:
                item["available"] += reservation["quantity"]

        self.reservations.remove(reservation)
        self.add_log(username, f"Cancelled reservation {reservation_id}")
        print("Reservation cancelled.")

    def view_reservations(self, username=None, admin=False):
        rows = self.reservations if admin else [
            row for row in self.reservations if row["username"] == username
        ]
        if not rows:
            print("\nNo reservations found.")
            return

        rows = self.search_rows(rows, ["id", "username", "type", "resource",
                                       "date", "time", "status"])
        rows = self.sort_rows(rows, ["id", "username", "type", "resource",
                                     "date", "time", "status"])
        print("\n--- Reservations ---")
        for reservation in rows:
            print(f"{reservation['id']} | {reservation['username']} | "
                  f"{reservation['type']} | {reservation['resource']} | "
                  f"{reservation['date']} | {reservation['time']} | "
                  f"{reservation['quantity']} | {reservation['status']}")

    def accountability_form(self, username):
        print("\n--- Accountability Form ---")
        name = self.read_choice("Borrower name: ")
        resource = self.read_choice("Resource/equipment borrowed: ")
        quantity_text = self.read_choice("Quantity: ")
        condition = self.read_choice("Condition upon return (Good/Damaged/Missing): ")
        remarks = self.read_choice("Remarks: ")
        if not quantity_text.isdigit():
            print("Quantity must be a number.")
            return

        entry = {
            "username": username,
            "name": name,
            "resource": resource,
            "quantity": int(quantity_text),
            "condition": condition,
            "remarks": remarks,
        }
        self.accountability.append(entry)
        self.add_log(username, f"Submitted accountability for {resource}")
        print("Accountability form submitted.")

    def view_available_resources(self):
        print("\n--- Available Resources ---")
        resources = [
            {**item, "resource_type": "Equipment"}
            for item in self.equipment
        ] + [
            {**lab, "resource_type": "Laboratory",
             "available": lab["capacity"] - lab["booked"]}
            for lab in self.laboratories
        ]
        resources = self.search_rows(resources, ["id", "name", "category",
                                                 "resource_type"])
        resources = self.sort_rows(resources, ["id", "name", "resource_type", "available"])
        for resource in resources:
            print(f"{resource['id']} | {resource['resource_type']} | "
                  f"{resource['name']} | Available: {resource['available']}")

    def view_logbook(self, username=None, admin=False):
        rows = self.logbook if admin else [
            entry for entry in self.logbook if entry["username"] == username
        ]
        if not rows:
            print("\nLogbook is empty.")
            return
        rows = self.search_rows(rows, ["username", "action", "date", "time"])
        rows = self.sort_rows(rows, ["username", "action", "date", "time"])
        print("\n--- Logbook ---")
        for entry in rows:
            print(f"{entry['date']} {entry['time']} | {entry['username']} | "
                  f"{entry['action']}")

    def set_laboratory_reservations(self):
        print("\n--- Set Available Laboratory Reservations ---")
        print("1. Add laboratory schedule")
        print("2. Remove laboratory schedule")
        print("3. Edit laboratory capacity")
        print("4. Block a date or session")
        print("5. Unblock a date or session")
        print("6. View blocked dates and sessions")
        choice = self.read_choice("Select action: ")

        if choice == "1":
            lab_id = self.read_choice("Laboratory ID: ").upper()
            name = self.read_choice("Laboratory name: ")
            capacity_text = self.read_choice("Capacity: ")
            if not capacity_text.isdigit():
                print("Invalid capacity.")
                return
            self.laboratories.append({
                "id": lab_id,
                "name": name,
                "date": "Every day",
                "time": "All fixed intervals",
                "capacity": int(capacity_text),
                "booked": 0,
            })
            print("Laboratory schedule added.")
        elif choice == "2":
            lab_id = self.read_choice("Laboratory ID to remove: ").upper()
            lab = next((item for item in self.laboratories if item["id"] == lab_id), None)
            if lab:
                self.laboratories.remove(lab)
                print("Laboratory schedule removed.")
            else:
                print("Laboratory not found.")
        elif choice == "3":
            lab_id = self.read_choice("Laboratory ID: ").upper()
            lab = next((item for item in self.laboratories if item["id"] == lab_id), None)
            if lab is None:
                print("Laboratory not found.")
                return
            capacity_text = self.read_choice("New capacity: ")
            if not capacity_text.isdigit() or int(capacity_text) < lab["booked"]:
                print("Invalid capacity.")
                return
            lab["capacity"] = int(capacity_text)
            print("Laboratory capacity updated.")
        elif choice == "4":
            blocked_date = self.read_choice("Date to block (YYYY-MM-DD): ").strip()
            try:
                date.fromisoformat(blocked_date)
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD.")
                return

            print("1. Entire day")
            print("2. Specific session")
            block_type = self.read_choice("Select block type: ")
            if block_type not in ("1", "2"):
                print("Invalid block type.")
                return

            print("1. All laboratories")
            for index, lab in enumerate(self.laboratories, 1):
                print(f"{index + 1}. {lab['name']}")
            scope_choice = self.read_choice("Select scope: ")

            if scope_choice == "1":
                scope = "__ALL__"
                scope_name = "All laboratories"
            elif scope_choice.isdigit() and 2 <= int(scope_choice) <= len(self.laboratories) + 1:
                lab = self.laboratories[int(scope_choice) - 2]
                scope = lab["name"]
                scope_name = lab["name"]
            else:
                print("Invalid scope.")
                return

            intervals = None
            if block_type == "2":
                for index, session in enumerate(self.LAB_INTERVALS, 1):
                    print(f"{index}. {session}")
                session_choices = self.read_choice(
                    "Select session number(s), separated by commas: "
                )
                session_numbers = [part.strip() for part in session_choices.split(",")]
                if not session_numbers or any(
                    not number.isdigit()
                    or not 1 <= int(number) <= len(self.LAB_INTERVALS)
                    for number in session_numbers
                ):
                    print("Invalid session selection.")
                    return

                intervals = []
                for number in session_numbers:
                    interval = self.LAB_INTERVALS[int(number) - 1]
                    if interval not in intervals:
                        intervals.append(interval)

            reason = self.read_choice("Reason laboratory cannot be conducted: ").strip()
            if not reason:
                print("Reason cannot be empty.")
                return
            if intervals is None:
                self.blocked_laboratory_dates[(scope, blocked_date)] = reason
                print(f"Blocked {scope_name} for the entire day on {blocked_date}. "
                      f"Reason: {reason}")
            else:
                for interval in intervals:
                    self.blocked_laboratory_sessions[
                        (scope, blocked_date, interval)
                    ] = reason
                    print(f"Blocked {scope_name} session {interval} on {blocked_date}. "
                          f"Reason: {reason}")
        elif choice == "5":
            blocked_date = self.read_choice("Date to unblock (YYYY-MM-DD): ").strip()
            try:
                date.fromisoformat(blocked_date)
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD.")
                return

            print("1. Entire day")
            print("2. Specific session")
            block_type = self.read_choice("Select block type: ")
            if block_type not in ("1", "2"):
                print("Invalid block type.")
                return

            print("1. All laboratories")
            for index, lab in enumerate(self.laboratories, 1):
                print(f"{index + 1}. {lab['name']}")
            scope_choice = self.read_choice("Select scope: ")

            if scope_choice == "1":
                scope = "__ALL__"
                scope_name = "All laboratories"
            elif scope_choice.isdigit() and 2 <= int(scope_choice) <= len(self.laboratories) + 1:
                lab = self.laboratories[int(scope_choice) - 2]
                scope = lab["name"]
                scope_name = lab["name"]
            else:
                print("Invalid scope.")
                return

            if block_type == "1":
                key = (scope, blocked_date)
                blocks = self.blocked_laboratory_dates
                description = f"{scope_name} for the entire day"
            else:
                for index, session in enumerate(self.LAB_INTERVALS, 1):
                    print(f"{index}. {session}")
                session_choices = self.read_choice(
                    "Select session number(s), separated by commas: "
                )
                session_numbers = [part.strip() for part in session_choices.split(",")]
                if not session_numbers or any(
                    not number.isdigit()
                    or not 1 <= int(number) <= len(self.LAB_INTERVALS)
                    for number in session_numbers
                ):
                    print("Invalid session selection.")
                    return

                intervals = []
                for number in session_numbers:
                    interval = self.LAB_INTERVALS[int(number) - 1]
                    if interval not in intervals:
                        intervals.append(interval)

                unblocked = []
                missing = []
                for interval in intervals:
                    key = (scope, blocked_date, interval)
                    if key in self.blocked_laboratory_sessions:
                        del self.blocked_laboratory_sessions[key]
                        unblocked.append(interval)
                    else:
                        missing.append(interval)

                if unblocked:
                    print(f"Unblocked {scope_name} sessions "
                          f"{', '.join(unblocked)} on {blocked_date}.")
                if missing:
                    print(f"No matching block found for: {', '.join(missing)}")
                return

            if key not in blocks:
                print("No matching block found.")
                return
            del blocks[key]
            print(f"Unblocked {description} on {blocked_date}.")
        elif choice == "6":
            print("\n--- Blocked Laboratory Dates and Sessions ---")
            if not self.blocked_laboratory_dates and not self.blocked_laboratory_sessions:
                print("No blocked laboratory dates or sessions.")
                return
            blocked_items = [
                (key, reason, "Entire day")
                for key, reason in self.blocked_laboratory_dates.items()
            ] + [
                ((scope, blocked_date), reason, interval)
                for (scope, blocked_date, interval), reason
                in self.blocked_laboratory_sessions.items()
            ]
            blocked_items = LABlySystem.insertion_sort(
                blocked_items,
                key=lambda item: str(item[0]).lower() + str(item[2]).lower(),
            )
            for (scope, blocked_date), reason, block_period in blocked_items:
                scope_name = "All laboratories" if scope == "__ALL__" else scope
                print(f"{blocked_date} | {scope_name} | {block_period} | "
                      f"Reason: {reason}")
        else:
            print("Invalid action.")

    def set_equipment_reservations(self):
        print("\n--- Set Equipment Reservations ---")
        print("1. Add equipment")
        print("2. Update equipment availability")
        print("3. Remove equipment")
        choice = self.read_choice("Select action: ")

        if choice == "1":
            item_id = self.read_choice("Equipment ID: ").upper()
            name = self.read_choice("Equipment name: ")
            category = self.read_choice("Category: ")
            quantity_text = self.read_choice("Total quantity: ")
            if not quantity_text.isdigit():
                print("Invalid quantity.")
                return
            quantity = int(quantity_text)
            self.equipment.append({
                "id": item_id,
                "name": name,
                "category": category,
                "available": quantity,
                "total": quantity,
            })
            print("Equipment added.")
        elif choice == "2":
            item_id = self.read_choice("Equipment ID: ").upper()
            item = next((entry for entry in self.equipment if entry["id"] == item_id), None)
            if item is None:
                print("Equipment not found.")
                return
            quantity_text = self.read_choice("Available quantity: ")
            if not quantity_text.isdigit() or int(quantity_text) > item["total"]:
                print("Invalid quantity.")
                return
            item["available"] = int(quantity_text)
            print("Equipment availability updated.")
        elif choice == "3":
            item_id = self.read_choice("Equipment ID to remove: ").upper()
            item = next((entry for entry in self.equipment if entry["id"] == item_id), None)
            if item:
                self.equipment.remove(item)
                print("Equipment removed.")
            else:
                print("Equipment not found.")
        else:
            print("Invalid action.")

    def resource_management(self):
        print("\n--- Resource Management ---")
        resources = [
            {**item, "resource_type": "Equipment"}
            for item in self.equipment
        ] + [
            {**lab, "resource_type": "Laboratory",
             "available": lab["capacity"] - lab["booked"]}
            for lab in self.laboratories
        ]
        resources = self.search_rows(resources, ["id", "name", "category",
                                                 "resource_type"])
        resources = self.sort_rows(resources, ["id", "name", "resource_type",
                                               "available"])
        for resource in resources:
            print(f"{resource['id']} | {resource['resource_type']} | "
                  f"{resource['name']} | Available: {resource['available']}")

    def add_administrator(self):
        print("\n--- Add Administrator ---")
        username = self.read_choice("New administrator username: ").lower()
        if username in self.admins:
            print("Administrator username already exists.")
            return
        name = self.read_choice("Administrator name: ")
        password = input("Password: ")
        if not password:
            print("Password cannot be empty.")
            return
        self.admins[username] = {"password": password, "name": name}
        print(f"Administrator '{username}' added successfully.")

    def user_menu(self, username):
        while True:
            print("\n========================================")
            print(f"           User Menu: {self.users[username]['name']}")
            print("========================================")
            print("1. Request/Cancel Laboratory Reservation")
            print("2. Request Equipment Reservation")
            print("3. View Current Reservations")
            print("4. Accountability Form")
            print("5. View Available Resources")
            print("6. Logbook System")
            print("7. Log out")

            choice = self.read_choice("Please choose a number: ")
            if choice == "1":
                print("\n1. Request laboratory")
                print("2. Cancel laboratory/equipment reservation")
                action = self.read_choice("Select action: ")
                if action == "1":
                    self.request_laboratory(username)
                elif action == "2":
                    self.cancel_reservation(username)
                else:
                    print("Invalid action.")
            elif choice == "2":
                self.request_equipment(username)
            elif choice == "3":
                self.view_reservations(username=username)
            elif choice == "4":
                self.accountability_form(username)
            elif choice == "5":
                self.view_available_resources()
            elif choice == "6":
                self.view_logbook(username=username)
            elif choice == "7":
                self.add_log(username, "Logged out")
                print("Logged out.")
                return
            else:
                print("Invalid menu choice.")

    def admin_menu(self, username):
        while True:
            print("\n========================================")
            print(f"       Admin Menu: {self.admins[username]['name']}")
            print("========================================")
            print("1. Set Available Reservations")
            print("2. Set Equipment Reservations")
            print("3. View Current Reservations")
            print("4. Resource Management")
            print("5. Logbook System")
            print("6. Add administrator")
            print("7. Log out")

            choice = self.read_choice("Please choose a number: ")
            if choice == "1":
                self.set_laboratory_reservations()
            elif choice == "2":
                self.set_equipment_reservations()
            elif choice == "3":
                self.view_reservations(admin=True)
            elif choice == "4":
                self.resource_management()
            elif choice == "5":
                self.view_logbook(admin=True)
            elif choice == "6":
                self.add_administrator()
            elif choice == "7":
                self.add_log(username, "Administrator logged out")
                print("Logged out.")
                return
            else:
                print("Invalid menu choice.")

    def run(self):
        print("\n========================================")
        print("                 LABly")
        print(" Laboratory Reservation Management")
        print("========================================")

        while True:
            print("\n1. Log in")
            print("2. Create user account")
            print("3. Exit")
            choice = self.read_choice("Please choose a number: ")

            if choice == "1":
                login = self.login()
                if login:
                    role, username = login
                    self.add_log(username, "Logged in")
                    if role == "user":
                        self.user_menu(username)
                    else:
                        self.admin_menu(username)
            elif choice == "2":
                self.register_user()
            elif choice == "3":
                print("Thank you for using LABly.")
                break
            else:
                print("Invalid choice.")


class LABlyGUI:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.role = None
        self.username = None

        self.root.title("LABly - Laboratory Reservation System")
        self.root.geometry("760x520")
        self.root.minsize(700, 480)
        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.role = None
        self.username = None

        frame = tk.Frame(self.root, padx=30, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="LABly", font=("Arial", 24, "bold")).pack(pady=(0, 5))
        tk.Label(frame, text="Laboratory Reservation Management",
                 font=("Arial", 11)).pack(pady=(0, 20))

        tk.Label(frame, text="Role").pack(anchor="w")
        role = ttk.Combobox(frame, values=["User", "Administrator"],
                            state="readonly", width=28)
        role.set("User")
        role.pack(pady=(0, 10))

        tk.Label(frame, text="Username").pack(anchor="w")
        username = ttk.Entry(frame, width=30)
        username.pack(pady=(0, 10))

        tk.Label(frame, text="Password").pack(anchor="w")
        password = ttk.Entry(frame, width=30, show="*")
        password.pack(pady=(0, 15))

        def login():
            selected_role = "user" if role.get() == "User" else "admin"
            accounts = self.system.users if selected_role == "user" else self.system.admins
            entered_username = username.get().strip().lower()
            if entered_username not in accounts:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                return
            if accounts[entered_username]["password"] != password.get():
                messagebox.showerror("Login Failed", "Invalid username or password.")
                return

            self.role = selected_role
            self.username = entered_username
            self.system.add_log(entered_username, "Logged in")
            if selected_role == "user":
                self.show_user_dashboard()
            else:
                self.show_admin_dashboard()

        ttk.Button(frame, text="Log In", width=28, command=login).pack(pady=5)
        ttk.Button(frame, text="Create User Account", width=28,
                   command=self.show_register_window).pack(pady=5)

    def show_register_window(self):
        window = tk.Toplevel(self.root)
        window.title("Create User Account")
        window.geometry("380x330")
        window.resizable(False, False)

        tk.Label(window, text="Create Account", font=("Arial", 16, "bold")).pack(pady=15)

        fields = {}
        for label, hidden in (
            ("Full Name", False),
            ("Username", False),
            ("Password", True),
            ("Confirm Password", True),
        ):
            tk.Label(window, text=label).pack(anchor="w", padx=40)
            entry = ttk.Entry(window, width=35, show="*" if hidden else "")
            entry.pack(pady=(0, 8))
            fields[label] = entry

        def register():
            name = fields["Full Name"].get().strip()
            username = fields["Username"].get().strip().lower()
            password = fields["Password"].get()
            confirm = fields["Confirm Password"].get()

            if not name or not username:
                messagebox.showerror("Registration Failed", "Name and username are required.")
                return
            if username in self.system.users:
                messagebox.showerror("Registration Failed", "Username already exists.")
                return
            if not password:
                messagebox.showerror("Registration Failed", "Password cannot be empty.")
                return
            if password != confirm:
                messagebox.showerror("Registration Failed", "Passwords do not match.")
                return

            self.system.users[username] = {"password": password, "name": name}
            self.system.add_log(username, "Created a user account")
            messagebox.showinfo("Registration Complete",
                                f"Account '{username}' was created successfully.")
            window.destroy()

        ttk.Button(window, text="Create Account", command=register).pack(pady=12)

    def make_header(self, title):
        header = tk.Frame(self.root, padx=15, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=title, font=("Arial", 18, "bold")).pack(side="left")
        ttk.Button(header, text="Log Out", command=self.logout).pack(side="right")

    def logout(self):
        self.system.add_log(self.username, "Logged out")
        self.show_login()

    def show_user_dashboard(self):
        self.clear_window()
        name = self.system.users[self.username]["name"]
        self.make_header(f"User Dashboard - {name}")

        buttons = tk.Frame(self.root, padx=25, pady=15)
        buttons.pack(expand=True)

        actions = (
            ("Request Laboratory Reservation", self.gui_laboratory_reservation),
            ("Cancel Reservation", self.gui_cancel_reservation),
            ("Request Equipment Reservation", self.gui_equipment_reservation),
            ("View Current Reservations", self.gui_reservations),
            ("Submit Accountability Form", self.gui_accountability),
            ("View Available Resources", self.gui_resources),
            ("View Logbook", self.gui_logbook),
        )
        for text, command in actions:
            ttk.Button(buttons, text=text, width=38, command=command).pack(pady=5)

    def gui_laboratory_reservation(self):
        window = tk.Toplevel(self.root)
        window.title("Laboratory Reservation")
        window.geometry("500x430")

        tk.Label(window, text="Reservation Date").pack(anchor="w", padx=30, pady=(15, 3))
        date_entry = ttk.Entry(window, width=25)
        date_entry.insert(0, date.today().isoformat())
        date_entry.pack(anchor="w", padx=30)

        tk.Label(window, text="Laboratory").pack(anchor="w", padx=30, pady=(12, 3))
        laboratory_names = [lab["name"] for lab in self.system.laboratories]
        laboratory = ttk.Combobox(window, values=laboratory_names,
                                  state="readonly", width=38)
        laboratory.set(laboratory_names[0] if laboratory_names else "")
        laboratory.pack(anchor="w", padx=30)

        tk.Label(window, text="Intervals (use Ctrl to select multiple)").pack(
            anchor="w", padx=30, pady=(12, 3)
        )
        interval_list = tk.Listbox(window, selectmode="multiple", height=9,
                                   exportselection=False)
        for interval in self.system.LAB_INTERVALS:
            interval_list.insert("end", interval)
        interval_list.pack(anchor="w", padx=30)

        def reserve():
            reservation_date = date_entry.get().strip()
            try:
                date.fromisoformat(reservation_date)
            except ValueError:
                messagebox.showerror("Invalid Date", "Use the YYYY-MM-DD format.")
                return

            all_block = self.system.blocked_laboratory_dates.get(
                ("__ALL__", reservation_date)
            )
            if all_block:
                messagebox.showerror("Date Blocked",
                                     f"Laboratories cannot be conducted on this date.\n"
                                     f"Reason: {all_block}")
                return

            lab = next((item for item in self.system.laboratories
                        if item["name"] == laboratory.get()), None)
            if lab is None:
                messagebox.showerror("Invalid Laboratory", "Select a laboratory.")
                return

            lab_block = self.system.blocked_laboratory_dates.get(
                (lab["name"], reservation_date)
            )
            if lab_block:
                messagebox.showerror("Date Blocked",
                                     f"This laboratory is unavailable.\nReason: {lab_block}")
                return

            selected = interval_list.curselection()
            if not selected:
                messagebox.showerror("No Interval", "Select at least one interval.")
                return

            created = []
            skipped = []
            for index in selected:
                interval = self.system.LAB_INTERVALS[index]
                block_reason = self.system.laboratory_block_reason(
                    lab["name"], reservation_date, interval
                )
                if block_reason:
                    skipped.append(f"{interval} (blocked: {block_reason})")
                    continue

                duplicate = any(
                    reservation["username"] == self.username
                    and reservation["type"] == "Laboratory"
                    and reservation["resource"] == lab["name"]
                    and reservation["date"] == reservation_date
                    and reservation["time"] == interval
                    for reservation in self.system.reservations
                )
                if duplicate:
                    skipped.append(f"{interval} (already reserved)")
                    continue

                booked = sum(
                    1 for reservation in self.system.reservations
                    if reservation["type"] == "Laboratory"
                    and reservation["resource"] == lab["name"]
                    and reservation["date"] == reservation_date
                    and reservation["time"] == interval
                )
                if booked >= lab["capacity"]:
                    skipped.append(f"{interval} (full)")
                    continue

                reservation_id = f"RES-{self.system.next_reservation_id:04d}"
                self.system.next_reservation_id += 1
                self.system.reservations.append({
                    "id": reservation_id,
                    "username": self.username,
                    "type": "Laboratory",
                    "resource": lab["name"],
                    "date": reservation_date,
                    "time": interval,
                    "quantity": 1,
                    "status": "Requested",
                })
                created.append(reservation_id)
                self.system.add_log(
                    self.username,
                    f"Requested laboratory reservation {reservation_id}",
                )

            message = ""
            if created:
                message += "Created: " + ", ".join(created)
            if skipped:
                message += ("\nSkipped: " if message else "") + ", ".join(skipped)
            messagebox.showinfo("Laboratory Reservations", message or "No reservation created.")

        ttk.Button(window, text="Reserve Selected Intervals",
                   command=reserve).pack(pady=12)

    def gui_cancel_reservation(self):
        rows = [row for row in self.system.reservations
                if row["username"] == self.username]
        if not rows:
            messagebox.showinfo("Reservations", "You have no reservations.")
            return

        window = tk.Toplevel(self.root)
        window.title("Cancel Reservation")
        window.geometry("650x340")

        tree = ttk.Treeview(window, columns=("ID", "Type", "Resource",
                                             "Date", "Time", "Status"),
                            show="headings")
        for column in ("ID", "Type", "Resource", "Date", "Time", "Status"):
            tree.heading(column, text=column)
            tree.column(column, width=100)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        for row in rows:
            tree.insert("", "end", values=(row["id"], row["type"], row["resource"],
                                           row["date"], row["time"], row["status"]))

        def cancel():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Cancel Reservation", "Select a reservation.")
                return
            reservation_id = tree.item(selected[0], "values")[0]
            reservation = next((row for row in rows if row["id"] == reservation_id), None)
            if reservation is None:
                return
            if reservation["type"] == "Equipment":
                item = next((item for item in self.system.equipment
                             if item["name"] == reservation["resource"]), None)
                if item:
                    item["available"] += reservation["quantity"]
            self.system.reservations.remove(reservation)
            self.system.add_log(self.username,
                                f"Cancelled reservation {reservation_id}")
            tree.delete(selected[0])
            messagebox.showinfo("Cancelled", "Reservation cancelled.")

        ttk.Button(window, text="Cancel Selected Reservation", command=cancel).pack(pady=5)

    def gui_equipment_reservation(self):
        window = tk.Toplevel(self.root)
        window.title("Equipment Reservation")
        window.geometry("420x300")

        tk.Label(window, text="Equipment").pack(anchor="w", padx=30, pady=(15, 3))
        equipment_names = [item["name"] for item in self.system.equipment
                           if item["available"] > 0]
        equipment = ttk.Combobox(window, values=equipment_names,
                                 state="readonly", width=38)
        equipment.set(equipment_names[0] if equipment_names else "")
        equipment.pack(anchor="w", padx=30)

        tk.Label(window, text="Quantity").pack(anchor="w", padx=30, pady=(10, 3))
        quantity = ttk.Entry(window, width=15)
        quantity.pack(anchor="w", padx=30)

        tk.Label(window, text="Use Date").pack(anchor="w", padx=30, pady=(10, 3))
        use_date = ttk.Entry(window, width=15)
        use_date.insert(0, date.today().isoformat())
        use_date.pack(anchor="w", padx=30)

        def reserve():
            item = next((item for item in self.system.equipment
                         if item["name"] == equipment.get()), None)
            if item is None:
                messagebox.showerror("Equipment", "Select equipment.")
                return
            if not quantity.get().isdigit():
                messagebox.showerror("Quantity", "Quantity must be a number.")
                return
            amount = int(quantity.get())
            if amount < 1 or amount > item["available"]:
                messagebox.showerror("Quantity",
                                     f"Available quantity: {item['available']}")
                return
            try:
                date.fromisoformat(use_date.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Date", "Use YYYY-MM-DD.")
                return

            reservation_id = f"RES-{self.system.next_reservation_id:04d}"
            self.system.next_reservation_id += 1
            self.system.reservations.append({
                "id": reservation_id,
                "username": self.username,
                "type": "Equipment",
                "resource": item["name"],
                "date": use_date.get().strip(),
                "time": "Not specified",
                "quantity": amount,
                "status": "Requested",
            })
            item["available"] -= amount
            self.system.add_log(
                self.username,
                f"Requested equipment reservation {reservation_id}",
            )
            messagebox.showinfo("Equipment Reservation",
                                f"Requested successfully ({reservation_id}).")

        ttk.Button(window, text="Request Equipment", command=reserve).pack(pady=15)

    def create_table_window(self, title, columns, rows):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("780x430")

        search_frame = tk.Frame(window)
        search_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(search_frame, text="Search").pack(side="left")
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side="left", padx=5)

        tree = ttk.Treeview(window, columns=tuple(columns), show="headings")
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=max(95, 700 // len(columns)), anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def populate():
            keyword = search_entry.get().strip().lower()
            for item in tree.get_children():
                tree.delete(item)
            for row in rows:
                if not keyword or any(keyword in str(value).lower()
                                      for value in row):
                    tree.insert("", "end", values=row)

        search_entry.bind("<KeyRelease>", lambda event: populate())
        populate()
        return window

    def gui_reservations(self):
        rows = [
            (row["id"], row["username"], row["type"], row["resource"],
             row["date"], row["time"], row["quantity"], row["status"])
            for row in self.system.reservations
            if self.role == "admin" or row["username"] == self.username
        ]
        self.create_table_window(
            "Current Reservations",
            ("ID", "Username", "Type", "Resource", "Date", "Time",
             "Quantity", "Status"),
            rows,
        )

    def gui_accountability(self):
        window = tk.Toplevel(self.root)
        window.title("Accountability Form")
        window.geometry("420x390")

        fields = {}
        for label in ("Borrower Name", "Resource", "Quantity",
                      "Condition", "Remarks"):
            tk.Label(window, text=label).pack(anchor="w", padx=30,
                                               pady=(10, 2))
            entry = ttk.Entry(window, width=38)
            entry.pack(anchor="w", padx=30)
            fields[label] = entry

        def submit():
            quantity = fields["Quantity"].get().strip()
            if not quantity.isdigit():
                messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
                return
            if not fields["Borrower Name"].get().strip():
                messagebox.showerror("Invalid Form", "Borrower name is required.")
                return

            self.system.accountability.append({
                "username": self.username,
                "name": fields["Borrower Name"].get().strip(),
                "resource": fields["Resource"].get().strip(),
                "quantity": int(quantity),
                "condition": fields["Condition"].get().strip(),
                "remarks": fields["Remarks"].get().strip(),
            })
            self.system.add_log(
                self.username,
                f"Submitted accountability for {fields['Resource'].get().strip()}",
            )
            messagebox.showinfo("Accountability", "Accountability form submitted.")

        ttk.Button(window, text="Submit Form", command=submit).pack(pady=15)

    def gui_resources(self):
        rows = [
            (item["id"], "Equipment", item["name"], item["available"])
            for item in self.system.equipment
        ] + [
            (lab["id"], "Laboratory", lab["name"],
             lab["capacity"] - lab["booked"])
            for lab in self.system.laboratories
        ]
        self.create_table_window(
            "Available Resources",
            ("ID", "Type", "Name", "Available"),
            rows,
        )

    def gui_logbook(self):
        rows = [
            (entry["date"], entry["time"], entry["username"], entry["action"])
            for entry in self.system.logbook
            if self.role == "admin" or entry["username"] == self.username
        ]
        self.create_table_window(
            "Logbook",
            ("Date", "Time", "Username", "Action"),
            rows,
        )

    def show_admin_dashboard(self):
        self.clear_window()
        name = self.system.admins[self.username]["name"]
        self.make_header(f"Administrator Dashboard - {name}")

        buttons = tk.Frame(self.root, padx=25, pady=15)
        buttons.pack(expand=True)

        actions = (
            ("Set Laboratory Reservations", self.gui_admin_laboratories),
            ("Set Equipment Reservations", self.gui_admin_equipment),
            ("View Current Reservations", self.gui_reservations),
            ("Resource Management", self.gui_admin_resources),
            ("View Logbook", self.gui_logbook),
            ("Add Administrator", self.gui_add_administrator),
        )
        for text, command in actions:
            ttk.Button(buttons, text=text, width=38, command=command).pack(pady=5)

    def gui_admin_laboratories(self):
        window = tk.Toplevel(self.root)
        window.title("Laboratory Reservations")
        window.geometry("700x560")

        tk.Label(window, text="Add Laboratory Schedule",
                 font=("Arial", 14, "bold")).pack(pady=10)
        add_frame = tk.Frame(window)
        add_frame.pack(padx=20)

        tk.Label(add_frame, text="ID").grid(row=0, column=0, sticky="w")
        lab_id = ttk.Entry(add_frame, width=12)
        lab_id.grid(row=1, column=0, padx=(0, 8))

        tk.Label(add_frame, text="Name").grid(row=0, column=1, sticky="w")
        lab_name = ttk.Entry(add_frame, width=24)
        lab_name.grid(row=1, column=1, padx=(0, 8))

        tk.Label(add_frame, text="Capacity").grid(row=0, column=2, sticky="w")
        capacity = ttk.Entry(add_frame, width=10)
        capacity.grid(row=1, column=2)

        def add_lab():
            if not lab_id.get().strip() or not lab_name.get().strip():
                messagebox.showerror("Laboratory", "ID and name are required.")
                return
            if not capacity.get().isdigit():
                messagebox.showerror("Laboratory", "Capacity must be a number.")
                return
            lab_id_value = lab_id.get().strip().upper()
            if any(lab["id"] == lab_id_value for lab in self.system.laboratories):
                messagebox.showerror("Laboratory", "Laboratory ID already exists.")
                return
            self.system.laboratories.append({
                "id": lab_id_value,
                "name": lab_name.get().strip(),
                "date": "Every day",
                "time": "All fixed intervals",
                "capacity": int(capacity.get()),
                "booked": 0,
            })
            messagebox.showinfo("Laboratory", "Laboratory schedule added.")

        ttk.Button(window, text="Add Laboratory", command=add_lab).pack(pady=10)

        tk.Label(window, text="Block an Entire Day or Specific Session",
                 font=("Arial", 14, "bold")).pack(pady=(12, 5))
        block_frame = tk.Frame(window)
        block_frame.pack(padx=20)

        tk.Label(block_frame, text="Date").grid(row=0, column=0, sticky="w")
        blocked_date = ttk.Entry(block_frame, width=15)
        blocked_date.grid(row=1, column=0, padx=(0, 8))

        tk.Label(block_frame, text="Block").grid(row=0, column=1, sticky="w")
        block_type = ttk.Combobox(
            block_frame,
            values=["Entire day", "Specific session"],
            state="readonly",
            width=18,
        )
        block_type.set("Entire day")
        block_type.grid(row=1, column=1, padx=(0, 8))

        tk.Label(block_frame, text="Scope").grid(row=0, column=2, sticky="w")
        lab_scopes = ["All laboratories"] + [
            lab["name"] for lab in self.system.laboratories
        ]
        scope = ttk.Combobox(block_frame, values=lab_scopes,
                             state="readonly", width=24)
        scope.set("All laboratories")
        scope.grid(row=1, column=2, padx=(0, 8))

        tk.Label(block_frame, text="Sessions (Ctrl-click for multiple)").grid(
            row=0, column=3, sticky="w"
        )
        session_frame = tk.Frame(block_frame)
        session_frame.grid(row=1, column=3)
        session_scrollbar = tk.Scrollbar(session_frame, orient="vertical")
        session_scrollbar.pack(side="right", fill="y")
        session = tk.Listbox(
            session_frame,
            selectmode="extended",
            height=5,
            width=22,
            yscrollcommand=session_scrollbar.set,
        )
        for interval in self.system.LAB_INTERVALS:
            session.insert(tk.END, interval)
        session.pack(side="left")
        session_scrollbar.config(command=session.yview)

        reason_frame = tk.Frame(window)
        reason_frame.pack(fill="x", padx=20, pady=(8, 0))
        tk.Label(reason_frame, text="Reason").pack(side="left")
        reason = ttk.Entry(reason_frame)
        reason.pack(side="left", fill="x", expand=True, padx=8)

        def block():
            blocked = blocked_date.get().strip()
            try:
                date.fromisoformat(blocked)
            except ValueError:
                messagebox.showerror("Invalid Date", "Use YYYY-MM-DD.")
                return
            if not reason.get().strip():
                messagebox.showerror("Reason Required",
                                     "Enter why laboratories cannot be conducted.")
                return
            scope_key = "__ALL__" if scope.get() == "All laboratories" else scope.get()
            if block_type.get() == "Entire day":
                self.system.blocked_laboratory_dates[(scope_key, blocked)] = reason.get().strip()
                description = f"{scope.get()} for the entire day"
            else:
                selected_indices = session.curselection()
                if not selected_indices:
                    messagebox.showerror("Session Required",
                                         "Select at least one session to block.")
                    return
                selected_sessions = [session.get(index) for index in selected_indices]
                for selected_session in selected_sessions:
                    self.system.blocked_laboratory_sessions[
                        (scope_key, blocked, selected_session)
                    ] = reason.get().strip()
                joined_sessions = ", ".join(selected_sessions)
                description = f"{scope.get()} session(s): {joined_sessions}"
            messagebox.showinfo("Laboratory Blocked",
                                f"Blocked {description} on {blocked}.")

        ttk.Button(window, text="Apply Block", command=block).pack(pady=10)

        tk.Label(window, text="Current Blocks",
                 font=("Arial", 14, "bold")).pack(pady=(5, 5))
        blocked = tk.Text(window, height=9, width=78)
        blocked.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        blocked_items = [
            ((scope_key, blocked_date_value), reason_text, "Entire day")
            for (scope_key, blocked_date_value), reason_text
            in self.system.blocked_laboratory_dates.items()
        ] + [
            ((scope_key, blocked_date_value), reason_text, interval)
            for (scope_key, blocked_date_value, interval), reason_text
            in self.system.blocked_laboratory_sessions.items()
        ]
        blocked_items = LABlySystem.insertion_sort(
            blocked_items,
            key=lambda item: str(item[0]).lower() + str(item[2]).lower(),
        )
        if blocked_items:
            for (scope_key, blocked_date_value), reason_text, period in blocked_items:
                scope_name = "All laboratories" if scope_key == "__ALL__" else scope_key
                blocked.insert(
                    "end",
                    f"{blocked_date_value} | {scope_name} | {period} | "
                    f"Reason: {reason_text}\n",
                )
        else:
            blocked.insert("end", "No blocked laboratory dates or sessions.")
        blocked.config(state="disabled")

    def gui_admin_equipment(self):
        window = tk.Toplevel(self.root)
        window.title("Equipment Management")
        window.geometry("500x330")

        tk.Label(window, text="Add Equipment",
                 font=("Arial", 14, "bold")).pack(pady=12)
        add_frame = tk.Frame(window)
        add_frame.pack(padx=20)

        labels = ("ID", "Name", "Category", "Quantity")
        entries = {}
        for index, label in enumerate(labels):
            tk.Label(add_frame, text=label).grid(row=0, column=index, sticky="w")
            entry = ttk.Entry(add_frame, width=14)
            entry.grid(row=1, column=index, padx=4)
            entries[label] = entry

        def add():
            quantity = entries["Quantity"].get().strip()
            if not entries["ID"].get().strip() or not entries["Name"].get().strip():
                messagebox.showerror("Equipment", "ID and name are required.")
                return
            if not quantity.isdigit():
                messagebox.showerror("Equipment", "Quantity must be a number.")
                return
            item_id = entries["ID"].get().strip().upper()
            if any(item["id"] == item_id for item in self.system.equipment):
                messagebox.showerror("Equipment", "Equipment ID already exists.")
                return
            amount = int(quantity)
            self.system.equipment.append({
                "id": item_id,
                "name": entries["Name"].get().strip(),
                "category": entries["Category"].get().strip(),
                "available": amount,
                "total": amount,
            })
            messagebox.showinfo("Equipment", "Equipment added.")

        ttk.Button(window, text="Add Equipment", command=add).pack(pady=12)

        tk.Label(window, text="Update Availability",
                 font=("Arial", 14, "bold")).pack(pady=(10, 5))
        equipment_names = [item["name"] for item in self.system.equipment]
        equipment = ttk.Combobox(window, values=equipment_names,
                                 state="readonly", width=35)
        equipment.set(equipment_names[0] if equipment_names else "")
        equipment.pack(pady=5)
        quantity = ttk.Entry(window, width=12)
        quantity.pack(pady=5)

        def update():
            item = next((item for item in self.system.equipment
                         if item["name"] == equipment.get()), None)
            if item is None:
                messagebox.showerror("Equipment", "Select equipment.")
                return
            if not quantity.get().isdigit():
                messagebox.showerror("Quantity", "Quantity must be a number.")
                return
            amount = int(quantity.get())
            if amount > item["total"]:
                messagebox.showerror("Quantity",
                                     f"Maximum quantity is {item['total']}.")
                return
            item["available"] = amount
            messagebox.showinfo("Equipment", "Availability updated.")

        ttk.Button(window, text="Update Available Quantity",
                   command=update).pack(pady=8)

    def gui_admin_resources(self):
        rows = [
            (item["id"], "Equipment", item["name"], item["category"],
             item["available"], item["total"])
            for item in self.system.equipment
        ] + [
            (lab["id"], "Laboratory", lab["name"], "General",
             lab["capacity"] - lab["booked"], lab["capacity"])
            for lab in self.system.laboratories
        ]
        self.create_table_window(
            "Resource Management",
            ("ID", "Type", "Name", "Category", "Available", "Total"),
            rows,
        )

    def gui_add_administrator(self):
        window = tk.Toplevel(self.root)
        window.title("Add Administrator")
        window.geometry("380x300")

        fields = {}
        for label, hidden in (
            ("Name", False),
            ("Username", False),
            ("Password", True),
        ):
            tk.Label(window, text=label).pack(anchor="w", padx=40,
                                               pady=(12, 2))
            entry = ttk.Entry(window, width=32, show="*" if hidden else "")
            entry.pack(anchor="w", padx=40)
            fields[label] = entry

        def add():
            name = fields["Name"].get().strip()
            username = fields["Username"].get().strip().lower()
            password = fields["Password"].get()
            if not name or not username or not password:
                messagebox.showerror("Administrator",
                                     "Name, username, and password are required.")
                return
            if username in self.system.admins:
                messagebox.showerror("Administrator",
                                     "Administrator username already exists.")
                return
            self.system.admins[username] = {"password": password, "name": name}
            messagebox.showinfo("Administrator",
                                f"Administrator '{username}' added.")

        ttk.Button(window, text="Add Administrator", command=add).pack(pady=15)
if __name__ == "__main__":
    lably_system = LABlySystem()
    root = tk.Tk()
    LABlyGUI(root, lably_system)
    root.mainloop()
