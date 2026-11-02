
from django.test import TestCase
from django.urls import reverse

from core.models import Team, Player, PlayerStat


class PlayerSearchTests(TestCase):

    def setUp(self):

        self.seahawks = Team.objects.create(

            name="Seattle Seahawks",
            abbreviation="SEA",
            conference="NFC",
            division="West"


        )

        self.chiefs = Team.objects.create(

            name="Kansas City Chiefs",
            abbreviation="KC",
            conference="AFC",
            division="West"

        )

        self.player1 = Player.objects.create(

            name="Jaxon Smith-Njigba",
            team=self.seahawks,

            position="WR"


        )

        self.player2 = Player.objects.create(

            name="Patrick Mahomes",
            team=self.chiefs,
            position="QB"


        )

        PlayerStat.objects.create(

            player=self.player1,
            season=2025,
            games_played=17,
            receiving_yards=1200,
            touchdowns=8
        )

        PlayerStat.objects.create(


            player=self.player2,
            season=2025,
            games_played=17,
            passing_yards=4000,
            touchdowns=30


        )

    def test_players_page_loads(self):

        response = self.client.get(reverse("players"))
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        response = self.client.get(

            reverse("players"), {"q": "Jaxon"}

        )
        self.assertContains(response, "Jaxon Smith-Njigba")
        self.assertNotContains(response, "Patrick Mahomes")

    def test_filter_by_team(self):

        response = self.client.get(

            reverse("players"), {"team": "SEA"}

        )


        self.assertContains(response, "Jaxon Smith-Njigba")
        self.assertNotContains(response, "Patrick Mahomes")

    def test_filter_by_position(self):

        response = self.client.get(

            reverse("players"), {"position": "QB"}


        )
        self.assertContains(response, "Patrick Mahomes")
        self.assertNotContains(response, "Jaxon Smith-Njigba")

    def test_filter_by_season(self):
        response = self.client.get(

            reverse("players"), {"season": "2025"}


        )
        self.assertEqual(len(response.context["players"]), 2)

    def test_filter_by_statistic(self):

        response = self.client.get(

            reverse("players"),
            {"stat_type": "passing_yards", "min_stat": "3000"}



        )
        self.assertContains(response, "Patrick Mahomes")
        self.assertNotContains(response, "Jaxon Smith-Njigba")

    def test_combined_filters(self):
        response = self.client.get(

            reverse("players"),
            {

                "team": "SEA",
                "position": "WR",
                "season": "2025",
                "stat_type": "receiving_yards",
                "min_stat": "1000"

            }
        )
        self.assertEqual(

            list(response.context["players"]),
            [self.player1]

        )

    def test_invalid_season(self):

        response = self.client.get(

            reverse("players"), {"season": "invalid"}
        )
        self.assertEqual(len(response.context["players"]), 0)

    def test_invalid_stat_value(self):
        response = self.client.get(

            reverse("players"),

            {"stat_type": "touchdowns", "min_stat": "abc"}

            
        )
        self.assertEqual(len(response.context["players"]), 0)

