from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from transport.models import LietotajaZinojums, Atsauksme, FavoriteRoute

def login_view(request):
    """
    Lietotāja pieteikšanās skats
    """
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'transport:home')
                return redirect(next_url)
            else:
                messages.error(request, _('Invalid username or password.'))
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})

def register_view(request):
    """
    Lietotāja reģistrācijas skats
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Your account has been created successfully.'))
            return redirect('transport:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    """
    Lietotāja atteikšanās skats
    """
    logout(request)
    messages.success(request, _('You have been logged out.'))
    return redirect('transport:home')

@login_required
def user_profile(request):
    """
    Lietotāja profila skats
    """
    reports = LietotajaZinojums.objects.filter(lietotajs=request.user).order_by('-laiks')
    review_count = Atsauksme.objects.filter(lietotajs=request.user).count()
    user_reviews = Atsauksme.objects.filter(lietotajs=request.user).order_by('-laiks')
    saved_routes = FavoriteRoute.objects.filter(user=request.user).select_related('route')
    context = {
        'user': request.user,
        'reports': reports,
        'review_count': review_count,
        'user_reviews': user_reviews,
        'saved_routes': saved_routes,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """
    Lietotāja profila rediģēšanas skats
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})