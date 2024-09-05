from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Student, Company, Internship, init_db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

@app.route('/')
def index():
    return render_template('welcome.html')

# /------------------------------------------Student------------------------------------------------/

@app.route('/student_logout')
def student_logout():
    # Clear the session data
    session.pop('user_id', None)  # Remove user_id from session
    return render_template('student_logout.html')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        student = Student.query.filter_by(email=email, password=password).first()
        if student:
            session['student_id'] = student.id
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('student_login'))
    return render_template('student_login.html')

@app.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        course_of_study = request.form['course_of_study']
        skills = request.form['skills']
        bio = request.form['bio']
        location_of_interest = request.form['location_of_interest']
        new_student = Student(name=name, email=email, password=password, course_of_study=course_of_study, skills=skills, bio=bio, location_of_interest=location_of_interest)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('student_login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please use a different email.', 'error')

    return render_template('student_signup.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    student = db.session.get(Student, session['student_id'])
    return render_template('student_dashboard.html', student=student)

@app.route('/edit_student_profile', methods=['GET', 'POST'])
def edit_student_profile():
    student = db.session.get(Student, session['student_id'])
    
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.bio = request.form['bio']
        student.location_of_interest = request.form['location_of_interest']
        student.skills = request.form['skills']
        student.password = request.form['password']
        student.course_of_study = request.form['course_of_study']
        student.password = request.form['password']

        db.session.commit()
        return redirect(url_for('student_dashboard'))
    
    return render_template('edit_student_profile.html', student=student)

# /------------------------------------------Student------------------------------------------------/

# /------------------------------------------Company------------------------------------------------/

@app.route('/company_logout')
def company_logout():
    # Clear the session data
    session.pop('user_id', None)  # Remove user_id from session
    return render_template('company_logout.html')

@app.route('/company_login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        company = Company.query.filter_by(email=email, password=password).first()
        if company:
            session['company_id'] = company.id
            return redirect(url_for('company_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('company_login'))
    return render_template('company_login.html')

@app.route('/company_signup', methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        industry = request.form.get('industry')
        location = request.form.get('location')
        about = request.form.get('about')
        website = request.form.get('website')
        new_company = Company(email=email, name=name, password=password, about=about, website=website, industry=industry, location=location)

        try:
            db.session.add(new_company)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('company_login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please use a different email.', 'error')

    return render_template('company_signup.html')

@app.route('/company_dashboard')
def company_dashboard():
    if 'company_id' not in session:
        return redirect(url_for('company_login'))

    company = db.session.get(Company, session['company_id'])
    internships = Internship.query.filter_by(company_id=company.id).all()

    return render_template('company_dashboard.html', company=company, internships=internships)

@app.route('/edit_company_profile', methods=['GET', 'POST'])
def edit_company_profile():
    company = db.session.get(Company, session['company_id'])

    if request.method == 'POST':
        company.name = request.form['name']
        company.email = request.form['email']
        company.about = request.form['about']
        company.location = request.form['location']
        company.website = request.form['website']
        company.password = request.form['password']
        company.industry = request.form['industry']

        db.session.commit()
        return redirect(url_for('company_dashboard'))

    return render_template('edit_company_profile.html', company=company)

# /------------------------------------------Company------------------------------------------------/

# /------------------------------------------Recommend----------------------------------------------/

@app.route('/recommender')
def recommender():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student = db.session.get(Student, session['student_id'])
    
    # Fetch all internships with their associated company details
    internships = db.session.query(Internship, Company).join(Company).filter(
        Internship.company_id == Company.id
    ).all()
    
    # Process and filter internships based on student skills
    filtered_internships = []
    student_skills = set(student.skills.lower().split(', '))  # Assuming skills are comma-separated
    
    for internship, company in internships:
        requirements = internship.requirements.lower()
        if any(skill.lower() in requirements for skill in student_skills):
            filtered_internships.append((internship, company))
    
    return render_template('recommender.html', student=student, recommendations=filtered_internships)


# /------------------------------------------Recommend----------------------------------------------/

# /------------------------------------------Internship---------------------------------------------/

@app.route('/post_internship', methods=['GET', 'POST'])
def post_internship():
    company = db.session.get(Company, session['company_id'])
    if request.method == 'POST':
        role = request.form.get('role')
        description = request.form.get('description')
        location = request.form.get('location')
        start_date_str = request.form.get('start_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        duration = request.form.get('duration')
        requirements = request.form.get('requirements')
        new_internship = Internship(role=role, description=description, location=location, company_id=company.id, start_date=start_date, duration=duration, requirements=requirements)
        print(new_internship)
        db.session.add(new_internship)
        db.session.commit()
        return redirect(url_for('company_dashboard'))
    return render_template('post_internship.html')

@app.route('/delete_internship/<int:internship_id>', methods=['POST'])
def delete_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if internship:
        db.session.delete(internship)
        db.session.commit()
    else:
        flash('Internship not found.', 'error')
    return redirect(url_for('company_dashboard'))

@app.route('/edit_internship/<int:internship_id>', methods=['GET', 'POST'])
def edit_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if internship.company_id != session.get('company_id'):
        flash('You do not have permission to edit this internship.', 'error')
        return redirect(url_for('company_dashboard'))
    
    if request.method == 'POST':
        internship.role = request.form.get('role')
        internship.description = request.form.get('description')
        internship.location = request.form.get('location')
        # Convert the string date to a Python date object
        start_date_str = request.form.get('start_date')
        internship.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        internship.duration = request.form.get('duration')
        internship.requirements = request.form.get('requirements')

        db.session.commit()
        flash('Internship updated successfully.', 'success')
        return redirect(url_for('company_dashboard'))
    
    return render_template('edit_internship.html', internship=internship)

# /-----------------------------------------Internship---------------------------------------------/

if __name__ == '__main__':
    app.run(debug=True)