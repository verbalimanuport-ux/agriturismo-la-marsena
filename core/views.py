from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def azienda_agricola(request):
    return render(request, "azienda_agricola.html")


def md_ranch(request):
    return render(request, "md_ranch.html")
