from django.shortcuts import render
from .forms import SignUpForm, SignInForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth import logout
# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_ambientes')
        else:
            return render(request, 'usuario/signup.html', {'form': form})
    form = SignUpForm()
    return render(request, 'usuario/signup.html', {'form': form})

def signin_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('lista_ambientes')
            else:
                form.add_error(None, 'Nome de usuário ou senha inválidos.')
                return render(request, 'usuario/signin.html', {'form': form})
    form = SignInForm()
    return render(request, 'usuario/signin.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    return render(request, 'home.html')