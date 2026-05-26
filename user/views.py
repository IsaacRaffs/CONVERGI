from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def index(request):
    return render(request, 'user/index.html', {'title': 'index'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            try:
                htmly = get_template('user/Email.html')
                d = {'username': username}
                subject = 'Bem-vindo!'
                from_email = 'noreply@convergi.com'
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, html_content, from_email, [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception:
                pass
            messages.success(request, f'Cadastro de "{username}" realizado! Aguarde a aprovação do administrador.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})
