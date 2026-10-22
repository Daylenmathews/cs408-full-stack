


import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Team, Player


class Command(BaseCommand):

    help = "Download NFL rosters from ESPN and update the database"

    def add_arguments(self, parser):

        parser.add_argument(

            "--team",
            default="sea",
            help="NFL team abbreviation, e.g. sea, kc, buf"


        )

    def handle(self, *args, **options):

        team_code = options["team"].lower()

        url = (
            "https://site.api.espn.com/apis/site/v2/"
            f"sports/football/nfl/teams/{team_code}/roster"
        )



        self.stdout.write(f"Downloading {team_code.upper()} roster...")

        try:

            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()


        except (requests.RequestException, ValueError) as error:
              raise CommandError(f"ESPN API request failed: {error}")

        team_data = data.get("team", {})
        groups = data.get("athletes", [])

        if not team_data or not groups:

            raise CommandError("No valid team or roster data returned.")

        team_name = (

            team_data.get("displayName")
            or team_data.get("name")
            or team_code.upper()

        )

        team_abbr = team_data.get("abbreviation", team_code.upper())

        with transaction.atomic():

            team, _ = Team.objects.update_or_create(

                abbreviation=team_abbr,

                defaults={

                    "name": team_name,
                    "conference": "Unknown",
                    "division": "Unknown",
                },



            )



            count = 0

            for group in groups:

                for athlete in group.get("items", []):
                    name = athlete.get("displayName")

                    if not name:
                        continue

                    position = athlete.get("position") or {}

                    jersey = athlete.get("jersey")

                    try:
                        jersey = int(jersey) if jersey else None
                    except (ValueError, TypeError):
                        jersey = None

                    Player.objects.update_or_create(

                        name=name,
                        team=team,

                        defaults={

                            "position": position.get("abbreviation", "N/A"),
                            "jersey_number": jersey,


                        },


                    )

                    count += 1

        self.stdout.write(

            self.style.SUCCESS(

                f"Updated {count} players for {team.name}."


            )


            
        )
