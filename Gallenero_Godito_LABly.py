"""
==============================================================================
    CS 5 (Q2, SY 26-27)
    Name : Gallenero, Danillen M. & Godito, Litlaine Nethri R.
    Section : G12 QUANTUM
==============================================================================
"""

from datetime import date

class HealthRecord:
    def __init__(self, date, symptoms):
        self.date = date
        self.symptoms = symptoms  # List of symptom strings
    
class Student:
    def __init__(self, name, grade, section):
        self.name = name
        self.grade = grade
        self.section = section
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def __str__(self):
        return f"Grade {self.grade} - {self.section}"


class SchoolSystem:
    def __init__(self):
        # Dictionary mapping name to Student object for O(1) lookups
        self.students = {}
        
        self.valid_sections = {
            "7": ["Diamond", "Emerald", "Ruby"],
            "8": ["Jasmin", "Sampaguita", "Waling-Waling"],
            "9": ["Lithium", "Potassium", "Sodium"],
            "10": ["Gluon", "Graviton", "Muon"],
            "11": ["Polaris", "Rigel", "Sirius"],
            "12": ["Byte", "Quantum", "Qubit"]
        }

    def rules_and_guidelines(self):
        print("\n\n-----------Rules and Guidelines-----------\n" \
        "      1. When sick\n" \
        "      2. When using the clinic\n" \
        "      3. When requesting for items\n" \
        "      4. Back to Main Menu")
        thischoice = input("\n\nPlease input your number of choice: ")
        while not thischoice.isnumeric(): #loop until user inputs a number
            thischoice = input("Invalid. Please input your number of choice: ")
        match thischoice:
            case "1":
                print("\n\n===================When Sick===================\n"\
                    "If you are experiencing symptoms that may affect others, avoid unnecessary close contact with classmates.\n"\
                    "Inform your teacher or the clinic if you are unable to attend class because of illness.\n"\
                    "Follow the instructions and recommendations provided by the school nurse.\n"\
                    "Do not take medicine without proper authorization or guidance from the school clinic.\n"\
                    "Seek immediate assistance from the clinic if your symptoms become severe or you feel that you need urgent help.\n\n")
                input("Enter any key to go back to the main menu: ")
            case "2":
                print("\n\n===================When Using the Clinic===================\n"\
                    "State your name, grade level, section, and reason for visiting.\n"\
                    "Maintain cleanliness and observe proper hygiene while inside the clinic.\n"\
                    "Follow the instructions of the school nurse and clinic personnel.\n"\
                    "Respect the privacy and confidentiality of other students.\n"\
                    "Avoid unnecessary noise or disturbance inside the clinic.\n"\
                    "Wait for your turn unless you require urgent medical attention.\n"\
                    "Return to class only when permitted or advised by the appropriate school personnel.\n\n")
                input("Enter any key to go back to the main menu: ")
            case "3":
                print("\n\n===================When Requesting For Items===================\n"\
                    "Ask permission from the clinic personnel before taking or requesting any clinic item.\n"\
                    "Clearly state the item you need and the reason for requesting it.\n"\
                    "Provide your name, grade level, and section when required.\n"\
                    "Only request items that are appropriate for their intended purpose.\n"\
                    "Do not take medicine or medical supplies without authorization.\n"\
                    "Follow the instructions given by the nurse regarding the proper use of any item provided.\n"\
                    "Return reusable clinic items after use, if applicable.\n"\
                    "Report damaged, missing, or improperly stored items to the clinic personnel.\n\n")
                input("Enter any key to go back to the main menu: ")
            case "4":
                print("\n\nYou'll be redirected to the main menu shortly.\n")
            case _:
                print("\n\nINVALID. You'll be redirected to the main menu.\n")

    def report_symptoms(self):
        print("\n\n=========================================")
        print("  SYMPTOMS REPORT (REPORT/REMOVE/MODIFY  )")
        print("=========================================\n\n")

        hasdata = False

        name = input("Please input your name in this format (Name M.I. Surname): ") 

        if name.upper() not in self.students:
            print("\nName not found. Please make sure you type your name correctly. Creating new record...")
            self.register_student(name.upper())
        thischoice = input("\nPlease choose 1 to report a symptom or 2 to remove a previously set symptom or 3 to modify a reported symptom." \
        "\nPlease input a valid number: ")
        templist = []
        if len(self.students[name.upper()].records) >= 1:
            studentrecord = self.students[name.upper()].records[0].symptoms
            hasdata = True
        match thischoice:
            case "1":
                while thischoice == "1":
                    temp = input("\nHow many symptoms will you report? Please input a number: ")
                    if temp.isnumeric():
                        for x in range(int(temp)):
                            thisinput = input("\nPlease input a symptom (one symptom per line): ")
                            if hasdata:
                                if thisinput.lower() in studentrecord:
                                    print("Symptom already listed.")
                                else:
                                    studentrecord.append(thisinput.lower())
                            else:
                                templist.append(thisinput.lower())
                        self.add_student_record(name.upper(), str(date.today()), templist)
                        thischoice = "3"
                    else:
                            print("INVALID. Choose number again.")
                            thischoice = 1
            case "2":
                if name.upper() in self.students and len(self.students[name.upper()].records) >= 1:
                    while thischoice == "2":
                        print("\nYour reported symptoms are: ")
                        for symptom in sorted(studentrecord):
                            print(f"-{symptom}")
                        thisnum = input("\nHow many symptoms would you like to remove? Please input a number: ")
                        if thisnum.isnumeric():
                            if int(thisnum) < len(studentrecord): 
                                for x in range(int(thisnum)): 
                                    toremove = input("\nPlease input the exact symptom inputted: ")
                                    if toremove.lower() in studentrecord:
                                        studentrecord.remove(toremove.lower())
                                    else:
                                        print("INVALID. No matching symptom from records.")
                                thischoice = 3
                            elif int(thisnum) == len(studentrecord):
                                thischoice = input("\nYour inputted number equals your number of symptoms. Would you like to clear your recorded symptoms?\n" \
                                "Press 1 to confirm you want to clear or press 2 so you can choose your number again. Please input number: ") #if equal just clear all data?
                                if thischoice == "1":
                                    self.students.pop(name.upper())
                                elif thischoice == "2":
                                    print("Reloading...")
                                else:
                                    print("INVALID. Redirecting to choose number again...")
                                    thischoice = "2"
                            else:
                                print("\nInvalid input. Number inputted is greater than number of symptoms. Please choose number again.")
                        else:
                            print("INVALID input. Choose number again.")
                else:
                    print("\nNo symptoms set. Removal invalid.")
            case "3":
                if name.upper() in self.students and len(self.students[name.upper()].records) >= 1:
                    print("\nYour reported symptoms are: ") #print the symptoms
                    for symptom in sorted(studentrecord):
                        print(f"-{symptom}")
                    toreplace = input("Please input the exact symptom inputted: ").lower()
                    if toreplace in studentrecord:
                        studentrecord[studentrecord.index(toreplace)] = input("Please input modification: ").lower()
                    else:
                        print("INVALID. No matching symptom from records. Redirecting to menu...")
                else:
                    print("No symptoms set. Modification invalid.")            
            case _:
                print("INVALID. Redirecting to main menu...")
        #display most recent addition

    def register_student(self, name):
        temp = 1
        while temp == 1:
            grade = input("Please input your grade level (numerical): ")
            
            # Check if the grade exists in our dictionary
            if grade in self.valid_sections:
                allowed_sections = self.valid_sections[grade]
                section_prompt = f"Please input your section ({'/'.join(allowed_sections)}): "
                section = input(section_prompt)
                
                # Check if the entered section is valid for that grade
                if section in allowed_sections:
                    # Instantiate a Student object and add it to our list
                    new_student = Student(name, grade, section)
                    self.students[name] = new_student
                    return True
                else:
                    print("Please input a valid section. Choose a grade level again.")
                    temp = 1
            else:
                print("INVALID. Please choose your grade level again.")
                temp = 1

    def add_student_record(self, name, date, symptoms):
        if name.upper() in self.students:
            record = HealthRecord(date, symptoms)
            self.students[name.upper()].add_record(record)

    def general_report(self):
        print("\n\n=========================================")
        print("             GENERAL REPORTS             ")
        print("=========================================\n\n")
        
        target_date = input("Please input requested date of data (YYYY-MM-DD): ")
        
        matching_students = []
        # Dynamic grade tallies instead of a global list with hardcoded indices
        grade_counts = {"7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}
        
        # Iterate through all registered students and check their records
        for student in self.students.values():
            for record in student.records:
                if record.date == target_date:
                    matching_students.append((student, record.symptoms))
                    if student.grade in grade_counts:
                        grade_counts[student.grade] += 1
                    break  # Count each student once per date

        if not matching_students:
            print("No data from requested date or wrong format.")
            return

        print(f"\nDate: {target_date}")
        print(f"\nNo. of people with symptoms: {len(matching_students)}")
        
        print("\nNo. of people with symptoms per grade level:")
        # Print in descending order (Grade 12 down to Grade 7) matching your original format
        for grade in ["12", "11", "10", "9", "8", "7"]:
            print(f"Grade {grade}: {grade_counts[grade]}")
            
        print("\nList of people with symptoms: ")
        for student, symptoms in matching_students:
            print(f"Name: {student.name}")
            for symptom in sorted(symptoms):
                print(f"- {symptom}")

    def display_students(self):
        print("\n--- Registered Students ---")
        if not self.students:
            print("No students registered yet.")
        for i, student in enumerate(self.students, 1):
            print(f"{i}. {student}")

    def find_student(self, input_name):
            """Replicates your name-matching logic cleanly using object properties."""
            if input_name in self.students:
                return self.students[input_name]
            
            print("No record found. Redirecting to main menu.")
            return None

    def personal_record_menu(self):
        print("\n\n=========================================")
        print("            Personal Records             ")
        print("=========================================\n\n")
        
        input_name = input("Please input your name: ")
        student = self.find_student(input_name.upper())
        
        if not student:
            return

        print(f"\n--- Records for {student.name} ---")
        if not student.records:
            print("No medical/symptom records found.")
            return

        for record in student.records:
            print(f"Date symptom/s was/were recorded: {record.date}")
            for symptom in sorted(record.symptoms):
                print(f"- {symptom}")

    def medical_forms(self):
        print("\n\n=========================================")
        print("               MEDICAL FORMS                 ")
        print("=========================================\n\n")
        print("Available forms:\n" \
        "1. Health History and Personal Data Sheet\n" \
        "2. Physical Examination Form\n" \
        "3. Dental Health Record\n" \
        "4. Clinic Admission Slip\n" \
        "5. Medical/Dental Consent Form\n" \
        "6. Infectious Disease Monitoring Tool\n" \
        "7. Health History and Personal Data Sheet")
        medchoice = input("\nPlease choose a valid number: ")

        match medchoice:
            case "1":
                print("Please go to this link: https://docs.google.com/document/d/1gMoEfS1M4UzvCKdm89OAEPlWEPMmxCYB/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "2":
                print("Please go to this link: https://docs.google.com/document/d/1lSQBp222n-cdXRQNVZuSFskms2DM5xnp/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "3":
                print("Please go to this link: https://docs.google.com/spreadsheets/d/16Zsj8gALeTE0uWL9cFFHg9oTrB0eYGFY/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "4":
                print("Please go to this link: https://docs.google.com/document/d/1X_fi8IXkIr05335IsyKGXm_blOsFKQEf/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "5":
                print("Please go to this link: https://docs.google.com/spreadsheets/d/1eEf2x33YUcw5LUDrNhIV2tP545gBM0zW/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "6":
                print("Please go to this link: https://docs.google.com/spreadsheets/d/1yuaBSmh5rmWm68tVYQxjI8C5owNG4iR3/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case "7":
                print("Please go to this link: https://docs.google.com/document/d/181_3h6ADxg_Kj6Zh8Io3mdNBm6cm4efP/edit?usp=sharing&ouid=115459480952760656709&rtpof=true&sd=true\n")
            case _:
                print("INVALID. Redirecting to menu...")

    def run(self):
        print("\n\n==========================================")
        print("        Medical Self-Report System")
        print("==========================================")
        print("\n A program that allows students to report \n     a symptom they have experienced.")
        print("\nIntended Users: [School Nurse and Students]")

        choice = ""

        while choice != "6":
            print("\n\n\n------------------------------------------")
            print("               MAIN MENU            ")
            print("------------------------------------------")
            print("[1] Clinic Rules and Guidelines")
            print("[2] Symptoms (Report/Remove/Modify)")
            print("[3] Personal Record")
            print("[4] Medical Forms")
            print("[5] General Report")
            print("[6] Exit")
            choice = input("\nPlease choose a number: ")

            match choice:
                case "1":
                    self.rules_and_guidelines() 
                case "2":
                    self.report_symptoms()
                case "3":
                    self.personal_record_menu()
                case "4":
                    self.medical_forms() 
                case "5":
                    self.general_report()
                case "6":
                    print("Thank you very much for contributing to the database.")
                case _:
                    print("Invalid, please choose again.")