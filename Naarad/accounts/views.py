from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
# Create your views here.

from django.db import IntegrityError

def register(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  # Save user to the database
            except IntegrityError:  # Handle error if user already exists
                form.add_error('username', 'Username already exists!')
                return render(request, 'registration/register.html', {'form': form})
                        
            login(request, user)  # Log the user in after registration
            return redirect('index')  # Redirect to the home page or dashboard
    else:
        form = UserProfileForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request, pk = None):

    if pk:
        user = get_object_or_404(User, pk=pk)
    else:
        user = request.user

    return render(request, 'registration/profile.html', {'user': user})

def leaderboard(request):
    leaderboard_data = Profile.objects.order_by('-points')
    return render(request, 'registration/leaderboard.html', {'leaderboard_data': leaderboard_data})