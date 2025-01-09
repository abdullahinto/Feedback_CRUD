from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

# Initialize SQLAlchemy instance
db = SQLAlchemy(app)

# Define the User model representing feedback entries in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key for unique identification
    product = db.Column(db.String(50), nullable=False)  # Product name, required
    message = db.Column(db.String(500), nullable=False)  # Feedback message, required

    def __repr__(self):
        return f"{self.id} - {self.product} - {self.message}"

# Define a form for user feedback input
class FeedbackForm(FlaskForm):
    product = StringField('Product Name', [DataRequired(), Length(min=6, max=50)])
    message = StringField('Your Message', [DataRequired(), Length(min=6, max=500)])
    submit = SubmitField('Submit')

# Handle form submission and display all feedback entries
@app.route('/', methods=['GET', 'POST'])
def submit():
    form = FeedbackForm()
    if form.validate_on_submit():
        # Save new feedback to the database
        user = User(product=form.product.data, message=form.message.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for your feedback!', 'success')  # Flash a success message
        return redirect(url_for('submit'))  # Redirect to refresh the page

    # Fetch all feedback entries from the database
    feedbacks = User.query.all()
    return render_template('index.html', form=form, feedbacks=feedbacks)

# Handle deletion of feedback entries
@app.route('/delete/<int:id>', methods=['POST'])
def delete_feedback(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)  # Delete the entry if it exists
        db.session.commit()
        flash('Feedback deleted successfully!', 'success')
    else:
        flash('Feedback not found!', 'error')
    return redirect(url_for('submit'))
    
# Handle editing of feedback entries
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_feedback(id):
    user = User.query.get(id)  # Fetch the feedback entry by ID
    form = FeedbackForm(request.form, obj=user)  # Populate form with existing data
    if request.method == "POST" and form.validate_on_submit():
        user.product = form.product.data  # Update product name
        user.message = form.message.data  # Update feedback message
        db.session.commit()
        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('submit'))
    return render_template('edit.html', form=form, user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if not already present
    app.run(debug=True)