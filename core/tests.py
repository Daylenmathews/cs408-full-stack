
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


from django.contrib.auth import get_user_model
from core.models import Favorite, Rating, Comment


class AccountAndFeatureTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(

            username="testuser",
            password="TestPassword123!"

        )

        self.team = Team.objects.create(

            name="Seattle Seahawks",
            abbreviation="SEA",
            conference="NFC",
            division="West"

        )

        self.player = Player.objects.create(

            name="Jaxon Smith-Njigba",
            team=self.team,

            position="WR"


        )

    def test_registration_page_loads(self):

        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)


    def test_user_registration(self):

        response = self.client.post(reverse("register"), {

            "username": "newuser",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!"

        })

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(

            get_user_model().objects.filter(username="newuser").exists()

        )

    def test_dashboard_requires_login(self):

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_favorites_requires_login(self):

        response = self.client.get(reverse("favorites"))
        self.assertEqual(response.status_code, 302)

    def test_add_favorite(self):

        self.client.force_login(self.user)
        self.client.post(
            reverse("toggle_favorite", args=[self.player.id])

        )
        self.assertTrue(

            Favorite.objects.filter(

                user=self.user, player=self.player

            ).exists()


        )

    def test_remove_favorite(self):

        self.client.force_login(self.user)

        Favorite.objects.create(user=self.user, player=self.player)

        self.client.post(

            reverse("toggle_favorite", args=[self.player.id])


        )

        self.assertFalse(

            Favorite.objects.filter(


                user=self.user, player=self.player

            ).exists()


        )

    def test_rate_player(self):

        self.client.force_login(self.user)

        self.client.post(

            reverse("rate_player", args=[self.player.id]),

            {"score": 5}


        )
        self.assertEqual(
            Rating.objects.get(

                user=self.user, player=self.player

            ).score,

            5
        )

    def test_invalid_rating(self):
        self.client.force_login(self.user)
        self.client.post(

            reverse("rate_player", args=[self.player.id]),

            {"score": 10}

        )
        self.assertFalse(
            Rating.objects.filter(

                user=self.user, player=self.player

            ).exists()
        )

    def test_add_comment(self):
        self.client.force_login(self.user)
        self.client.post(

            reverse("add_comment", args=[self.player.id]),
            
            {"text": "Great player!"}
        )

        self.assertTrue(

            Comment.objects.filter(

                user=self.user,
                player=self.player,

                text="Great player!"

            ).exists()

        )

    def test_empty_comment(self):

        self.client.force_login(self.user)
        self.client.post(

            reverse("add_comment", args=[self.player.id]),

            {"text": "   "}
            
        )
        self.assertEqual(Comment.objects.count(), 0)
