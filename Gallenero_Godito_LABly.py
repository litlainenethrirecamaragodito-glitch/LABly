"""
LABly - Laboratory Reservation and Resource Management System
Console application for students/users and administrators.
"""

from datetime import date


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
             "time": "All fixed intervals", "capacity": 30, "booked": 0},
            {"id": "LAB-002", "name": "Chemistry Laboratory 2", "date": "Every day",
             "time": "All fixed intervals", "capacity": 25, "booked": 0},
            {"id": "LAB-003", "name": "Computer Laboratory", "date": "Every day",
             "time": "All fixed intervals", "capacity": 40, "booked": 0},
        ]
        self.blocked_laboratory_dates = {}
        self.equipment = [
            {"id": "EQ-001", "name": "Microscope", "category": "Science",
             "available": 10, "total": 10},
            {"id": "EQ-002", "name": "Laptop", "category": "Computer",
             "available": 15, "total": 15},
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
                return sorted(rows, key=lambda row: str(row.get(field, "")).lower(), reverse=reverse)
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

        lab_date = reservation_date
        all_date_block = self.blocked_laboratory_dates.get(("__ALL__", lab_date))
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

        lab_date_block = self.blocked_laboratory_dates.get((lab["name"], reservation_date))
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
        print("4. Block a date")
        print("5. Unblock a date")
        print("6. View blocked dates")
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

            reason = self.read_choice("Reason laboratory cannot be conducted: ").strip()
            if not reason:
                print("Reason cannot be empty.")
                return
            self.blocked_laboratory_dates[(scope, blocked_date)] = reason
            print(f"Blocked {scope_name} on {blocked_date}. Reason: {reason}")
        elif choice == "5":
            blocked_date = self.read_choice("Date to unblock (YYYY-MM-DD): ").strip()
            try:
                date.fromisoformat(blocked_date)
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD.")
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

            key = (scope, blocked_date)
            if key not in self.blocked_laboratory_dates:
                print("No matching blocked date found.")
                return
            del self.blocked_laboratory_dates[key]
            print(f"Unblocked {scope_name} on {blocked_date}.")
        elif choice == "6":
            print("\n--- Blocked Laboratory Dates ---")
            if not self.blocked_laboratory_dates:
                print("No blocked laboratory dates.")
                return
            for (scope, blocked_date), reason in sorted(self.blocked_laboratory_dates.items()):
                scope_name = "All laboratories" if scope == "__ALL__" else scope
                print(f"{blocked_date} | {scope_name} | Reason: {reason}")
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


if __name__ == "__main__":
    LABlySystem().run()
