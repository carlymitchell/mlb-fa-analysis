import streamlit as st
import pandas as pd

# Function to load data based on player type and year
def load_data(player_type, year):
    if player_type == 'Hitter':
        if year == '2024':
            df = pd.read_csv('hitter_free_agents_2024.csv', encoding='ISO-8859-1')  # Adjust this path
        else:
            df = pd.read_csv('hitter_free_agents_career.csv', encoding='ISO-8859-1')  # Adjust this path
    else:
        if year == '2024':
            df = pd.read_csv('pitchers_free_agents_2024.csv', encoding='ISO-8859-1')  # Adjust this path
        else:
            df = pd.read_csv('pitchers_free_agents_career.csv', encoding='ISO-8859-1')  # Adjust this path
    
    # Remove the playerid column, as it's not useful
    if 'playerid' in df.columns:
        df = df.drop(columns=['playerid'])
    
    # Clean AAV by removing commas and converting to numeric
    if 'AAV' in df.columns:
        df['AAV'] = df['AAV'].replace({',': ''}, regex=True)  # Remove commas
        df['AAV'] = pd.to_numeric(df['AAV'], errors='coerce')  # Convert to numeric
    
    return df

# Function to load additional datasets
def load_additional_data(dataset_type):
    if dataset_type == 'ZiPs Hitters':
        df = pd.read_csv('25_zips_hitters.csv', encoding='ISO-8859-1')  # Adjust this path
    elif dataset_type == 'ZiPs Pitchers':
        df = pd.read_csv('25_zips_pitchers.csv', encoding='ISO-8859-1')  # Adjust this path
    elif dataset_type == 'Contracts':
        df = pd.read_csv('24_FA_contracts.csv', encoding='ISO-8859-1')  # Adjust this path
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    # Clean numeric columns (like 'AAV' or 'WAR') if needed
    if 'AAV' in df.columns:
        df['AAV'] = df['AAV'].replace({',': ''}, regex=True)  # Remove commas
        df['AAV'] = pd.to_numeric(df['AAV'], errors='coerce')  # Convert to numeric

    if 'WAR' in df.columns:
        df['WAR'] = pd.to_numeric(df['WAR'], errors='coerce')  # Ensure WAR is numeric

    return df

# Title of the app
st.title("MLB Free Agent Comparison Tool")

# Text blurb explaining the app and data source
st.markdown("""
Welcome to the MLB Free Agent Comparison Tool, a personal project by Carly Mitchell. 
This app allows you to compare upcoming MLB free agents using data from the 2024 season, their career statistics, and simple projections based on those datasets.
You can select players, view various performance metrics, and analyze key stats through interactive charts. 
Data used in this app is sourced from publicly available MLB datasets via FanGraphs. Reach out with any questions - carlymbasebalL@gmail.com
""")

# Tabs for Home (All players), Hitters, Pitchers, and 2025 Projections
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Hitters", "Pitchers", "2025 Free Agent Projections"])

