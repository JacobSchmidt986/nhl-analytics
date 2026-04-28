import streamlit as st
import pandas as pd
import plotly.express as px
from nhl_api import get_standings, get_standings_by_season, get_scores_by_date, get_boxscore, get_game_details


st.set_page_config(page_title="NHL Analytics Dashboard", layout = "wide")
st.sidebar.title("NHL Dashboard")
page = st.sidebar.radio("Navigate",
    [
     "Team Profile",
     "League Overview",
     "Team Comparison",
     "Momentum Scores",
     "Live Games"])
df = get_standings()
st.title("NHL Analytics Dashboard")
if page == "Team Profile":
    st.subheader("Team Standings and Performance Overview")

    # Specific Team Metrics: Allow users to select a team and view key metrics


    
    #st.write(df)
    #st.write("Number of teams:", len(df))

    team = st.selectbox("Choose a team", df["Team"].sort_values())

    team_row = df[df["Team"] == team].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Points", int(team_row["Points"]))
    col2.metric("Wins", int(team_row["Wins"]))
    col3.metric("Goal Differential", int(team_row["Goal Differential"]))
    col4.metric("Win Percentage", round(team_row["Win Percentage"], 3))

    #Compare how Teams are performing relative to their historical average
    st.header("Historical Performance Comparison")
    season_dates = {
        "2024-25": "2025-04-17",
        "2023-24": "2024-04-18",
        "2022-23": "2023-04-14",
        "2021-22": "2022-04-29",
    }
    season_label = st.selectbox("Choose a season to compare against", list(season_dates.keys()))

    current_df = get_standings()
    past_df = get_standings_by_season(season_dates[season_label])

    current_team = current_df[current_df["Team"] == team].iloc[0]
    past_team = past_df[past_df["Team"] == team].iloc[0]

    history_comparison = pd.DataFrame({
        "Stat": ["Points", "Wins", "Losses", "OT Losses", "Goals For", "Goals Against", "Goal Differential", "Win Percentage"],
        f"{season_label}": [past_team["Points"], past_team["Wins"], past_team["Losses"], past_team["OT Losses"], past_team["Goals For"], past_team["Goals Against"], past_team["Goal Differential"], round(past_team["Win Percentage"], 3)],
        "Current Season": [current_team["Points"], current_team["Wins"], current_team["Losses"], current_team["OT Losses"], current_team["Goals For"], current_team["Goals Against"], current_team["Goal Differential"], round(current_team["Win Percentage"], 3)]
    })
    st.dataframe(history_comparison, hide_index=True)



# Show League Goal Differential in a bar chart
if page == "League Overview":
    st.divider()
    st.header("League Goal Differential")

    fig = px.bar(
        df.sort_values("Goal Differential" , ascending=False),
        x="Team",
        y="Goal Differential",
        title="Goal Differential by Team",

    )
    df_sorted = df.sort_values("Points", ascending=False).reset_index(drop=True)
    df_sorted["Rank"] = df_sorted.index + 1
    df_sorted = df_sorted.set_index("Rank")

    st.plotly_chart(fig, use_container_width=True)


#Full Standings Table: Display a sortable table of all teams and their key stats


    st.header("Full Standings Table")
    st.dataframe(df_sorted)

#Allow users to select two teams and compare their stats side by side, along with a visual comparison of key metrics.
if page == "Team Comparison":

    st.divider()
    st.header("Team Comparison")

    team_options = sorted(df["Team"].tolist())

    team1 = st.selectbox("Choose Team 1", team_options, index = 0)
    team2 = st.selectbox("Choose Team 2", team_options, index = 1)

    team1_data = df[df["Team"] == team1].iloc[0]
    team2_data = df[df["Team"] == team2].iloc[0]

    comparison_df = pd.DataFrame({
        "Stat":["Points", "Wins", "Losses", "OT Losses","Goals For", "Goals Against" ,"Goal Differential", "Win Percentage"],
        team1: [team1_data["Points"], team1_data["Wins"], team1_data["Losses"], team1_data["OT Losses"], team1_data["Goals For"], team1_data["Goals Against"], team1_data["Goal Differential"], round(team1_data["Win Percentage"], 3)],
        team2: [team2_data["Points"], team2_data["Wins"], team2_data["Losses"], team2_data["OT Losses"], team2_data["Goals For"], team2_data["Goals Against"], team2_data["Goal Differential"], round(team2_data["Win Percentage"], 3)]
    })

    st.dataframe(comparison_df, hide_index=True)
    comparison_chart_df = comparison_df[
        comparison_df["Stat"].isin(["Points", "Wins","Goals For", "Goals Against","Goal Differential"])
        ]

    comparison_chart_df = comparison_chart_df.melt(
        id_vars="Stat",
        var_name="Team",
        value_name="Value"
    )
    fig = px.bar(
        comparison_chart_df,
        x="Stat",
        y="Value",
        color="Team",
        barmode="group",
        title=f"{team1} vs {team2}",
    )
    st.plotly_chart(fig, use_container_width=True)


