
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from core.models import Player


def home(request):


    return render(request, 'core/home.html')


@login_required


def dashboard(request):
    return render(request, 'core/dashboard.html')


def register(request):


    if request.method == 'POST':


        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()
            login(request, user)

            return redirect('dashboard')

        
    else:


        form = UserCreationForm()

        

    return render(request, 'core/register.html', {'form': form})

def players(request):

    query = request.GET.get('q', '').strip()

    player_list = Player.objects.select_related('team').all()

    if query:
        player_list = player_list.filter(name__icontains=query)

    player_list = player_list.order_by('name')

    return render(request, 'core/players.html', {

        'players': player_list,
        'query': query,

    })


def player_detail(request, player_id):
    player = get_object_or_404(


        Player.objects.select_related('team'),
        id=player_id
    )

    stats = player.stats.all().order_by('-season')

    return render(request, 'core/player_detail.html', {

        'player': player,

        'stats': stats,

        
    })
