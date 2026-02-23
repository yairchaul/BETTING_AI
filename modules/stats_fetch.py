# modules/stats_fetch.py
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

def get_player_avg(player_name, stat='PTS'):
    try:
        player = players.find_players_by_full_name(player_name)
        if not player:
            return 0.0
        player_id = player[0]['id']
        career = playercareerstats.PlayerCareerStats(player_id)
        df = career.get_data_frames()[0]
        if stat in df.columns:
            return df[stat].mean()
        return 0.0
    except:
        return 0.0