#Calculate a "Momentum Score" for each team based on recent performance

if page == "Momentum Scores":
    st.divider()
    st.header("Momentum Scores")
    df["Momentum Score"] = (
        0.45 * df["Win Percentage"] +
        0.35 * (df["Goal Differential"] / df["Goal Differential"].abs().max()) +
        0.20 * (df["Goals For"] / df["Goals For"].max())
    )

    momentum_fig = px.bar(
        df.sort_values("Momentum Score", ascending=False),
        x="Team",
        y="Momentum Score",
        title="Momentum Score by Team",
    )
    st.plotly_chart(momentum_fig, use_container_width=True)
    with st.expander("How is Momentum Score calculated?"):
        st.write("""
        Momentum Score combines win percentage, goal differential, and offensive production.
        It is not a betting model, but a simple performance index for comparing teams.
        """)
if page == "Live Games":
    st.title("Live Game Tracker")

    if st.button("Refresh Games"):
        st.cache_data.clear()
        st.rerun()

    selected_date = st.date_input("Choose a date")

    games_df = get_scores_by_date(selected_date.isoformat())

    if games_df.empty:
        st.info("No NHL games found for this date.")
    else:
        for _, game in games_df.iterrows():
            st.subheader(f"{game['Away Team']} vs {game['Home Team']}")

            col1, col2, col3 = st.columns(3)

            col1.metric(game["Away Team"], int(game["Away Score"]))
            col2.metric("Status", game["Status"])
            col3.metric(game["Home Team"], int(game["Home Score"]))

            st.caption(f"Venue: {game['Venue']}")

            with st.expander("View detailed game stats"):
                try:
                    boxscore = get_boxscore(game["Game ID"])
                    details = get_game_details(game["Game ID"])

                    away_team = boxscore["awayTeam"]
                    home_team = boxscore["homeTeam"]

                    stats_df = pd.DataFrame({
                        "Stat": [
                            "Score",
                            "Shots",
                            "Power Play Goals",
                            "Power Play Opportunities",
                            "Faceoff Win %",
                            "Penalty Minutes"
                        ],
                        away_team["abbrev"]: [
                            away_team.get("score", 0),
                            away_team.get("sog", 0),
                            away_team.get("powerPlayGoals", "N/A"),
                            away_team.get("powerPlayOpportunities", "N/A"),
                            away_team.get("faceoffWinningPctg", "N/A"),
                            away_team.get("pim", "N/A")
                        ],
                        home_team["abbrev"]: [
                            home_team.get("score", 0),
                            home_team.get("sog", 0),
                            home_team.get("powerPlayGoals", "N/A"),
                            home_team.get("powerPlayOpportunities", "N/A"),
                            home_team.get("faceoffWinningPctg", "N/A"),
                            home_team.get("pim", "N/A")
                        ]
                    })

                    st.dataframe(stats_df, hide_index=True)

                    st.subheader("Game Info")

                    period = details.get("periodDescriptor", {}).get("number", "N/A")
                    time_remaining = details.get("clock", {}).get("timeRemaining", "N/A")

                    col_a, col_b = st.columns(2)
                    col_a.metric("Period", period)
                    col_b.metric("Time Remaining", time_remaining)

                except Exception as e:
                    st.warning("Detailed stats are not available for this game yet.")
                    st.caption(str(e))

            st.divider()