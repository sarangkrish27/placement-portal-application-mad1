from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, SelectField, IntegerField, DecimalField, FileField, URLField, TextAreaField, SelectMultipleField, DateField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange, URL
from wtforms.widgets import CheckboxInput, ListWidget
from flask_wtf.file import FileAllowed, FileSize

class LoginForm(FlaskForm):
    email = EmailField(validators=[
                           InputRequired(), Length(min=4, max=25)], render_kw={
                               "class": "rounded-pill w-100 ps-3 pe-5 mb-4",
                               "placeholder": "Enter your email"
                               })

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={
                                 "class": "rounded-pill w-100 ps-3 pe-5 mb-4",
                                 "placeholder": "Enter your password"
                                 })

    login = SubmitField('Login', render_kw={
        "class": "rounded-pill shadow",
    })

class SignupForm(FlaskForm):
    email = EmailField(validators=[
                           InputRequired(), Length(min=4, max=25)], render_kw={
                               "class": "rounded-pill w-100 ps-3 pe-5 mb-4",
                               "placeholder": "Enter your email"
                               })

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={
                                 "class": "rounded-pill w-100 ps-3 pe-5 mb-4",
                                 "placeholder": "Enter your password"
                                 })
    confirm_password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={
                                 "class": "rounded-pill w-100 ps-3 pe-5 mb-4",
                                 "placeholder": "Enter your password"
                                 })

    signup = SubmitField('Sign Up', render_kw={
        "class": "rounded-pill shadow",
    })

class StudentProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])

    degree = SelectField(
        "Degree",
        choices=[
            ("", "Select Course"),
            ("BA", "BA (Bachelor of Arts)"),
            ("BCA", "BCA (Bachelor of Computer Applications)"),
            ("BSc", "BSc (Bachelor of Science)"),
            ("BS", "BS (Bachelor of Science)"),
            ("BTech", "BTech (Bachelor of Technology)"),
            ("MCA", "MCA (Master of Computer Applications)"),
            ("MSc", "MSc (Master of Science)"),
            ("MS", "MS (Master of Science)"),
            ("MTech", "MTech (Master of Technology)"),
            ("PhD", "PhD (Doctor of Philosophy)")
        ],
        validators=[DataRequired()]
    )

    yos = IntegerField(
        "Year of Graduation",
        validators=[DataRequired(), NumberRange(min=1995, max=2030)]
    )

    cgpa = DecimalField(
        "CGPA",
        places=2,
        validators=[DataRequired(), NumberRange(min=0, max=10)]
    )

    profile = FileField(
        "Profile Picture",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Only image files are allowed!")
        ]
    )

    resume = FileField(
        "Resume",
        validators=[
            FileAllowed(["pdf", "doc", "docx"], "Only PDF, DOC, DOCX files are allowed!")
        ]
    )

    submit = SubmitField("Save changes")

class CompanyProfileForm(FlaskForm):
    company_name = StringField("Company Name", validators=[DataRequired()])

    industry = SelectField(
        "Industry",
        choices=[
            ("", "Select Industry"),
            ("Information Technology Services", "Information Technology Services"),
            ("Software Development & Engineering", "Software Development & Engineering"),
            ("Artificial Intelligence & Machine Learning", "Artificial Intelligence & Machine Learning"),
            ("Data Science & Analytics", "Data Science & Analytics"),
            ("Cybersecurity & Network Security", "Cybersecurity & Network Security"),
            ("Cloud Computing & DevOps", "Cloud Computing & DevOps"),
            ("Web & Mobile Application Development", "Web & Mobile Application Development"),
            ("Product-Based Technology Companies", "Product-Based Technology Companies"),
            ("Robotics & Automation", "Robotics & Automation"),
            ("Internet of Things (IoT)", "Internet of Things (IoT)"),
            ("Bioinformatics & Health Technology", "Bioinformatics & Health Technology"),
            ("FinTech", "FinTech"),
            ("EdTech", "EdTech"),
            ("E-Commerce & Digital Platforms", "E-Commerce & Digital Platforms"),
            ("Gaming & Simulation", "Gaming & Simulation"),
            ("Telecommunications", "Telecommunications"),
            ("Embedded Systems & Hardware Design", "Embedded Systems & Hardware Design"),
            ("Research & Development (R&D)", "Research & Development (R&D)"),
            ("Consulting & Professional Services", "Consulting & Professional Services"),
            ("PStartup & Innovation EcosystemhD", "Startup & Innovation Ecosystem")
        ],
        validators=[DataRequired()]
    )

    description = StringField("Description", validators=[DataRequired()])
    hr_name = StringField("HR Name", validators=[DataRequired()])
    website = URLField("Website", validators=[DataRequired(), URL()])

    profile = FileField(
        "Profile Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Only image files are allowed!")]
    )

    submit = SubmitField("Save changes")

