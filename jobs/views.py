from jobs import *

@app.route('/')
def index():
    return render_template('index.html')


# user functions


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == "POST":
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm = request.form['confirm']
            
            if len(username) > 4 and len(username) < 20:
                if len(email) > 4 and len(email) < 50:
                    if len(password) > 4 and len(password) < 50 and password == confirm:
                        hashedpw = sha256_crypt.encrypt(password)
                        
                        newUser = User(username, email, hashedpw)
                        db.session.add(newUser)
                        db.session.flush()
                        db.session.commit()
                        
                        session['logged_in'] = True
                        session['username'] = username
                        
                        flash('You successfully registered')
                        return redirect(url_for('index'))
                        
                    else:
                        flash('Your passwords must match and be between 4 and 50 characters')
                        return redirect(url_for('signup'))
                        
                else:
                    flash('Your email must be between 4 and 50 characters')
                    return redirect(url_for('signup'))
            else:
                flash('Your username must be between 4 and 20 characters')
                return redirect(url_for('signup'))
            
        
        return render_template("signup.html")
        
    except Exception as e:
        return str(e)
    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter(User.username == username).first()
            
            if user:
                if sha256_crypt.verify(password, user.password):
                    session['logged_in'] = True
                    session['username'] = username
                    
                    flash('You are now logged in!')
                    return redirect(url_for('index'))
                else:
                    flash('Password is incorrect')
                    return redirect(url_for('login'))
                
            else:
                flash('That user does not exist!')
                return redirect(url_for('login'))
            
        return render_template('login.html')
    except Exception as e:
        return str(e)
    
    
@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You are now logged out!')
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        username = session['username']
        listings = Job.query.filter(Job.job_poster == username).order_by("job_posted asc").all()
        applications = Application.query.filter(Application.applicant == username).order_by("date_applied asc").all()
        return render_template('dashboard.html', listings=listings, applications=applications)
        
    except Exception as e:
        return str(e)
    
    
@app.route('/delete/profile/')
def delete_profile():
    try:
        username = session['username']
        user = User.query.filter(User.username == username).first()
        db.session.delete(user)
        db.session.commit()
        db.session.flush()
          
        session.clear()
        flash('Your account has been deleted. We hope to see you again.')
        return redirect(url_for('index'))
    
    except Exception as e:
        return str(e)
    
@app.route('/edit/profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    try:
        username = session['username']
        user = User.query.filter(User.username == username).first()
        
        if request.method == "POST":
            if request.form['username'] or request.form['email']:
                username = request.form['username']
                email = request.form['email']
                
                
                user.username = username
                user.email = email
                db.session.commit()
                db.session.flush()
                session['username'] = username
                flash('Changes saved!')
                redirect(url_for('dashboard'))
           
                    
            else:
                redirect(url_for('dashboard'))
        
        
        
        return render_template('edit.html', user=user)
    except Exception as e:
        return str(e)
    
#end user funcs

#job funcs n stuff

@app.route('/new/job/', methods=['GET', 'POST'])
@login_required
def new_job():
    
    try:
        categories = Category.query.all()
        
        if request.method == "POST":
            job_name = request.form['job_name']
            job_desc = request.form['job_desc']
            job_posted = datetime.now()
            job_poster = session['username']
            category = str(request.form.get('category'))
            fulfilled = False
            
            
            if len(job_name) > 5 and len(job_desc) > 5 and category:
                newJob = Job(job_name, job_poster, job_posted, category, job_desc, fulfilled)
                db.session.add(newJob)
                db.session.flush()
                db.session.commit()
                
                flash('Job listing added!')
                return redirect(url_for('dashboard'))
            
            else:
                flash('Please correct the errors with your listing')
                return redirect(url_for('new_job'))
            
        return render_template('newjob.html', categories=categories)
    
    except Exception as e:
        return str(e)
    
@app.route('/show/<category_id>/')
def show(category_id):
    try:
        category = ''
        if category_id == "1":
            category = 'All'
            listings = Job.query.all()
            
        else:
            category = Category.query.filter(Category.id == category_id).first()
            category = category.cat_name
            listings = Job.query.filter(Job.category == category).all()
        
        return render_template('show.html', category=category, listings=listings)
        
    except Exception as e:
        return str(e)
    
    
@app.route('/job/<job_id>')
def show_job(job_id):
    
    try:
        
        job = Job.query.filter(Job.id == job_id).first()
        
        
        return render_template('job.html', job=job)
        
        
    except Exception as e:
        return str(e)
    
@app.route('/delete/<job_id>')
@login_required
def delete_job(job_id):
    try:
        job = Job.query.get(job_id)
        db.session.delete(job)
        db.session.flush()
        db.session.commit()
        
        flash('Job deleted!')
        return redirect(url_for('dashboard'))
    except Exception as e:
        return str(e)
    
    
@app.route('/apply/<job_id>/', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    try:
        
        if request.method == "POST":
            if request.form['message']:
                message = request.form['message']
                date_applied = datetime.now()
                applicant = session['username']
                for_listing = job_id
                
                
                newApp = Application(applicant, message, date_applied, for_listing)
                db.session.add(newApp)
                db.session.flush()
                db.session.commit()
                
                
                flash('Your application has been received! You will receive a response')
                return redirect(url_for('dashboard'))
                
            else:
                flash('You have not filled out your application')
                return redirect(url_for('apply_job'))

            
            
        
        
        return render_template('apply.html', job_id=job_id)
        
    except Exception as e:
        return str(e)
        
@app.route('/application/<app_id>/')
@login_required
def view_app(app_id):
    try:
        
        appl = Application.query.get(app_id)
        
        
        job = Job.query.get(appl.id)
        
        
        return render_template('application.html', appl=appl, job=job)
        
        
    except Exception as e:
        return str(e)
    
@app.route('/delete/app/<app_id>/')
@login_required
def delete_app(app_id):
    try:
        
        appl = Application.query.get(app_id)
        db.session.delete(appl)
        db.session.flush()
        db.session.commit()
        
        flash('Your application has been rescinded')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        return str(e)