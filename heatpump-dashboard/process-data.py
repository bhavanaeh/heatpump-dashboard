"""
Bhavana Sundar (bsundar3)
CS 498 - End to End Data Science
University of Illinois Urbana-Champaign

"""
import pandas as pd

def process_data(input_file):

    df = pd.read_excel(input_file)
    df_filtered = df[df['population'] >= 10000]
    df_filtered['city_state'] = df_filtered['city'] + ", " + df_filtered['state_name']
    df_final = df_filtered[['city_state', 'lat', 'lng']].drop_duplicates()
    df_final.to_csv('data/cities.csv', index=False)

if __name__ == "__main__":
    input_file = 'data-raw/uscities.xlsx'
    process_data(input_file)
