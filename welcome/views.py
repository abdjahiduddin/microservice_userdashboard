from django.shortcuts import render

def home(response):
    return render(response, 'welcome/home.html')

def team(response):
    return render(response, 'welcome/team.html')
