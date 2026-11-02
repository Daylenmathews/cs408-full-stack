
import requests



from django.core.management.base import BaseCommand, CommandError
from core.models import Player, PlayerStat



ROSTER_URL = (


    "https://site.api.espn.com/apis/site/v2/"
    "sports/football/nfl/teams/sea/roster"

)

STATS_URL = (

    "https://site.web.api.espn.com/apis/common/v3/"
    "sports/football/nfl/athletes/{player_id}/stats"
)


def get_number(value):

    try:


        return int(float(str(value).replace(",", "")))
    except (ValueError, TypeError):




        return 0


class Command(BaseCommand):

    help = "Import real Seahawks player statistics from ESPN"

    def add_arguments(self, parser):

        parser.add_argument("--season", type=int, default=2025)

    def handle(self, *args, **options):
        season = options["season"]

        self.stdout.write(f"Importing Seahawks stats for {season}...")

        try:

            response = requests.get(ROSTER_URL, timeout=20)
            response.raise_for_status()

            roster = response.json()

        except (requests.RequestException, ValueError) as error:
            raise CommandError(f"Roster download failed: {error}")

        athletes = [

            athlete


            for group in roster.get("athletes", [])
            for athlete in group.get("items", [])
        ]


        saved = 0

        skipped = 0

        for athlete in athletes:
            name = athlete.get("displayName")
            player_id = athlete.get("id")

            if not name or not player_id:
                skipped += 1
                continue

            player = Player.objects.filter(

                name=name,
                team__abbreviation__iexact="SEA"


            ).first()

            if player is None:

                skipped += 1


                continue

            try:
                response = requests.get(

                    STATS_URL.format(player_id=player_id),

                    params={"season": season, "seasontype": 2},
                    timeout=20
                )


                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, ValueError) as error:


                self.stderr.write(f"Skipped {name}: {error}")
                skipped += 1
                continue

            values = {}
            found_season = False

            for category in data.get("categories", []):

                names = category.get("names", [])

                for record in category.get("statistics", []):

                    record_season = record.get("season", {}).get("year")

                    if str(record_season) != str(season):
                        continue

                    # Only use statistics earned with Seattle.
                    if str(record.get("teamId")) != "26":
                        continue

                    found_season = True

                    for stat_name, stat_value in zip(


                        names, record.get("stats", [])

                    ):

                        number = get_number(stat_value)

                    if stat_name == "gamesPlayed":
                         values[stat_name] = max(
                            values.get(stat_name, 0),
                            number
                        )
                    else:
                        values[stat_name] = number

            if not found_season:

                skipped += 1
                continue

            # Combine passing, rushing and receiving touchdowns.
            touchdowns = (


                values.get("passingTouchdowns", 0)
                + values.get("rushingTouchdowns", 0)
                + values.get("receivingTouchdowns", 0)

            )

            PlayerStat.objects.update_or_create(

                player=player,
                season=season,


                defaults={


                    "games_played": values.get("gamesPlayed", 0),
                    "passing_yards": values.get("passingYards", 0),
                    "rushing_yards": values.get("rushingYards", 0),
                    "receiving_yards": values.get("receivingYards", 0),
                    "touchdowns": touchdowns,

                }
            )

            saved += 1

        self.stdout.write(

            self.style.SUCCESS(

                f"Saved {saved} player stat records. "
                f"Skipped {skipped} players."
            )
        )
