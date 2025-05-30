from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

CYLINDER_DB = 'cylinders.json'
CUSTOMER_DB = 'customers.json'

# Initialize with dummy data if not present
def initialize_databases():
    if not os.path.exists(CUSTOMER_DB):
        customers = [
            {"id": "CUST001", "name": "Alice Johnson", "phone": "123-456-7890", "address": "123 Maple St, Springfield"},
            {"id": "CUST002", "name": "Bob Smith", "phone": "987-654-3210", "address": "456 Oak Ave, Shelbyville"}
        ]
        with open(CUSTOMER_DB, 'w') as f:
            json.dump(customers, f, indent=4)

    if not os.path.exists(CYLINDER_DB):
        cylinders = [
            {"id": "CYL001", "location": "Factory", "status": "In factory", "customer_id": None},
            {"id": "CYL002", "location": "Customer Address", "status": "With customer", "customer_id": "CUST001"},
            {"id": "CYL003", "location": "Customer Address", "status": "With customer", "customer_id": "CUST002"}
        ]
        with open(CYLINDER_DB, 'w') as f:
            json.dump(cylinders, f, indent=4)

def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    cylinders = load_json(CYLINDER_DB)
    customers_list = load_json(CUSTOMER_DB)
    customers = {c["id"]: c for c in customers_list}
    return render_template('index.html', cylinders=cylinders, customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customers = load_json(CUSTOMER_DB)

        # Generate new customer id (simple increment based on last ID)
        if customers:
            last_id_num = max(int(c['id'][4:]) for c in customers)
            new_id = f"CUST{last_id_num + 1:03d}"
        else:
            new_id = "CUST001"

        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        address = request.form['address'].strip()

        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('add_customer'))

        new_customer = {"id": new_id, "name": name, "phone": phone, "address": address}
        customers.append(new_customer)
        save_json(customers, CUSTOMER_DB)
        flash(f"Customer {name} added with ID {new_id}", "success")
        return redirect(url_for('index'))

    return render_template('add_customer.html')

@app.route('/add_cylinder', methods=['GET', 'POST'])
def add_cylinder():
    if request.method == 'POST':
        cylinders = load_json(CYLINDER_DB)
        customers = load_json(CUSTOMER_DB)
        customer_ids = {c['id'] for c in customers}

        # Generate new cylinder id
        if cylinders:
            last_id_num = max(int(c['id'][3:]) for c in cylinders)
            new_id = f"CYL{last_id_num + 1:03d}"
        else:
            new_id = "CYL001"

        location = request.form['location'].strip()
        status = request.form['status'].strip()
        customer_id = request.form['customer_id'].strip() or None

        # Validate customer_id if provided
        if customer_id and customer_id not in customer_ids:
            flash("Invalid customer ID", "error")
            return redirect(url_for('add_cylinder'))

        new_cylinder = {"id": new_id, "location": location, "status": status, "customer_id": customer_id}
        cylinders.append(new_cylinder)
        save_json(cylinders, CYLINDER_DB)
        flash(f"Cylinder {new_id} added successfully", "success")
        return redirect(url_for('index'))

    customers = load_json(CUSTOMER_DB)
    return render_template('add_cylinder.html', customers=customers)

@app.route('/update_cylinder/<cylinder_id>', methods=['GET', 'POST'])
def update_cylinder(cylinder_id):
    cylinders = load_json(CYLINDER_DB)
    customers = load_json(CUSTOMER_DB)
    customer_ids = {c['id'] for c in customers}

    cylinder = next((c for c in cylinders if c['id'] == cylinder_id), None)
    if not cylinder:
        flash("Cylinder not found", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        location = request.form['location'].strip()
        status = request.form['status'].strip()
        customer_id = request.form['customer_id'].strip() or None

        if customer_id and customer_id not in customer_ids:
            flash("Invalid customer ID", "error")
            return redirect(url_for('update_cylinder', cylinder_id=cylinder_id))

        cylinder['location'] = location
        cylinder['status'] = status
        cylinder['customer_id'] = customer_id

        save_json(cylinders, CYLINDER_DB)
        flash(f"Cylinder {cylinder_id} updated successfully", "success")
        return redirect(url_for('index'))

    return render_template('update_cylinder.html', cylinder=cylinder, customers=customers)

if __name__ == '__main__':
    initialize_databases()
    app.run(debug=True)
