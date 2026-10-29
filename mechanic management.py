import mysql.connector
import datetime
from decimal import Decimal 

# ------------------- Database Connection -------------------
def db_connection():
    host = input("Enter Host: ").strip()
    user = input("Enter User: ").strip()
    password = input("Enter Password: ").strip()
    
    db = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = "mechanicdb"
    )
    return (db.cursor() , db)

# ------------------- Utility Functions -------------------
def line():
    print("-" * 120)

# ------------------- Customer Management -------------------
def add_customer():
    print("\n ADD CUSTOMER")
    name = input("Enter customer name: ").strip()
    phone = input("Enter phone number: ").strip()
    vehicle_number = input("Enter vehicle number: ").strip()
    vehicle_model = input("Enter vehicle model: ").strip()

    cursor.execute("""
        INSERT INTO customers (name, phone, vehicle_number, vehicle_model)
        VALUES (%s, %s, %s, %s)
        """,
        (name, phone, vehicle_number, vehicle_model))
    
    db.commit()
    print(f"✅ Customer '{name}' added successfully!\n")

def show_customers():
    print("\n CUSTOMERS LIST \n")
    cursor.execute("SELECT * FROM customers")
    results = cursor.fetchall()
    
    if not results:
        print("⚠️ No customers found.\n")
        return
    
    line()
    print(f"{'ID':<5}{'Name':<50}{'Phone':<15}{'Vehicle No.':<15}{'Model':<30}")
    
    line()
    for row in results:
        print(f"{row[0]:<5}{row[1]:<50}{row[2]:<15}{row[3]:<15}{row[4]:<30}")
    line()

# ------------------- Parts Management -------------------
def add_part():
    print("\n ADD PART")
    name = input("Enter part name: ").strip()
    price = Decimal(input("Enter price: ")) 
    stock = int(input("Enter stock quantity: "))

    cursor.execute("""
        INSERT INTO parts (part_name, price, stock)
        VALUES (%s, %s, %s)
        """, 
        (name, price, stock))
    db.commit()
    print(f"✅ Part '{name}' added successfully!\n")

def show_parts():
    print("\n PARTS LIST \n")
    cursor.execute("SELECT * FROM parts")
    parts = cursor.fetchall()
    
    if not parts:
        print("⚠️ No parts found.\n")
        return
    
    line()
    print(f"{'ID':<5}{'Name':<50}{'Price':<10}{'Stock'}")
    line()
    
    for p in parts:
        print(f"{p[0]:<5}{p[1]:<50}{p[2]:<10}{p[3]}")
    line()

def update_part_stock():
    show_parts()
    pid = input("Enter Part ID to update: ")
    qty = int(input("Enter new stock quantity: "))
    cursor.execute("UPDATE parts SET stock=%s WHERE part_id=%s", (qty, pid))
    db.commit()
    print("✅ Stock updated successfully!\n")

# ------------------- Tools Management -------------------
def add_tool():
    print("\n ADD TOOL")
    name = input("Enter tool name: ").strip()
    condition = input("Enter condition (Good/Damaged): ").strip()
    
    cursor.execute("""
        INSERT INTO tools (tool_name, condition_status) 
        VALUES (%s, %s)
        """, 
        (name, condition))
    
    db.commit()
    print("✅ Tool added successfully!\n")

def show_tools():
    print("\n TOOLS LIST \n")
    cursor.execute("SELECT * FROM tools")
    tools = cursor.fetchall()
    
    if not tools:
        print("⚠️ No tools found.\n")
        return
    
    line()
    print(f"{'ID':<5}{'Tool Name':<50}{'Condition'}")
    line()
    
    for t in tools:
        print(f"{t[0]:<5}{t[1]:<50}{t[2]}")
    line()

# ------------------- Work Management -------------------
def add_work():
    show_customers()
    print("\n ADD WORK")
    cust_id = input("Enter customer ID: ")
    desc = input("Enter work description: ")
    labour = Decimal(input("Enter labour charge: "))  # FIXED

    cursor.execute("""
        INSERT INTO works (customer_id, description, labour_charge, status) 
        VALUES (%s,%s,%s,'Pending')
        """,
        (cust_id, desc, labour))
    
    db.commit()
    print("✅ Work added successfully!\n")

def assign_part_to_work():
    show_parts()
    show_works()
    print("\n ASSIGN PART TO WORK")
    work_id = input("Enter work ID: ")
    part_id = input("Enter part ID: ")
    qty = int(input("Enter quantity used: "))

    cursor.execute("""
        INSERT INTO work_parts (work_id, part_id, quantity) 
        VALUES (%s, %s, %s)
        """, 
        (work_id, part_id, qty))
    
    db.commit()
    print("✅ Part assigned successfully.\n")

def show_works():
    print("\n WORKS \n")
    cursor.execute("SELECT * FROM works")
    works = cursor.fetchall()
    
    if not works:
        print("⚠️ No works found.\n")
        return
    
    line()
    print(f"{'ID':<5}{'CustID':<10}{'Description':<75}{'Status':<15}{'Labour(₹)':<10}")
    line()
    
    for w in works:
        print(f"{w[0]:<5}{w[1]:<10}{w[2]:<75}{w[4]:<15}{w[3]:<10}")
    line()

