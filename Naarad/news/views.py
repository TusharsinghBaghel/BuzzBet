from django.shortcuts import render, redirect
from .models import newsPost, Location, Comment
from django.shortcuts import get_object_or_404
from .forms import NewsPostForm, LocationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
def news_list(request):
    filter_by = request.GET.get('filter', 'latest')
    news_list = newsPost.objects.all()
    
    if filter_by == 'latest':
        news_list = newsPost.objects.order_by('-created_at', 'validity')
    elif filter_by == 'oldest':
        news_list = newsPost.objects.order_by('created_at', 'validity')
    elif filter_by == 'impact':
        news_list = newsPost.objects.order_by('impact', 'validity')
    
    
    context = {
        'news_list':news_list,
        'filter': filter_by,
    }
    return render(request, 'news_list.html', context)

def news_detail(request, pk):
    news = get_object_or_404(newsPost, pk=pk)
    return render(request, 'news_detail.html', {'news': news})

def news_search(request):
    query = request.GET.get('q', '')
    news_list = newsPost.objects.filter(headline__icontains = query)
    return render(request, 'news_list.html', {'news_list': news_list, 'query': query})

@login_required
def news_create(request):
    user_profile = request.user.profile
    locations = Location.objects.all()
    half_points = user_profile.points //2
    form = NewsPostForm()
    if request.method == "POST":
        if 'create_location' in request.POST:  # Check if the form submitted is for creating a location
            location_form = LocationForm(request.POST)
            if location_form.is_valid():
                location_form.save()
                return redirect('create_news')  # Redirect to the same page to select the newly created location
        else:
            form = NewsPostForm(request.POST, request.FILES)
            if form.is_valid():
                news_post = form.save(commit=False)
                news_post.author = request.user
                bet_amount = form.cleaned_data['bet']
                user_profile.points -= bet_amount
                user_profile.save()
                news_post.save()
                return redirect('news_list')
    
    else:
        form = NewsPostForm()
        location_form = LocationForm()
    return render(request, 'news_create.html', {
        'form': form, 
        'location_form': location_form, 
        'locations': locations, 
        'half_points': half_points
        })

        
            
@login_required
def validate_and_impact_news(request, news_id):
    news = get_object_or_404(newsPost, id=news_id)

    if request.method == "POST":
        # Check if the user has already validated or unvalidated
        if request.user in news.reacted_by.all():
            messages.warning(request, "You have already reacted")
        
        else:
            if 'validate' in request.POST:
                # Add user to validated_by and increase validity points
                prev_validity = news.validity
                news.validity = news.validity*news.reacted_by.count() + request.user.profile.validity
                news.reacted_by.add(request.user)
                news.validity /= news.reacted_by.count()
                
                messages.success(request, "Thank you for validating this news.")

                # Get impact value from the form
                try:
                    impact_value = int(request.POST.get("impact"))
                    if 0 <= impact_value <= 100:  # Validate input range
                        prev_impact = news.impact
                        news.impact = prev_impact*(news.reacted_by.count()-1) + impact_value*request.user.profile.validity//100
                        news.impact /= news.reacted_by.count()
                        prev_profit = news.bet*prev_impact*prev_validity//10000
                        new_profit = news.bet*news.impact*news.validity//10000
                        news.author.profile.points += new_profit - prev_profit

                        author_news_count = newsPost.objects.filter(author=news.author).count()
                        total_validity = sum(n.validity for n in newsPost.objects.filter(author=news.author))
                        news.author.profile.validity = total_validity / author_news_count
                        messages.success(request, "Thank you for providing an impact score!")
                    else:
                        messages.warning(request, "Impact value must be between 0 and 100.")
                except (ValueError, TypeError):
                    messages.error(request, "Invalid impact value.")
            elif 'unvalidate' in request.POST:
                # Add user to unvalidated_by and decrease validity points
                prev_validity = news.validity
                news.validity = news.validity*news.reacted_by.count() - request.user.profile.validity
                news.reacted_by.add(request.user)
                news.validity /= news.reacted_by.count()
                messages.info(request, "You have unvalidated this news.")
                # Get impact value from the form
                try:
                    impact_value = int(request.POST.get("impact"))
                    if 0 <= impact_value <= 100:  # Validate input range
                        prev_impact = news.impact
                        news.impact = prev_impact*(news.reacted_by.count()-1) + impact_value*request.user.profile.validity//100
                        news.impact /= news.reacted_by.count()
                        prev_profit = news.bet*prev_impact*prev_validity//10000
                        new_profit = news.bet*news.impact*news.validity//10000
                        news.author.profile.points += new_profit - prev_profit
                        author_news_count = newsPost.objects.filter(author=news.author).count()
                        total_validity = sum(n.validity for n in newsPost.objects.filter(author=news.author))
                        news.author.profile.validity = total_validity / author_news_count
                        messages.success(request, "Thank you for providing an impact score!")
                    else:
                        messages.warning(request, "Impact value must be between 0 and 100.")
                except (ValueError, TypeError):
                    messages.error(request, "Invalid impact value.")
        news.author.profile.save()
        news.save()
    return redirect('news_detail', pk=news_id)


@login_required
def add_comment(request, news_id):
    if request.method == 'POST':
        news = get_object_or_404(newsPost, id=news_id)
        comment_content = request.POST.get('comment', '').strip()
        if comment_content:
            Comment.objects.create(news_post=news, author=request.user, content=comment_content)
    return redirect('news_detail', pk=news_id)

@login_required
def delete_news(request, news_id):
    news = get_object_or_404(newsPost, id=news_id)
    news.delete()
    return redirect('news_list')