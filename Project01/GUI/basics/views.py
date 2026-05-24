from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required



from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


def crop_prediction(request):

    if request.method == "POST":

        # ---------------------------
        # USER INPUT
        # ---------------------------
        try:
            N = float(request.POST['nitrogen'])
            P = float(request.POST['phosphorus'])
            K = float(request.POST['potassium'])
            temp = float(request.POST['temperature'])
            humidity = float(request.POST['humidity'])
            ph = float(request.POST['ph'])
            rainfall = float(request.POST['rainfall'])
        except:
            return render(request, 'crop_prediction.html', {
                'error': 'Invalid input values'
            })

        # ---------------------------
        # LOAD DATASET (BEST PRACTICE)
        # ---------------------------
        path = os.path.join(
            settings.BASE_DIR,
            'Crop_recommendation',
            'Crop_recommendation.csv'
        )
        data = pd.read_csv("dataset.csv")

        X = data.drop('label', axis=1)
        y = data['label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # ---------------------------
        # MODELS
        # ---------------------------
        lr = LogisticRegression(max_iter=2000)
        dt = DecisionTreeClassifier()
        rf = RandomForestClassifier()
        knn = KNeighborsClassifier()

        # Train & Accuracy (🔥 FIX: *100)
        lr.fit(X_train, y_train)
        lr_acc = round(accuracy_score(y_test, lr.predict(X_test)) * 100, 2)

        dt.fit(X_train, y_train)
        dt_acc = round(accuracy_score(y_test, dt.predict(X_test)) * 100, 2)

        rf.fit(X_train, y_train)
        rf_acc = round(accuracy_score(y_test, rf.predict(X_test)) * 100, 2)

        knn.fit(X_train, y_train)
        knn_acc = round(accuracy_score(y_test, knn.predict(X_test)) * 100, 2)

        # ---------------------------
        # PREDICTION
        # ---------------------------
        result = rf.predict([[N, P, K, temp, humidity, ph, rainfall]])

        # ---------------------------
        # BEST MODEL (optional)
        # ---------------------------
        accuracies = [lr_acc, dt_acc, rf_acc, knn_acc]
        names = ['Logistic Regression', 'Decision Tree', 'Random Forest', 'KNN']

        best_acc = max(accuracies)
        best_model = names[accuracies.index(best_acc)]

        # ---------------------------
        # CONTEXT
        # ---------------------------
        context = {
            'result': result[0],
            'lr_acc': lr_acc,
            'dt_acc': dt_acc,
            'rf_acc': rf_acc,
            'knn_acc': knn_acc,
            'best_model': best_model,
            'best_acc': best_acc
        }

        return render(request, 'crop_prediction.html', context)

    return render(request, 'crop_prediction.html')


@login_required(login_url='login')
def index(request):
    return render(request, "index.html")


def SignupPage(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        User.objects.create_user(username=uname, email=email, password=pass1)

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, "signup.html")



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {'error': 'All fields are required'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
