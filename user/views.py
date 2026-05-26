from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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


@login_required
def gestao_usuarios(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        target = get_object_or_404(User, pk=user_id, is_staff=False)
        if action == 'aprovar':
            target.is_active = True
            target.save()
            messages.success(request, f'Usuário "{target.username}" aprovado com sucesso.')
        elif action == 'revogar':
            target.is_active = False
            target.save()
            messages.success(request, f'Acesso de "{target.username}" revogado.')
        return redirect('gestao_usuarios')

    pendentes = User.objects.filter(is_active=False, is_staff=False).order_by('date_joined')
    aprovados = User.objects.filter(is_active=True, is_staff=False).order_by('username')

    return render(request, 'user/gestao_usuarios.html', {
        'pendentes': pendentes,
        'aprovados': aprovados,
    })


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
