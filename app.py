from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/images'

# Hardcoded admin credentials (for demo only)
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': '12345'
}

# Mock database (in a real app, use a proper database)
users_db = {}
lands_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html')

@app.route('/admin/government-approval')
def government_approval():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin/government.html', lands=lands_db)

@app.route('/admin/register-land', methods=['GET', 'POST'])
def register_land():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Handle land registration
        aadhaar = request.form['aadhaar']
        owner_name = request.form['owner_name']
        location = request.form['location']
        area = request.form['area']
        price = request.form['price']
        
        # Handle file upload
        if 'land_image' in request.files:
            file = request.files['land_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                land_image = filename
        
        # Store in mock database (in real app, use blockchain)
        land_id = len(lands_db) + 1
        lands_db[land_id] = {
            'id': land_id,
            'aadhaar': aadhaar,
            'owner_name': owner_name,
            'location': location,
            'area': area,
            'price': price,
            'image': land_image,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'verified': False,
            'action': 'pending',  # New field to track accept/reject status
            'gov_approval': 'pending'  # New field for government approval status
        }
        
        flash('Land registered successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/register_land.html')

@app.route('/admin/register-user', methods=['GET', 'POST'])
def register_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo = filename
        
        # Store in mock database
        users_db[aadhaar] = {
            'aadhaar': aadhaar,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'photo': photo,
            'lands': [],
            'gov_approval': 'pending'  # New field for government approval status
        }
        
        flash('User registered successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Pass default user object to avoid template error
    return render_template('admin/register_user.html', user={'gov_approval': 'pending'})

@app.route('/admin/view-records')
def view_records():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin/view_records.html', lands=lands_db)

@app.route('/admin/transfer-land', methods=['GET', 'POST'])
def transfer_land():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        land_id = int(request.form['land_id'])
        new_aadhaar = request.form['new_aadhaar']
        
        if land_id in lands_db:
            lands_db[land_id]['aadhaar'] = new_aadhaar
            lands_db[land_id]['owner_name'] = users_db.get(new_aadhaar, {}).get('name', 'Unknown')
            flash('Land transferred successfully!', 'success')
        else:
            flash('Land ID not found!', 'danger')
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/transfer_land.html', lands=lands_db)

@app.route('/admin/land/accept/<int:land_id>')
def accept_land(land_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if land_id in lands_db:
        lands_db[land_id]['action'] = 'accepted'
        lands_db[land_id]['verified'] = True
        flash(f'Land ID {land_id} has been accepted.', 'success')
    else:
        flash('Land ID not found!', 'danger')
    return redirect(url_for('view_records'))

@app.route('/admin/land/reject/<int:land_id>')
def reject_land(land_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if land_id in lands_db:
        lands_db[land_id]['action'] = 'rejected'
        lands_db[land_id]['verified'] = False
        flash(f'Land ID {land_id} has been rejected.', 'warning')
    else:
        flash('Land ID not found!', 'danger')
    return redirect(url_for('view_records'))

# New routes for government approval of land
@app.route('/admin/land/gov-approve/<int:land_id>')
def gov_approve_land(land_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if land_id in lands_db:
        lands_db[land_id]['gov_approval'] = 'approved'
        flash(f'Government approval granted for Land ID {land_id}.', 'success')
    else:
        flash('Land ID not found!', 'danger')
    return redirect(url_for('view_records'))

@app.route('/admin/land/gov-reject/<int:land_id>')
def gov_reject_land(land_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if land_id in lands_db:
        lands_db[land_id]['gov_approval'] = 'rejected'
        flash(f'Government approval rejected for Land ID {land_id}.', 'warning')
    else:
        flash('Land ID not found!', 'danger')
    return redirect(url_for('view_records'))

# New routes for government approval of user
@app.route('/admin/user/gov-approve/<string:aadhaar>')
def gov_approve_user(aadhaar):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if aadhaar in users_db:
        users_db[aadhaar]['gov_approval'] = 'approved'
        flash(f'Government approval granted for User {aadhaar}.', 'success')
    else:
        flash('User not found!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/gov-reject/<string:aadhaar>')
def gov_reject_user(aadhaar):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if aadhaar in users_db:
        users_db[aadhaar]['gov_approval'] = 'rejected'
        flash(f'Government approval rejected for User {aadhaar}.', 'warning')
    else:
        flash('User not found!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        # In a real app, add proper authentication
        if aadhaar in users_db:
            session['user_aadhaar'] = aadhaar
            return redirect(url_for('user_dashboard'))
        else:
            flash('Aadhaar not registered!', 'danger')
    return render_template('user/login.html')

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo = filename
        
        # Store in mock database
        users_db[aadhaar] = {
            'aadhaar': aadhaar,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'photo': photo,
            'lands': []
        }
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))
    
    return render_template('user/register.html')

@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_aadhaar'):
        return redirect(url_for('user_login'))
    
    aadhaar = session['user_aadhaar']
    user_lands = [land for land in lands_db.values() if land['aadhaar'] == aadhaar]
    
    return render_template('user/dashboard.html', 
                         user=users_db.get(aadhaar, {}),
                         lands=user_lands)

@app.route('/user/logout')
def user_logout():
    session.pop('user_aadhaar', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
