import statsapi
import pandas as pd
from datetime import datetime

PLAYERS = {
    'Mike Trout':    545361,
    'Aaron Judge':   592450,
    'Mookie Betts':  605141,
}

def extract():
    """Extract yearByYear hitting stats from MLB Stats API.

    In production, player IDs would be pulled dynamically or from config.
    """
    records = []
    for name, player_id in PLAYERS.items():
        stats = statsapi.player_stat_data(player_id, group='hitting', type='yearByYear')
        for s in stats['stats']:
            records.append({
                'playerName': name,
                'playerID':   player_id,
                'season':     int(s['season']),
                'HR':         s['stats'].get('homeRuns'),
                'RBI':        s['stats'].get('rbi'),
                'AVG':        float(s['stats'].get('avg', 0)),
                'gamesPlayed': s['stats'].get('gamesPlayed'),
            })
    return pd.DataFrame(records)


def validate(df):
    """Validate extracted data before transformation."""
    print("Validating data...")
    if len(df) == 0:
        raise ValueError("Validation failed: DataFrame is empty")
    critical_cols = ['playerID', 'season', 'HR', 'RBI', 'AVG']
    null_counts = df[critical_cols].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Validation failed: Nulls found:\n{null_counts[null_counts > 0]}")
    dupes = df.duplicated(subset=['playerID', 'season']).sum()
    if dupes > 0:
        raise ValueError(f"Validation failed: {dupes} duplicate player/season rows found")
    print(f"Validation passed: {len(df)} rows, no nulls, no duplicates")
    return df


def transform(df):
    """Add trend metrics to batting data."""
    df = df.sort_values(['playerID', 'season']).copy()
    df['yoy_hr_change'] = (df.groupby('playerID')['HR']
                           .transform(lambda x: x - x.shift(1)))
    df['hr_rolling_avg'] = (df.groupby('playerID')['HR']
                            .transform(lambda x: x.rolling(3, min_periods=1).mean().round(1)))
    return df


def load(df, filepath='batting_trends.csv'):
    """Save transformed data to CSV."""
    df.to_csv(filepath, index=False)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved to {filepath}")


def run_pipeline(filepath='batting_trends.csv'):
    """Run the full ETL pipeline: Extract → Validate → Transform → Load."""
    print("Starting pipeline...")
    raw         = extract()
    validated   = validate(raw)
    transformed = transform(validated)
    load(transformed, filepath)
    print("Pipeline complete!")
    return transformed

if __name__ == '__main__':
    run_pipeline()
