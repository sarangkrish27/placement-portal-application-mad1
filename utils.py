DEPARTMENT_MAP = {
    "ai": "Artificial Intelligence",
    "bio": "Bioinformatics",
    "ce": "Computer Engineering",
    "cs": "Computer Science",
    "cy": "Cybersecurity",
    "da": "Data Analytics",
    "ds": "Data Science",
    "it": "Information Technology",
    "ml": "Machine Learning",
    "rb": "Robotics",
    "se": "Software Engineering",
    "wt": "Web Technologies"
}

def validate_smail(smail):
    if smail.endswith("@smail.nist.edu"):
        return True
    else:
        return False

def validate_department(smail):
    dept_code = smail.split("@")[0][2:-3]
    if dept_code not in DEPARTMENT_MAP:
        return False
    else:
        return True

def get_department(smail):
    dept_code = smail.split("@")[0][2:-3]
    return DEPARTMENT_MAP[dept_code]

def greet(hour):
    greeting = ""
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    elif 17 <= hour < 21:
        greeting = "Good Evening"
    else:
        greeting = "Good Night"
    return greeting