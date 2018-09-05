from django.shortcuts import render

def flightSearch(request):
    return render(request, 'flightSearch/flightSearch.html', {"active_tab": "flightSearch"})

def gatheredData(request):
    return render(request, 'flightSearch/gatheredData.html', {"active_tab": "gatheredData"})    