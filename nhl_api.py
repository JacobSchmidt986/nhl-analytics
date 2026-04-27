import requests
import pandas as pd

BASE_URL = "https://api-web.nhle.com/v1"

def get_standings():
    url = f"{BASE_URL}/standings/now"
    response = requests.get(url)
    response.raise_for_status()

    json_data = response.json()

    print(json_data.keys())  # Debugging line to check the structure of the JSON response
    print(type(json_data["standings"]))  # Debugging line to check the type of the 'standings' key
    print("Number of items from API:", len(json_data["standings"]))  # Debugging line to check the number of items in 'standings'
    data = json_data["standings"]

    rows = []
    for team in data:
        rows.append({
            "Team": team["teamName"]["default"],
            "Abbrev": team["teamAbbrev"]["default"],
            "Games Played": team["gamesPlayed"],
            "Wins": team["wins"],
            "Losses": team["losses"],
            "OT Losses": team["otLosses"],
            "Points": team["points"],
            "Goals For": team["goalFor"],
            "Goals Against": team["goalAgainst"],
            "Goal Differential": team["goalDifferential"],
            "Win Percentage": team["wins"] / team["gamesPlayed"] if team["gamesPlayed"] else 0
        })
        
    print("Rows Created:", len(rows))  # Debugging line to check the number of rows created
    df = pd.DataFrame(rows)
    return df

def get_standings_by_season(date):
    url = f"{BASE_URL}/standings/{date}"
    response = requests.get(url)
    response.raise_for_status()

    json_data = response.json()
    data = json_data["standings"]

    rows = []
    for team in data:
        rows.append({
            "Team": team["teamName"]["default"],
            "Abbrev": team["teamAbbrev"]["default"],
            "Games Played": team["gamesPlayed"],
            "Wins": team["wins"],
            "Losses": team["losses"],
            "OT Losses": team["otLosses"],
            "Points": team["points"],
            "Goals For": team["goalFor"],
            "Goals Against": team["goalAgainst"],
            "Goal Differential": team["goalDifferential"],
            "Win Percentage": team["wins"] / team["gamesPlayed"] if team["gamesPlayed"] else 0
        })
        
    df = pd.DataFrame(rows)
    return df