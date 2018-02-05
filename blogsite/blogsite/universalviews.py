from django.shortcuts import render

def pagenotfound(request):
    return render(request, '404.html')

def servererror(request):
    return render(request, '500.html')