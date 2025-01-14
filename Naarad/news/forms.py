from django import forms 
from .models import newsPost, Location

class NewsPostForm(forms.ModelForm):
    class Meta:
        model = newsPost
        fields = ['headline', 'content', 'bet', 'photo', 'location']

        def clean_bet(self):
            bet = self.cleaned_data['bet']
            user_profile = self.instance.author.profile
            if bet > user_profile.points//2:
                raise forms.ValidationError("Bet cannot be more than half of current points wallet")
            return bet
        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location 
        fields = ['latitude', 'longitude', 'address']