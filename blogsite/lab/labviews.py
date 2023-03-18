from django.shortcuts import render

# Create your views here.
# 此项功能仍在开发中，目前只能看到一个世界地图（在lab/页面，没有链接可以直接到达，地图来自highcharts）

def worldmap(request):
    return render(request, 'lab.html')
