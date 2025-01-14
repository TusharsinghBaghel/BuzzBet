from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
class UserProfileForm(UserCreationForm):
    email = forms.EmailField()
    address = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('username', 'email', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        # Pass initial data for the address field from Profile
        if 'instance' in kwargs:
            user = kwargs['instance']
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['address'] = user.profile.address if hasattr(user, 'profile') else ''
        super().__init__(*args, **kwargs)



    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save the Profile model
            print("Address:", self.cleaned_data.get('address'))
            profile, created = Profile.objects.get_or_create(user=user)
            profile.address = self.cleaned_data.get('address', '')
            profile.save()

        return user
        