# ------------------- Billing -------------------
def complete_work_and_generate_bill():
    show_works()
    print("\n BILL GENERATION")
    work_id = input("Enter work ID: ")

    gst_rate = Decimal(input("Enter GST rate (%): "))

    cursor.execute("SELECT labour_charge FROM works WHERE work_id=%s", (work_id,))
    labour = cursor.fetchone()[0]

    cursor.execute("""
        SELECT p.price, wp.quantity
        FROM work_parts wp
        JOIN parts p ON wp.part_id = p.part_id
        WHERE wp.work_id = %s
        """, (work_id,))
    parts_used = cursor.fetchall()

    subtotal = labour + sum(price * qty for price, qty in parts_used)
    gst = subtotal * gst_rate / Decimal(100)
    total = subtotal + gst
    today = datetime.datetime.now().date()

    cursor.execute("INSERT INTO bills (work_id, subtotal, gst, total, date) VALUES (%s, %s, %s, %s, %s)",
                   (work_id, subtotal, gst, total, today))
    db.commit()

    cursor.execute("UPDATE works SET status='Completed' WHERE work_id=%s", (work_id,))
    db.commit()

    print(f"\n✅ Bill generated. Grand Total = ₹{total}")

# ------------------- Extra Features -------------------
def check_tire_pressure():
    print("\n TIRE PRESSURE CHECKER")
    print("Select your car model:\n")

    cars = {
        1: ("Maruti Suzuki Swift", 33),
        2: ("Maruti Baleno", 32),
        3: ("Hyundai i20", 33),
        4: ("Hyundai Creta", 34),
        5: ("Tata Punch", 32),
        6: ("Tata Nexon", 34),
        7: ("Mahindra Thar", 32),
        8: ("Mahindra Scorpio-N", 34),
        9: ("Toyota Innova Crysta", 33),
        10: ("Honda City", 32),
        11: ("Kia Seltos", 34),
        12: ("Kia Sonet", 33)
    }

    for key, value in cars.items():
        print(f"{key}. {value[0]} (Ideal: {value[1]} PSI)")

    choice = int(input("\nEnter your car number: "))

    if choice not in cars:
        print("❌ Invalid choice!")
        return

    car_name, ideal = cars[choice]
    current = float(input(f"Enter current tire pressure for {car_name}: "))

    print("\n RESULT \n")
    print(f"Car: {car_name}")
    print(f"Ideal Pressure: {ideal} PSI")
    print(f"Current Pressure: {current} PSI\n")

    if current < ideal:
        print("⚠️ Low tire pressure — please inflate your tyres!")
    elif current > ideal:
        print("⚠️ High tire pressure — release some air.")
    else:
        print("✅ Perfect! Tyre pressure is ideal.")

def show_mechanic_manual():
    print("""
📘 MECHANIC MANUAL:
1. Always inspect before disassembly.
2. Use safety gloves and goggles.
3. Check oil, brakes, and tires regularly.
4. Verify part compatibility before replacement.
5. Ensure torque specs are followed.
6. Clean workspace after repair.
7. Record every repair in the system.
""")

# ------------------- Nearby Shops -------------------
def add_nearby_shop():
    show_parts()
    print("\n ADD NEARBY PARTS SHOP")
    shop_name = input("Enter shop name: ").strip()
    address = input("Enter shop address: ").strip()
    phone = input("Enter phone number: ").strip()
    parts_available = input("Enter parts available (comma-separated): ").strip()

    cursor.execute("""
        INSERT INTO nearby_shops (shop_name, address, phone, parts_available)
        VALUES (%s, %s, %s, %s)
        """, 
        (shop_name, address, phone, parts_available))
    
    db.commit()
    print(f"✅ Shop '{shop_name}' added successfully!\n")


def show_nearby_shops():
    print("\n NEARBY SHOPS \n")
    cursor.execute("SELECT * FROM nearby_shops")
    shops = cursor.fetchall()
    
    if not shops:
        print("⚠️ No nearby shops found.\n")
        return
    
    line()
    print(f"{'ID':<5}{'Shop Name':<25}{'Phone':<15}{'Parts Available':<30}{'Address':<40}")
    line()
    
    for s in shops:
        print(f"{s[0]:<5}{s[1]:<25}{s[3]:<15}{s[4]:<30}{s[2]:<40}")
    line()

# ------------------- Main Menu -------------------
print("===ESTABLISH DATABASE CONNECTION===")
cursor , db = db_connection()

def main_menu():
    while True:
        print("""
====== MECHANICDB MAIN MENU ======
1. Add Customer
2. Show Customers
3. Add Part
4. Update Part Stock
5. Show Parts
6. Add Tool
7. Show Tools
8. Add Work
9. Assign Part to Work
10. Show Works
11. Complete Work & Generate Bill
12. Check Tire Pressure
13. Add Nearby Shop
14. Show Nearby Shops
15. Show Mechanic Manual
0. Exit
""")
        ch = input("Enter choice: ")
        if ch == '1': add_customer()
        elif ch == '2': show_customers()
        elif ch == '3': add_part()
        elif ch == '4': update_part_stock()
        elif ch == '5': show_parts()
        elif ch == '6': add_tool()
        elif ch == '7': show_tools()
        elif ch == '8': add_work()
        elif ch == '9': assign_part_to_work()
        elif ch == '10': show_works()
        elif ch == '11': complete_work_and_generate_bill()
        elif ch == '12': check_tire_pressure()
        elif ch == '13': add_nearby_shop()
        elif ch == '14': show_nearby_shops()
        elif ch == '15': show_mechanic_manual()
        elif ch == '0':
            print("👋 Exiting Mechanic Management System.")
            break
        else:
            print("❌ Invalid choice! Try again.\n")

# ------------------- Start -------------------
if __name__ == "__main__":
    main_menu()
