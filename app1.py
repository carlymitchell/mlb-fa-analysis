import streamlit as st
import pandas as pd

# Loading hitter/pitcher data
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
    
    # Removing playerid column
    if 'playerid' in df.columns:
        df = df.drop(columns=['playerid'])
    
    # AAV -- removing commas & converting to numeric
    if 'AAV' in df.columns:
        df['AAV'] = df['AAV'].replace({',': ''}, regex=True)  # Remove commas
        df['AAV'] = pd.to_numeric(df['AAV'], errors='coerce')  # Convert to numeric
    
    return df

# Loading 2025 ZIPS Projections
def load_additional_data(dataset_type):
    if dataset_type == 'ZiPs Hitters':
        df = pd.read_csv('25_zips_hitters.csv', encoding='ISO-8859-1')  # Adjust this path
    elif dataset_type == 'ZiPs Pitchers':
        df = pd.read_csv('25_zips_pitchers.csv', encoding='ISO-8859-1')  # Adjust this path
    elif dataset_type == 'Contracts':
        df = pd.read_csv('24_FA_contracts.csv', encoding='ISO-8859-1')  # Adjust this path
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    # Clean numeric columns as needed
    if 'AAV' in df.columns:
        df['AAV'] = df['AAV'].replace({',': ''}, regex=True)  # Remove commas
        df['AAV'] = pd.to_numeric(df['AAV'], errors='coerce')  # Convert to numeric

    if 'WAR' in df.columns:
        df['WAR'] = pd.to_numeric(df['WAR'], errors='coerce')  # Ensure WAR is numeric

    return df

# App Title
st.title("MLB Free Agent Comparison Tool")

# Introduction Blurb
st.markdown("""
Welcome to the MLB Free Agent Comparison Tool, a personal project by Carly Mitchell. 
This app allows you to compare upcoming MLB free agents using data from the 2024 season, their career statistics, and simple projections based on those datasets.
You can select players, view various performance metrics, and analyze key stats through interactive charts. 
Data used in this app is sourced from publicly available MLB datasets via FanGraphs. Reach out with any questions - carlymbasebalL@gmail.com
""")

# Tabs for Home
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Hitters", "Pitchers", "2025 Free Agent Projections"])

# Home Tab - All Players
with tab1:
    st.header("Compare All Players")

    # Loads both hitters and pitchers data for 2024 initially
    hitters_df = load_data('Hitter', '2024')
    pitchers_df = load_data('Pitcher', '2024')

    # Combines position options from both hitters and pitchers
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

    # Combine stats for hitters and pitchers with clear labels
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

    # Select whether to view hitter or pitcher projections
    player_type = st.selectbox("Select Player Type", options=["Hitter", "Pitcher"], key="player_type_projections")

    # Based on selection, load the appropriate data
    if player_type == "Hitter":
        zips_data = zips_hitters
        position_filter = ["1B", "2B", "3B", "SS", "LF", "CF", "RF", "C", "DH"]  # Common hitter positions
        projection_columns = ['Name', 'PA', 'WAR', 'HR', 'RBI', 'wRC+']  # Add more relevant stats if needed
    else:
        zips_data = zips_pitchers
        position_filter = ["SP", "RP"]  # Common pitcher roles
        projection_columns = ['Name', 'IP', 'WAR', 'ERA', 'FIP', 'K/9']  # Add more relevant stats if needed

    # Select player from the ZiPs data
    selected_player = st.selectbox("Select Player to Project", options=zips_data['Name'].unique())

    # Get selected player's ZiPs projections for 2025
    player_projection = zips_data[zips_data['Name'] == selected_player]

    # Display player ZiPs projections in a dataframe
    st.subheader(f"2025 ZiPs Projections for {selected_player}")
    st.dataframe(player_projection[projection_columns], use_container_width=True)

    # Automatically retrieve projected WAR and Age from ZiPs
    projected_war = player_projection['WAR'].values[0]
    player_age = player_projection['Age'].values[0]  # Assuming 'Age' is a column in the zips data

    # Heuristic for projecting contract length and AAV (can replace with regression model)
    if projected_war >= 5:
        projected_contract_years = 6  # Higher WAR, longer contract
    elif projected_war >= 3:
        projected_contract_years = 4  # Moderate WAR, medium-length contract
    else:
        projected_contract_years = 2  # Lower WAR, shorter contract

    # Calculate AAV with a minimum value of $740,000
    projected_aav = max(projected_war * 2.5, 0.74)  # Ensure AAV does not drop below $740,000
    total_contract_value = projected_aav * projected_contract_years

    # Display the projected contract details
    st.subheader(f"Contract Projection for {selected_player}")
    st.markdown(f"**Projected WAR:** {projected_war}")
    st.markdown(f"**Contract Length:** {projected_contract_years} years")
    st.markdown(f"**AAV:** ${projected_aav:.2f} million")
    st.markdown(f"**Total Value:** ${total_contract_value:.2f} million")

    # Comparison with Historical Contracts
    st.subheader("Compare with Similar 2024 Free Agents")

    # Filter fa_contracts based on position, projected WAR, and age
    similar_players = fa_contracts[
        (fa_contracts['Position'].isin(position_filter)) & 
        (fa_contracts['Proj WAR'].between(projected_war - 0.5, projected_war + 0.5)) &
        (fa_contracts['Age'].between(player_age - 2, player_age + 2))  # Assuming 'Age' is a column in the fa_contracts data
    ]

    # Display the comparison
    st.dataframe(similar_players[['Name', 'Proj WAR', 'Med Years', 'AAV', 'Signing Team', 'Age']])

    # Ensure player projection AAV is included in the bar graph data
    projected_data = pd.DataFrame({'Name': [selected_player], 'AAV': [projected_aav]})
    historical_data = similar_players[['Name', 'AAV']].rename(columns={'AAV': 'AAV'})

    # Combine the historical and projected data for comparison
    comparison_data = pd.concat([historical_data, projected_data])

    # Visualization: Projected AAV vs. Historical Contracts
    st.subheader(f"Projected AAV for {selected_player} vs. Similar Free Agents")
    st.bar_chart(comparison_data.set_index('Name'))