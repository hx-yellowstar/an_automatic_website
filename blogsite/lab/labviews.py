from django.shortcuts import render

# Create your views here.

def worldmap(request):
    return render(request, 'lab.html')