class MultiCheckboxField(SelectMultipleField):
    """A SelectMultipleField rendered as a list of checkboxes."""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
 
 
DEGREE_CHOICES = [
    ('BTech', 'BTech'),
    ('BS', 'BS'),
    ('BSc', 'BSc'),
    ('BCA', 'BCA'),
    ('MTech', 'MTech'),
    ('MS', 'MS'),
    ('MSc', 'MSc'),
    ('MCA', 'MCA'),
]
 
DEPARTMENT_CHOICES = [
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Bioinformatics', 'Bioinformatics'),
    ('Computer Engineering', 'Computer Engineering'),
    ('Computer Science', 'Computer Science'),
    ('Cybersecurity', 'Cybersecurity'),
    ('Data Analytics', 'Data Analytics'),
    ('Data Science', 'Data Science'),
    ('Information Technology', 'Information Technology'),
    ('Machine Learning', 'Machine Learning'),
    ('Robotics', 'Robotics'),
    ('Software Engineering', 'Software Engineering'),
    ('Web Technologies', 'Web Technologies'),
]
 
WORK_MODE_CHOICES = [
    ('', 'Select Work Mode'),
    ('On-Site', 'On-Site'),
    ('Remote', 'Remote'),
    ('Hybrid', 'Hybrid'),
]
 
JOB_TYPE_CHOICES = [
    ('', 'Select Job Type'),
    ('Full-Time', 'Full-Time'),
    ('Internship', 'Internship'),
    ('Part-Time', 'Part-Time'),
    ('Contract', 'Contract'),
]
 
 
class PlacementDriveForm(FlaskForm):
    job_title = StringField(
        'Job Title',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Job Title'}
    )
    job_location = StringField(
        'Location',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Location'}
    )
    job_mode = SelectField(
        'Work Mode',
        choices=WORK_MODE_CHOICES,
        validators=[DataRequired()]
    )
    job_type = SelectField(
        'Job Type',
        choices=JOB_TYPE_CHOICES,
        validators=[DataRequired()]
    )
    job_description = TextAreaField(
        'Job Description',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Job Description'}
    )
    key_responsibility = TextAreaField(
        'Key Responsibilities',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Key Responsibilities'}
    )
    eligible_degrees = SelectMultipleField(
        'Eligible Degree(s)',
        choices=DEGREE_CHOICES,
        validators=[DataRequired()]
    )
    preferred_departments = SelectMultipleField(
        'Preferred Department(s)',
        choices=DEPARTMENT_CHOICES,
        validators=[DataRequired()]
    )

    cgpa = DecimalField(
        'Minimum CGPA',
        validators=[DataRequired(), NumberRange(min=0, max=10)],
        places=2
    )
    other_eligibility = TextAreaField(
        'Other Eligibility',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Other Eligibility'}
    )
    required_skills = TextAreaField(
        'Required Technical Skills',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Required Technical Skills'}
    )
    preferred_skills = TextAreaField(
        'Preferred Skills',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Preferred Skills'}
    )
    compensation_benefits = TextAreaField(
        'Compensation & Benefits',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter Compensation & Benefits'}
    )
    application_deadline = DateField(
        'Application Deadline',
        validators=[DataRequired()]
    )
    submit = SubmitField('Create Drive')
 