# Home Tab - All Players
with tab1:
    st.header("Compare All Players")

    # Load both hitters and pitchers data for 2024 initially
    hitters_df = load_data('Hitter', '2024')
    pitchers_df = load_data('Pitcher', '2024')

    # Combine position options from both hitters and pitchers
    hitters_df['Position'] = hitters_df['Position'].str.split('/')  # Split multi-position players into lists
    all_positions_hitters = sorted(set(pos for sublist in hitters_df['Position'].dropna() for pos in sublist))
    pitcher_roles = ['SP', 'RP']  # Starter and Reliever roles
    combined_positions = all_positions_hitters + pitcher_roles

    # Unified dropdown for both hitter positions and pitcher roles
    selected_positions_combined = st.multiselect("Select Positions", options=combined_positions, key="positions_combined")

    # Filter hitters based on selected positions
    if selected_positions_combined:
        hitters_filtered = hitters_df[hitters_df['Position'].apply(lambda x: any(pos in selected_positions_combined for pos in x))]
        pitchers_filtered = pitchers_df[pitchers_df['Position'].isin(selected_positions_combined)]
    else:
        hitters_filtered = hitters_df
        pitchers_filtered = pitchers_df

    # Concatenate filtered hitters and pitchers
    all_players_df = pd.concat([hitters_filtered, pitchers_filtered], ignore_index=True)

    # Multiselect to filter by players
    selected_players_all = st.multiselect("Select Players", options=all_players_df['Name'].unique(), key="players_home")

    # Separate available stats for hitters and pitchers
    hitter_stats = hitters_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    pitcher_stats = pitchers_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Ensure 'AAV' is included in the stats if it exists
    if 'AAV' not in hitter_stats and 'AAV' in hitters_df.columns:
        hitter_stats.append('AAV')
    if 'AAV' not in pitcher_stats and 'AAV' in pitchers_df.columns:
        pitcher_stats.append('AAV')

    # Combine stats for hitters and pitchers, but label them clearly
    all_available_stats = ['Hitters: ' + stat for stat in hitter_stats] + ['Pitchers: ' + stat for stat in pitcher_stats]
    selected_stats_all = st.multiselect("Select Stats to Compare", options=all_available_stats, key="stats_home")

    # Switch between 2024 and Career with a unique key for the radio button
    year_option_all = st.radio("Select Year to View", options=["2024", "Career"], index=0, key='year_all')

    # Load both hitters and pitchers data based on the year selection
    hitters_df = load_data('Hitter', year_option_all)
    pitchers_df = load_data('Pitcher', year_option_all)

    # Concatenate hitters and pitchers into one dataframe
    hitters_df['Type'] = 'Hitter'
    pitchers_df['Type'] = 'Pitcher'
    all_players_df = pd.concat([hitters_df, pitchers_df], ignore_index=True)

    # Display filtered data in a table
    if selected_players_all and selected_stats_all:
        # Filter based on selected players and stats, separating stats for hitters and pitchers
        selected_hitters_stats = [stat.replace('Hitters: ', '') for stat in selected_stats_all if 'Hitters: ' in stat]
        selected_pitchers_stats = [stat.replace('Pitchers: ', '') for stat in selected_stats_all if 'Pitchers: ' in stat]

        # Filter the DataFrame for comparison
        comparison_all = all_players_df[all_players_df['Name'].isin(selected_players_all)]
        comparison_all = pd.concat([
            comparison_all[comparison_all['Type'] == 'Hitter'][['Name', 'Position'] + selected_hitters_stats],
            comparison_all[comparison_all['Type'] == 'Pitcher'][['Name', 'Position'] + selected_pitchers_stats]
        ])
        
        st.table(comparison_all)

        # Bar charts for each selected stat
        for stat in selected_stats_all:
            stat_name = stat.replace('Hitters: ', '').replace('Pitchers: ', '')
            st.subheader(f"{stat_name}")  # Just show the stat name
            st.bar_chart(comparison_all.set_index('Name')[stat_name])

# Hitters Tab
with tab2:
    st.header("Compare Hitters")

    # Load data for hitters
    hitters_df = load_data('Hitter', '2024')

    # Position filtering logic for hitters
    hitters_df['Position'] = hitters_df['Position'].str.split('/')  # Split multi-position players into lists
    all_positions_hitters = sorted(set(pos for sublist in hitters_df['Position'].dropna() for pos in sublist))
    selected_positions_hitters = st.multiselect("Select Positions", options=all_positions_hitters, key="hitters_positions_hitters")

    # Filter hitters based on selected positions
    if selected_positions_hitters:
        hitters_df = hitters_df[hitters_df['Position'].apply(lambda x: any(pos in selected_positions_hitters for pos in x))]

    # Multiselect to filter by players
    selected_players_hitters = st.multiselect("Select Hitters", options=hitters_df['Name'].unique(), key="players_hitters")

    # Stat selection - use all numeric columns for comparison
    available_stats_hitters = hitters_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Ensure 'AAV' is included in the stats if it exists
    if 'AAV' not in available_stats_hitters and 'AAV' in hitters_df.columns:
        available_stats_hitters.append('AAV')

    selected_stats_hitters = st.multiselect("Select Stats to Compare", options=available_stats_hitters, key="stats_hitters")

    # Display filtered data in a table
    if selected_players_hitters and selected_stats_hitters:
        comparison_hitters = hitters_df[hitters_df['Name'].isin(selected_players_hitters)][['Name', 'Position'] + selected_stats_hitters]
        st.table(comparison_hitters)

        # Bar charts for each selected stat
        for stat in selected_stats_hitters:
            st.subheader(f"{stat}")  # Just show the stat name
            st.bar_chart(comparison_hitters.set_index('Name')[stat])

