from django.db import models

# Create your models here.

class Team(models.Model):


    name = models.CharField(max_length=100)

    abbreviation = models.CharField(max_length=10, unique=True)
    conference = models.CharField(max_length=10)
    division = models.CharField(max_length=20)

    def __str__(self):



        return self.name


class Player(models.Model):

    name = models.CharField(max_length=100)

    team = models.ForeignKey(


        Team,
        on_delete=models.CASCADE,
        related_name='players'


    )
    position = models.CharField(max_length=20)

    jersey_number = models.IntegerField(null=True, blank=True)

    def __str__(self):


        return self.name


class PlayerStat(models.Model):

    player = models.ForeignKey(
        Player,

        on_delete=models.CASCADE,
        related_name='stats'


    )



    season = models.IntegerField()
    games_played = models.IntegerField(default=0)
    passing_yards = models.IntegerField(default=0)
    rushing_yards = models.IntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    touchdowns = models.IntegerField(default=0)

    def __str__(self):


        return f"{self.player.name} - {self.season}"

    class Meta:

        constraints = [


            models.UniqueConstraint(
                fields=['player', 'season'],
                name='unique_player_season'


                
            )
        ]