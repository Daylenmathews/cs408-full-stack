
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from core.models import Player, Team, PlayerStat


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
    team = request.GET.get('team', '').strip()
    position = request.GET.get('position', '').strip()
    season = request.GET.get('season', '').strip()
    stat_type = request.GET.get('stat_type', '').strip()
    min_stat = request.GET.get('min_stat', '').strip()

    player_list = Player.objects.select_related('team').all()

    if query:

        player_list = player_list.filter(name__icontains=query)

    if team:


        player_list = player_list.filter(team__abbreviation=team)

    if position:

        player_list = player_list.filter(position=position)

    # Only allow supported statistical fields.
    stat_fields = {

        'passing_yards': 'passing_yards',
        'rushing_yards': 'rushing_yards',
        'receiving_yards': 'receiving_yards',
        'touchdowns': 'touchdowns',
        'games_played': 'games_played',


    }

    stat_filters = {}

    if season:

        try:
            stat_filters['stats__season'] = int(season)

        except ValueError:
            player_list = player_list.none()

    if stat_type in stat_fields and min_stat:

        try:
            stat_filters[f'stats__{stat_fields[stat_type]}__gte'] = int(min_stat)
        except ValueError:
            player_list = player_list.none()

    if stat_filters:


        player_list = player_list.filter(**stat_filters)



    player_list = player_list.distinct().order_by('name', 'id')

    teams = Team.objects.order_by('name')

    positions = (

        Player.objects.order_by('position')
        .values_list('position', flat=True)
        .distinct()

        
    )
    seasons = (
        PlayerStat.objects.order_by('-season')
        .values_list('season', flat=True)
        .distinct()
    )

    return render(request, 'core/players.html', {
        'players': player_list,
        'query': query,
        'selected_team': team,
        'selected_position': position,
        'selected_season': season,
        'selected_stat_type': stat_type,
        'min_stat': min_stat,
        'teams': teams,
        'positions': positions,
        'seasons': seasons,
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
