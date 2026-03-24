import os
import json
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# File to store user data
USER_DATA_FILE = "user_data.json"

def load_exam_data():
    """Load all exam data"""
    return {
        # Licentiate Level (Compulsory)
        "IC-01": {"title": "Principles of Insurance", "credits": 20, "level": "Licentiate", "compulsory": True},
        "IC-02": {"title": "Practice of Life Insurance", "credits": 20, "level": "Licentiate", "compulsory": True},
        "IC-11": {"title": "Practice of General Insurance", "credits": 20, "level": "Licentiate", "compulsory": True},
        
        # Associateship Level (Compulsory)
        "IC-22": {"title": "Life Insurance Underwriting", "credits": 30, "level": "Associateship", "compulsory": True},
        "IC-26": {"title": "Life Assurance Finance", "credits": 30, "level": "Associateship", "compulsory": True},
        "IC-45": {"title": "General Insurance Underwriting", "credits": 30, "level": "Associateship", "compulsory": True},
        "IC-46": {"title": "General Insurance Accounts & Regulation", "credits": 30, "level": "Associateship", "compulsory": True},
        
        # Optional Subjects (20 credits)
        "IC-14": {"title": "Regulations of Insurance Business", "credits": 20, "level": "Optional", "compulsory": False},
        
        # Optional Subjects (30 credits)
        "IC-24": {"title": "Legal Aspects of Life Assurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-27": {"title": "Health Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-29": {"title": "General Insurance Claims", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-39": {"title": "Fraud Risk Management in Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-57": {"title": "Fire and Consequential Loss Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-67": {"title": "Marine Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-71": {"title": "Agriculture Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-72": {"title": "Motor Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-74": {"title": "Liability Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-76": {"title": "Aviation Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-77": {"title": "Engineering Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-78": {"title": "Miscellaneous Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-83": {"title": "Group Insurance & Retirement Benefits", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-88": {"title": "Marketing and Public Relations", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-90": {"title": "Human Resources Management", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-99": {"title": "Asset Management", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-102": {"title": "Insurance Business Ecosystem", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-103": {"title": "Distribution Channels Management", "credits": 30, "level": "Optional", "compulsory": False},
        "IC-104": {"title": "Products of Life Insurance", "credits": 30, "level": "Optional", "compulsory": False},
        
        # Optional Subjects (40 credits)
        "IC-85": {"title": "Reinsurance Management", "credits": 40, "level": "Optional", "compulsory": False},
        "IC-86": {"title": "Risk Management", "credits": 40, "level": "Optional", "compulsory": False},
        "IC-89": {"title": "Management Accounting", "credits": 40, "level": "Optional", "compulsory": False},
        
        # Fellowship Level (Compulsory Actuarial)
        "IC-28": {"title": "Foundation of Actuarial Science", "credits": 40, "level": "Fellowship", "compulsory": True},
        "IC-47": {"title": "Foundation of Casualty Actuarial Science I", "credits": 40, "level": "Fellowship", "compulsory": True},
        "IC-81": {"title": "Mathematical Basis of Life Assurance", "credits": 40, "level": "Fellowship", "compulsory": True},
        "IC-84": {"title": "Foundation of Casualty Actuarial Science II", "credits": 40, "level": "Fellowship", "compulsory": True},
        "IC-92": {"title": "Actuarial Aspects of Product Development", "credits": 40, "level": "Fellowship", "compulsory": True},
    }

def load_user_data(username):
    """Load user data from file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                all_data = json.load(f)
                return all_data.get(username, {
                    'passed_exams': {},
                    'profile': {
                        'name': username,
                        'email': '',
                        'registration_id': '',
                        'created_at': datetime.now().strftime("%Y-%m-%d")
                    }
                })
        except:
            pass
    return {'passed_exams': {}, 'profile': {'name': username, 'email': '', 'registration_id': '', 'created_at': datetime.now().strftime("%Y-%m-%d")}}

def save_user_data(username, data):
    """Save user data to file"""
    all_data = {}
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                all_data = json.load(f)
        except:
            pass
    
    all_data[username] = data
    
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)

def calculate_credits(passed_exams, exam_data):
    """Calculate total credits"""
    total = 0
    for exam_code, exam_info in passed_exams.items():
        if exam_info.get('passed', False) and exam_code in exam_data:
            total += exam_data[exam_code]['credits']
    return total

def get_status(passed_exams, total_credits, exam_data):
    """Determine professional status"""
    has_ic01 = passed_exams.get('IC-01', {}).get('passed', False)
    has_life = passed_exams.get('IC-02', {}).get('passed', False)
    has_general = passed_exams.get('IC-11', {}).get('passed', False)
    licentiate_compulsory = has_ic01 and (has_life or has_general)
    
    has_assoc_life = passed_exams.get('IC-22', {}).get('passed', False) and passed_exams.get('IC-26', {}).get('passed', False)
    has_assoc_nonlife = passed_exams.get('IC-45', {}).get('passed', False) and passed_exams.get('IC-46', {}).get('passed', False)
    associate_compulsory = has_assoc_life or has_assoc_nonlife
    
    actuarial = ['IC-28', 'IC-47', 'IC-81', 'IC-84', 'IC-92']
    has_actuarial = any(passed_exams.get(subj, {}).get('passed', False) for subj in actuarial)
    
    if total_credits >= 490 and has_actuarial and associate_compulsory and licentiate_compulsory:
        return "Fellowship (FIII)", 490
    elif total_credits >= 250 and associate_compulsory and licentiate_compulsory:
        return "Associateship (AIII)", 250
    elif total_credits >= 60 and licentiate_compulsory:
        return "Licentiate", 60
    else:
        return "Student", 60

def get_suggestions(passed_exams, total_credits, exam_data):
    """Generate suggestions for next exams"""
    suggestions = []
    passed_codes = [code for code, info in passed_exams.items() if info.get('passed', False)]
    
    has_ic01 = 'IC-01' in passed_codes
    has_life = 'IC-02' in passed_codes
    has_general = 'IC-11' in passed_codes
    
    if not has_ic01:
        suggestions.append({
            'code': 'IC-01',
            'title': exam_data['IC-01']['title'],
            'credits': 20,
            'reason': 'Required for Licentiate Certificate',
            'priority': 'High'
        })
    
    if not has_life and not has_general:
        suggestions.append({
            'code': 'IC-02 or IC-11',
            'title': 'Practice of Life Insurance OR Practice of General Insurance',
            'credits': 20,
            'reason': 'One of these is required for Licentiate',
            'priority': 'High'
        })
    
    if has_ic01 and (has_life or has_general) and total_credits < 60:
        needed = 60 - total_credits
        suggestions.append({
            'code': 'Optional Subjects',
            'title': 'Any optional subject (20-40 credits)',
            'credits': needed,
            'reason': f'Need {needed} more credits to complete Licentiate',
            'priority': 'High'
        })
    
    status, _ = get_status(passed_exams, total_credits, exam_data)
    if status == 'Licentiate' and total_credits >= 60:
        has_assoc_life = 'IC-22' in passed_codes and 'IC-26' in passed_codes
        has_assoc_nonlife = 'IC-45' in passed_codes and 'IC-46' in passed_codes
        
        if not has_assoc_life and not has_assoc_nonlife:
            suggestions.append({
                'code': 'IC-22 & IC-26 OR IC-45 & IC-46',
                'title': 'Associateship Compulsory Subjects (Choose Life or Non-Life stream)',
                'credits': 60,
                'reason': 'Required to complete Associateship after Licentiate',
                'priority': 'High'
            })
        elif total_credits < 250:
            needed = 250 - total_credits
            suggestions.append({
                'code': 'Optional Subjects (30-40 credits each)',
                'title': 'Additional optional subjects to reach 250 credits',
                'credits': needed,
                'reason': f'Need {needed} more credits for Associateship',
                'priority': 'Medium'
            })
    
    if status == 'Associateship (AIII)' and total_credits >= 250:
        actuarial_passed = [code for code in ['IC-28', 'IC-47', 'IC-81', 'IC-84', 'IC-92'] if code in passed_codes]
        
        if not actuarial_passed:
            suggestions.append({
                'code': 'Any Actuarial Subject',
                'title': 'Compulsory Actuarial Subject for Fellowship',
                'credits': 40,
                'reason': 'One Actuarial subject is required for Fellowship (FIII)',
                'priority': 'High'
            })
        elif total_credits < 490:
            needed = 490 - total_credits
            suggestions.append({
                'code': 'Advanced Subjects (40 credits each)',
                'title': 'Additional advanced subjects to reach 490 credits',
                'credits': needed,
                'reason': f'Need {needed} more credits for Fellowship (FIII)',
                'priority': 'Medium'
            })
    
    return suggestions

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username and password:
            # Simple password check (in production, use proper password hashing)
            user_data = load_user_data(username)
            stored_password = user_data.get('password', '')
            
            if stored_password and stored_password == password:
                session['username'] = username
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            elif not stored_password:
                # New user - create account
                user_data['password'] = password
                user_data['profile']['name'] = username
                save_user_data(username, user_data)
                session['username'] = username
                flash(f'Account created! Welcome to III Exam Tracker, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash('Please enter both username and password', 'warning')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not password:
            flash('Please fill all fields', 'warning')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            existing_user = load_user_data(username)
            if existing_user.get('password'):
                flash('Username already exists. Please login instead.', 'warning')
                return redirect(url_for('login'))
            else:
                user_data = {
                    'password': password,
                    'passed_exams': {},
                    'profile': {
                        'name': username,
                        'email': '',
                        'registration_id': '',
                        'created_at': datetime.now().strftime("%Y-%m-%d")
                    }
                }
                save_user_data(username, user_data)
                session['username'] = username
                flash(f'Account created successfully! Welcome, {username}!', 'success')
                return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """User dashboard"""
    username = session['username']
    user_data = load_user_data(username)
    exam_data = load_exam_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_exam':
            exam_code = request.form.get('exam_code')
            if exam_code and exam_code in exam_data:
                if exam_code not in user_data['passed_exams']:
                    user_data['passed_exams'][exam_code] = {
                        'passed': True,
                        'date': datetime.now().strftime("%Y-%m-%d")
                    }
                    save_user_data(username, user_data)
                    flash(f'✅ Added {exam_code} - {exam_data[exam_code]["title"]}', 'success')
                else:
                    flash(f'⚠️ {exam_code} is already in your passed list', 'warning')
        
        elif action == 'remove_exam':
            exam_code = request.form.get('exam_code')
            if exam_code in user_data['passed_exams']:
                del user_data['passed_exams'][exam_code]
                save_user_data(username, user_data)
                flash(f'🗑️ Removed {exam_code}', 'info')
        
        elif action == 'update_profile':
            user_data['profile']['email'] = request.form.get('email', '')
            user_data['profile']['registration_id'] = request.form.get('registration_id', '')
            save_user_data(username, user_data)
            flash('✅ Profile updated successfully!', 'success')
        
        return redirect(url_for('dashboard'))
    
    total_credits = calculate_credits(user_data['passed_exams'], exam_data)
    status, required = get_status(user_data['passed_exams'], total_credits, exam_data)
    suggestions = get_suggestions(user_data['passed_exams'], total_credits, exam_data)
    
    progress_percent = min(100, int((total_credits / required) * 100)) if required > 0 else 0
    
    # Get available exams (not passed yet)
    available_exams = []
    for code, exam in exam_data.items():
        if code not in user_data['passed_exams']:
            available_exams.append({'code': code, **exam})
    
    # Sort available exams by level
    level_order = {'Licentiate': 1, 'Optional': 2, 'Associateship': 3, 'Fellowship': 4}
    available_exams.sort(key=lambda x: (level_order.get(x['level'], 5), x['code']))
    
    return render_template('dashboard.html',
                         username=username,
                         user_profile=user_data['profile'],
                         passed_exams=user_data['passed_exams'],
                         exam_data=exam_data,
                         total_credits=total_credits,
                         status=status,
                         progress_percent=progress_percent,
                         credits_needed=max(0, required - total_credits),
                         suggestions=suggestions,
                         available_exams=available_exams)

@app.route('/exams')
@login_required
def exams():
    """List all exams"""
    exam_data = load_exam_data()
    username = session['username']
    user_data = load_user_data(username)
    passed_exams = user_data['passed_exams']
    
    # Group exams by level
    exams_by_level = {
        'Licentiate': [],
        'Associateship': [],
        'Optional': [],
        'Fellowship': []
    }
    
    for code, exam in exam_data.items():
        is_passed = code in passed_exams
        exams_by_level[exam['level']].append({
            'code': code,
            'title': exam['title'],
            'credits': exam['credits'],
            'compulsory': exam['compulsory'],
            'passed': is_passed
        })
    
    return render_template('exams.html', exams_by_level=exams_by_level)

@app.route('/leaderboard')
@login_required
def leaderboard():
    """Show leaderboard of top users"""
    exam_data = load_exam_data()
    leaderboard_data = []
    
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                all_users = json.load(f)
                
                for username, data in all_users.items():
                    if username != 'password':  # Skip if stored differently
                        passed_exams = data.get('passed_exams', {})
                        credits = calculate_credits(passed_exams, exam_data)
                        status, _ = get_status(passed_exams, credits, exam_data)
                        
                        leaderboard_data.append({
                            'name': data.get('profile', {}).get('name', username),
                            'username': username,
                            'credits': credits,
                            'status': status,
                            'exams_passed': len(passed_exams)
                        })
        except:
            pass
    
    leaderboard_data.sort(key=lambda x: x['credits'], reverse=True)
    
    return render_template('leaderboard.html', leaderboard=leaderboard_data[:50])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)