# Pitchers Tab
with tab3:
    st.header("Compare Pitchers")

    # Load data for pitchers
    pitchers_df = load_data('Pitcher', '2024')

    # Position filtering logic for pitchers
    pitcher_roles = ['SP', 'RP']  # Starter and Reliever roles
    selected_positions_pitchers = st.multiselect("Select Positions", options=pitcher_roles, key="pitchers_roles_pitchers")

    # Filter pitchers based on selected roles
    if selected_positions_pitchers:
        pitchers_df = pitchers_df[pitchers_df['Position'].isin(selected_positions_pitchers)]

    # Multiselect to filter by players
    selected_players_pitchers = st.multiselect("Select Pitchers", options=pitchers_df['Name'].unique(), key="players_pitchers")

    # Stat selection - use all numeric columns for comparison
    available_stats_pitchers = pitchers_df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Ensure 'AAV' is included in the stats if it exists
    if 'AAV' not in available_stats_pitchers and 'AAV' in pitchers_df.columns:
        available_stats_pitchers.append('AAV')

    selected_stats_pitchers = st.multiselect("Select Stats to Compare", options=available_stats_pitchers, key="stats_pitchers")

    # Display filtered data in a table
    if selected_players_pitchers and selected_stats_pitchers:
        comparison_pitchers = pitchers_df[pitchers_df['Name'].isin(selected_players_pitchers)][['Name', 'Position'] + selected_stats_pitchers]
        st.table(comparison_pitchers)

        # Bar charts for each selected stat
        for stat in selected_stats_pitchers:
            st.subheader(f"{stat}")  # Just show the stat name
            st.bar_chart(comparison_pitchers.set_index('Name')[stat])

# 2025 Projections Tab (ZiPs Projections with Contract Data)
with tab4:
    st.header("2025 Free Agent Projections")

    # Load the additional datasets for ZiPs projections and contract data
    zips_hitters = load_additional_data('ZiPs Hitters')
    zips_pitchers = load_additional_data('ZiPs Pitchers')
    fa_contracts = load_additional_data('Contracts')

    # Display ZiPs Hitters projections table
    st.markdown("### 2025 ZiPs Projections - Hitters")
    st.dataframe(zips_hitters[['Name', 'PA', 'WAR', 'HR', 'RBI', 'wRC+']], use_container_width=True)

    # Display ZiPs Pitchers projections table
    st.markdown("### 2025 ZiPs Projections - Pitchers")
    st.dataframe(zips_pitchers[['Name', 'IP', 'WAR', 'ERA', 'FIP', 'K/9']], use_container_width=True)

    # Historical contract comparison
    st.subheader("Historical Contracts Comparison (Recent Free Agents)")
    st.markdown("Here are the median contract values (years and AAV) for recent free agents similar to the projected 2025 free agents.")

    # Display historical contract data
    st.dataframe(fa_contracts[['Name', 'Proj WAR', 'Med Years', 'Med Total', 'Med AAV', 'Signing Team']], use_container_width=True)

    # Add more interactivity by allowing users to select specific players to compare projections and historical contracts
    selected_players = st.multiselect("Select Players to Compare", options=fa_contracts['Name'].unique(), key="players_comparison")

    # Filter data based on selected players
    if selected_players:
        selected_fa_contracts = fa_contracts[fa_contracts['Name'].isin(selected_players)]
        selected_zips_hitters = zips_hitters[zips_hitters['Name'].isin(selected_players)]
        selected_zips_pitchers = zips_pitchers[zips_pitchers['Name'].isin(selected_players)]

        # Display comparison
        st.subheader("Selected Players: ZiPs Projections and Historical Contracts")
        
        st.markdown("#### ZiPs Projections - Hitters (Selected Players)")
        st.dataframe(selected_zips_hitters[['Name', 'PA', 'WAR', 'HR', 'RBI', 'wRC+']], use_container_width=True)

        st.markdown("#### ZiPs Projections - Pitchers (Selected Players)")
        st.dataframe(selected_zips_pitchers[['Name', 'IP', 'WAR', 'ERA', 'FIP', 'K/9']], use_container_width=True)

        st.markdown("#### Historical Contracts - Selected Players")
        st.dataframe(selected_fa_contracts[['Name', 'Proj WAR', 'Med Years', 'Med Total', 'Med AAV', 'Signing Team']], use_container_width=True)