import numpy as np
import scipy as sp
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import pickle
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # change this for security

# Load model
model = pickle.load(open('model.pkl', 'rb'))

# ===================== DB SETUP =====================

DB_NAME = 'users.db'


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def create_user(username, email, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password))
    conn.commit()
    conn.close()


# Initialize DB once at startup
init_db()

# ===================== ROUTES =====================


@app.route('/')
def home_redirect():
    # Redirect root to login or dashboard based on session
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user_by_username(username)
        if user and user[3] == password:  # user[3] is password (plain text here, only for demo!)
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "danger")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            flash("Passwords do not match", "danger")
            return render_template('register.html')

        existing = get_user_by_username(username)
        if existing:
            flash("Username already exists", "danger")
            return render_template('register.html')

        create_user(username, email, password)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = {
        'username': session.get('username'),
        'email': session.get('email')
    }
    # dashboard and prediction form in same page (index.html)
    return render_template('index.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'email': session.get('email')
    }
    return render_template('userprofile.html', user=user)


@app.route('/predict', methods=['POST'])
def predict():
    """
    For rendering results on HTML GUI
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # ============= Get form values =============
    Age = int(request.form.get("Age"))
    BusinessTravel = request.form['BusinessTravel']
    DailyRate = int(request.form.get('DailyRate'))
    Department = request.form['Department']
    DistanceFromHome = int(request.form.get("DistanceFromHome"))
    Education = int(request.form.get("Education"))
    EducationField = request.form['EducationField']
    EnvironmentSatisfaction = int(request.form.get("EnvironmentSatisfaction"))
    Gender = request.form['Gender']
    HourlyRate = int(request.form.get("HourlyRate"))
    JobInvolvement = int(request.form.get("JobInvolvement"))
    JobLevel = int(request.form.get("JobLevel"))
    JobRole = request.form['JobRole']
    JobSatisfaction = int(request.form.get("JobSatisfaction"))
    MaritalStatus = request.form['MaritalStatus']
    MonthlyIncome = int(request.form.get("MonthlyIncome"))
    NumCompaniesWorked = int(request.form.get("NumCompaniesWorked"))
    OverTime = request.form['OverTime']
    PerformanceRating = int(request.form.get("PerformanceRating"))
    RelationshipSatisfaction = int(request.form.get("RelationshipSatisfaction"))
    StockOptionLevel = int(request.form.get("StockOptionLevel"))
    TotalWorkingYears = int(request.form.get("TotalWorkingYears"))
    TrainingTimesLastYear = int(request.form.get("TrainingTimesLastYear"))
    WorkLifeBalance = int(request.form.get("WorkLifeBalance"))
    YearsAtCompany = int(request.form.get("YearsAtCompany"))
    YearsInCurrentRole = int(request.form.get("YearsInCurrentRole"))
    YearsSinceLastPromotion = int(request.form.get("YearsSinceLastPromotion"))
    YearsWithCurrManager = int(request.form.get("YearsWithCurrManager"))

    input_data = {
        'Age': Age,
        'BusinessTravel': BusinessTravel,
        'DailyRate': DailyRate,
        'Department': Department,
        'DistanceFromHome': DistanceFromHome,
        'Education': Education,
        'EducationField': EducationField,
        'EnvironmentSatisfaction': EnvironmentSatisfaction,
        'Gender': Gender,
        'HourlyRate': HourlyRate,
        'JobInvolvement': JobInvolvement,
        'JobLevel': JobLevel,
        'JobRole': JobRole,
        'JobSatisfaction': JobSatisfaction,
        'MaritalStatus': MaritalStatus,
        'MonthlyIncome': MonthlyIncome,
        'NumCompaniesWorked': NumCompaniesWorked,
        'OverTime': OverTime,
        'PerformanceRating': PerformanceRating,
        'RelationshipSatisfaction': RelationshipSatisfaction,
        'StockOptionLevel': StockOptionLevel,
        'TotalWorkingYears': TotalWorkingYears,
        'TrainingTimesLastYear': TrainingTimesLastYear,
        'WorkLifeBalance': WorkLifeBalance,
        'YearsAtCompany': YearsAtCompany,
        'YearsInCurrentRole': YearsInCurrentRole,
        'YearsSinceLastPromotion': YearsSinceLastPromotion,
        'YearsWithCurrManager': YearsWithCurrManager
    }

    df = pd.DataFrame([input_data])

    # ============= Feature Engineering (same as your code) =============
    df['Total_Satisfaction'] = (
        df['EnvironmentSatisfaction'] +
        df['JobInvolvement'] +
        df['JobSatisfaction'] +
        df['RelationshipSatisfaction'] +
        df['WorkLifeBalance']
    ) / 5

    df.drop(
        ['EnvironmentSatisfaction', 'JobInvolvement', 'JobSatisfaction',
         'RelationshipSatisfaction', 'WorkLifeBalance'],
        axis=1, inplace=True
    )

    df['Total_Satisfaction_bool'] = df['Total_Satisfaction'].apply(lambda x: 1 if x >= 2.8 else 0)
    df.drop('Total_Satisfaction', axis=1, inplace=True)

    df['Age_bool'] = df['Age'].apply(lambda x: 1 if x < 35 else 0)
    df.drop('Age', axis=1, inplace=True)

    df['DailyRate_bool'] = df['DailyRate'].apply(lambda x: 1 if x < 800 else 0)
    df.drop('DailyRate', axis=1, inplace=True)

    df['Department_bool'] = df['Department'].apply(lambda x: 1 if x == 'Research & Development' else 0)
    df.drop('Department', axis=1, inplace=True)

    df['DistanceFromHome_bool'] = df['DistanceFromHome'].apply(lambda x: 1 if x > 10 else 0)
    df.drop('DistanceFromHome', axis=1, inplace=True)

    df['JobRole_bool'] = df['JobRole'].apply(lambda x: 1 if x == 'Laboratory Technician' else 0)
    df.drop('JobRole', axis=1, inplace=True)

    df['HourlyRate_bool'] = df['HourlyRate'].apply(lambda x: 1 if x < 65 else 0)
    df.drop('HourlyRate', axis=1, inplace=True)

    df['MonthlyIncome_bool'] = df['MonthlyIncome'].apply(lambda x: 1 if x < 4000 else 0)
    df.drop('MonthlyIncome', axis=1, inplace=True)

    df['NumCompaniesWorked_bool'] = df['NumCompaniesWorked'].apply(lambda x: 1 if x > 3 else 0)
    df.drop('NumCompaniesWorked', axis=1, inplace=True)

    df['TotalWorkingYears_bool'] = df['TotalWorkingYears'].apply(lambda x: 1 if x < 8 else 0)
    df.drop('TotalWorkingYears', axis=1, inplace=True)

    df['YearsAtCompany_bool'] = df['YearsAtCompany'].apply(lambda x: 1 if x < 3 else 0)
    df.drop('YearsAtCompany', axis=1, inplace=True)

    df['YearsInCurrentRole_bool'] = df['YearsInCurrentRole'].apply(lambda x: 1 if x < 3 else 0)
    df.drop('YearsInCurrentRole', axis=1, inplace=True)

    df['YearsSinceLastPromotion_bool'] = df['YearsSinceLastPromotion'].apply(lambda x: 1 if x < 1 else 0)
    df.drop('YearsSinceLastPromotion', axis=1, inplace=True)

    df['YearsWithCurrManager_bool'] = df['YearsWithCurrManager'].apply(lambda x: 1 if x < 1 else 0)
    df.drop('YearsWithCurrManager', axis=1, inplace=True)

    # BusinessTravel one-hot
    if BusinessTravel == 'Rarely':
        df['BusinessTravel_Rarely'] = 1
        df['BusinessTravel_Frequently'] = 0
        df['BusinessTravel_No_Travel'] = 0
    elif BusinessTravel == 'Frequently':
        df['BusinessTravel_Rarely'] = 0
        df['BusinessTravel_Frequently'] = 1
        df['BusinessTravel_No_Travel'] = 0
    else:
        df['BusinessTravel_Rarely'] = 0
        df['BusinessTravel_Frequently'] = 0
        df['BusinessTravel_No_Travel'] = 1
    df.drop('BusinessTravel', axis=1, inplace=True)

    # Education one-hot
    if Education == 1:
        df['Education_1'] = 1
        df['Education_2'] = 0
        df['Education_3'] = 0
        df['Education_4'] = 0
        df['Education_5'] = 0
    elif Education == 2:
        df['Education_1'] = 0
        df['Education_2'] = 1
        df['Education_3'] = 0
        df['Education_4'] = 0
        df['Education_5'] = 0
    elif Education == 3:
        df['Education_1'] = 0
        df['Education_2'] = 0
        df['Education_3'] = 1
        df['Education_4'] = 0
        df['Education_5'] = 0
    elif Education == 4:
        df['Education_1'] = 0
        df['Education_2'] = 0
        df['Education_3'] = 0
        df['Education_4'] = 1
        df['Education_5'] = 0
    else:
        df['Education_1'] = 0
        df['Education_2'] = 0
        df['Education_3'] = 0
        df['Education_4'] = 0
        df['Education_5'] = 1
    df.drop('Education', axis=1, inplace=True)

    # EducationField
    if EducationField == 'Life Sciences':
        df['EducationField_Life_Sciences'] = 1
        df['EducationField_Medical'] = 0
        df['EducationField_Marketing'] = 0
        df['EducationField_Technical_Degree'] = 0
        df['Education_Human_Resources'] = 0
        df['Education_Other'] = 0
    elif EducationField == 'Medical':
        df['EducationField_Life_Sciences'] = 0
        df['EducationField_Medical'] = 1
        df['EducationField_Marketing'] = 0
        df['EducationField_Technical_Degree'] = 0
        df['Education_Human_Resources'] = 0
        df['Education_Other'] = 0
    elif EducationField == 'Marketing':
        df['EducationField_Life_Sciences'] = 0
        df['EducationField_Medical'] = 0
        df['EducationField_Marketing'] = 1
        df['EducationField_Technical_Degree'] = 0
        df['Education_Human_Resources'] = 0
        df['Education_Other'] = 0
    elif EducationField == 'Technical Degree':
        df['EducationField_Life_Sciences'] = 0
        df['EducationField_Medical'] = 0
        df['EducationField_Marketing'] = 0
        df['EducationField_Technical_Degree'] = 1
        df['Education_Human_Resources'] = 0
        df['Education_Other'] = 0
    elif EducationField == 'Human Resources':
        df['EducationField_Life_Sciences'] = 0
        df['EducationField_Medical'] = 0
        df['EducationField_Marketing'] = 0
        df['EducationField_Technical_Degree'] = 0
        df['Education_Human_Resources'] = 1
        df['Education_Other'] = 0
    else:
        df['EducationField_Life_Sciences'] = 0
        df['EducationField_Medical'] = 0
        df['EducationField_Marketing'] = 0
        df['EducationField_Technical_Degree'] = 0
        df['Education_Human_Resources'] = 0
        df['Education_Other'] = 1
    df.drop('EducationField', axis=1, inplace=True)

    # Gender
    if Gender == 'Male':
        df['Gender_Male'] = 1
        df['Gender_Female'] = 0
    else:
        df['Gender_Male'] = 0
        df['Gender_Female'] = 1
    df.drop('Gender', axis=1, inplace=True)

    # Marital Status
    if MaritalStatus == 'Married':
        df['MaritalStatus_Married'] = 1
        df['MaritalStatus_Single'] = 0
        df['MaritalStatus_Divorced'] = 0
    elif MaritalStatus == 'Single':
        df['MaritalStatus_Married'] = 0
        df['MaritalStatus_Single'] = 1
        df['MaritalStatus_Divorced'] = 0
    else:
        df['MaritalStatus_Married'] = 0
        df['MaritalStatus_Single'] = 0
        df['MaritalStatus_Divorced'] = 1
    df.drop('MaritalStatus', axis=1, inplace=True)

    # Overtime
    if OverTime == 'Yes':
        df['OverTime_Yes'] = 1
        df['OverTime_No'] = 0
    else:
        df['OverTime_Yes'] = 0
        df['OverTime_No'] = 1
    df.drop('OverTime', axis=1, inplace=True)

    # Stock Option Level
    if StockOptionLevel == 0:
        df['StockOptionLevel_0'] = 1
        df['StockOptionLevel_1'] = 0
        df['StockOptionLevel_2'] = 0
        df['StockOptionLevel_3'] = 0
    elif StockOptionLevel == 1:
        df['StockOptionLevel_0'] = 0
        df['StockOptionLevel_1'] = 1
        df['StockOptionLevel_2'] = 0
        df['StockOptionLevel_3'] = 0
    elif StockOptionLevel == 2:
        df['StockOptionLevel_0'] = 0
        df['StockOptionLevel_1'] = 0
        df['StockOptionLevel_2'] = 1
        df['StockOptionLevel_3'] = 0
    else:
        df['StockOptionLevel_0'] = 0
        df['StockOptionLevel_1'] = 0
        df['StockOptionLevel_2'] = 0
        df['StockOptionLevel_3'] = 1
    df.drop('StockOptionLevel', axis=1, inplace=True)

    # Training Time Last Year
    if TrainingTimesLastYear == 0:
        df['TrainingTimesLastYear_0'] = 1
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 0
    elif TrainingTimesLastYear == 1:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 1
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 0
    elif TrainingTimesLastYear == 2:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 1
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 0
    elif TrainingTimesLastYear == 3:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 1
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 0
    elif TrainingTimesLastYear == 4:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 1
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 0
    elif TrainingTimesLastYear == 5:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 1
        df['TrainingTimesLastYear_6'] = 0
    else:
        df['TrainingTimesLastYear_0'] = 0
        df['TrainingTimesLastYear_1'] = 0
        df['TrainingTimesLastYear_2'] = 0
        df['TrainingTimesLastYear_3'] = 0
        df['TrainingTimesLastYear_4'] = 0
        df['TrainingTimesLastYear_5'] = 0
        df['TrainingTimesLastYear_6'] = 1
    df.drop('TrainingTimesLastYear', axis=1, inplace=True)

    # ============= Predict =============
    prediction = model.predict(df)[0]

    if prediction == 0:
        result_text = """
        <b style='color:green;'>Employee is likely to stay in the organization.</b><br><br>
        ✔ Good job satisfaction and engagement indicators.<br>
        ✔ No major risk factors identified currently.<br><br>
        <b>Recommendations:</b><br>
        🔹 Continue employee motivation & recognition activities.<br>
        🔹 Provide growth and learning opportunities.<br>
        🔹 Maintain flexible and positive work environment.
        """
    else:
        result_text = """
        <b style='color:red;'>⚠ Employee is at high risk of leaving the organization!</b><br><br>
        <b>Possible Reasons:</b><br>
        🔸 Low satisfaction / high workload / imbalance<br>
        🔸 Compensation or recognition issues<br>
        🔸 Limited growth opportunities or job role mismatch<br><br>
        <b>Suggested HR Actions:</b><br>
        💡 Arrange a personal feedback meeting<br>
        💡 Offer upskilling / career growth roadmap<br>
        💡 Improve team collaboration and flexibility<br>
        💡 Review pay benefits if required
        """


    user = {
        'username': session.get('username'),
        'email': session.get('email')
    }

    return render_template('index.html', prediction_text=result_text, user=user)


if __name__ == "__main__":
    app.run(debug=True)
