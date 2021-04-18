from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, session
from filters import datetimeformat, file_type
from resources import get_bucket
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type


@app.route('/')
def index():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('index.html', my_bucket=my_bucket, files=summaries, params=params)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if "user" in session and session['user'] == params['admin_user']:
        my_bucket = get_bucket()
        summaries = my_bucket.objects.all()
        return render_template("dashboard.html", params=params, my_bucket=my_bucket, files=summaries)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            my_bucket = get_bucket()
            summaries = my_bucket.objects.all()
            return render_template("dashboard.html", params=params, my_bucket=my_bucket, files=summaries)
        else:
            flash('Invalid Credentials')
            return render_template("login.html", params=params)
    return render_template("login.html", params=params)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if "user" in session and session['user'] == params['admin_user']:
        if(request.method == "POST"):
            file = request.files['file']
            my_bucket = get_bucket()
            my_bucket.Object(file.filename).put(Body=file)

            flash('File uploaded successfully')
            return redirect(url_for('dashboard'))
    else:
        file = request.files['file']
        my_bucket = get_bucket()
        my_bucket.Object(file.filename).put(Body=file)

        flash('File uploaded successfully')
        return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('dashboard'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=True)
