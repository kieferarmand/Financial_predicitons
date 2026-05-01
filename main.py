import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import re

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(creds)

sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1S_Pa05YUIkdhodB_mR7h3fLbkwCrpl-h0zTWHP-6F2U/edit?gid=1867461690#gid=1867461690").worksheet("Form Responses 1")
data = pd.DataFrame(sheet.get_all_records())


base_standings = pd.DataFrame({
    'Team': ['Los Big Dig', 'DD4t Paprika','League of Lumni', 'LPP Boiz',
             'Iron Dragons', 'Hardstuck Casterlow', 'Team Volatility Vortex',
             'Forge Esports Chaos', 'Jobless Piggies', 'Big Pharma',
             'High Alert Engineers', 'Nefarious Implications'],
    'Series Won': [6, 6, 7, 4, 3, 3, 2, 2, 2, 1, 1, 1],
    'Series Lost': [0, 0, 1, 3, 3, 3, 3, 4, 5, 4, 5, 7],
    'Games Won': [12, 12, 14, 9, 7, 7, 4, 8, 4, 4, 3, 5],
    'Games Lost': [1, 1, 5, 8, 7, 8, 7, 8, 12, 8, 10, 14]
})
base_standings = base_standings.set_index("Team")

matches = [
    ("Hardstuck Casterlow", "Team Volatility Vortex"),
    ("Hardstuck Casterlow", "Los Big Dig"),
    ("Los Big Dig", "DD4t Paprika"),
    ("DD4t Paprika", "LPP Boiz"),
    ("Team Volatility Vortex", "Jobless Piggies"),
    ("Team Volatility Vortex", "Big Pharma"),
    ("Big Pharma", "High Alert Engineers"),
    ("High Alert Engineers", "Iron Dragons"),
    ("Iron Dragons", "Forge Esports Chaos"),
    ("Forge Esports Chaos", "Big Pharma")
]

predictions = {}
for x in range(5):
  row = data.iloc[x+1]
  standings = base_standings.copy()
  index = 2
  for match in matches:
    two_zero = row.iloc[index]
    two_one = row.iloc[index + 1]
    matchup = matches[int((index/2)-1)]

    if two_zero == matchup[0]:
      winner = matchup[0]
      loser = matchup[1]
    elif two_zero == matchup[1]:
      winner = matchup[1]
      loser = matchup[0]
    elif two_one == matchup[0]:
      winner = matchup[0]
      loser = matchup[1]
    elif two_one == matchup[1]:
      winner = matchup[1]
      loser = matchup[0]

    if two_zero:
      standings.at[winner, "Series Won"] += 1
      standings.at[winner, "Games Won"] += 2
      standings.at[loser, "Series Lost"] += 1
      standings.at[loser, "Games Lost"] += 2
    if two_one:
      standings.at[winner, "Series Won"] += 1
      standings.at[winner, "Games Won"] += 2
      standings.at[winner, "Games Lost"] += 1
      standings.at[loser, "Series Lost"] += 1
      standings.at[loser, "Games Lost"] += 2
      standings.at[loser, "Games Won"] += 1
    index += 2
  standings['Series Win %'] = standings['Series Won'] / (standings['Series Won'] + standings['Series Lost'])
  standings['Game Win %'] = standings['Games Won'] / (standings['Games Won'] + standings['Games Lost'])
  standings = standings.sort_values(by=['Series Win %', 'Game Win %'], ascending=False)
  predictions[row.iloc[1]] = standings

os.makedirs("masterfile", exist_ok=True)
os.makedirs("individual", exist_ok=True)

for k, v in predictions.items():
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', k)
    filename = f"individual/{safe_name}.csv"
    v.to_csv(filename, index=True)
master_path = "masterfile/all_predictions.csv"

with open(master_path, "w") as f:
    for username, df in predictions.items():
        f.write(f"{username}\n")
        df.to_csv(f, index=True)
        f.write("\n\n")
