"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    referendum_acess = "data/referendum.csv"
    referendum = pd.read_csv(referendum_acess, delimiter=';')

    regions_acess = "data/regions.csv"
    regions = pd.read_csv(regions_acess)

    departments_acess = "data/departments.csv"
    departments = pd.read_csv(departments_acess)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions, departments, left_on='code', right_on='region_code', how='inner' ,suffixes=('_reg', '_dep')) # how='inner'
    return merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merged_df = pd.merge(referendum, regions_and_departments, left_on='Department code', right_on='code_dep', how='inner')
    return merged_df

    # Filtre les lignes relatives aux DOM-TOM-COM et aux Français vivant à l'étranger
    #filtered_df = merged_df[~merged_df['nom_region_ou_departement'].str.lower().str.contains('dom-tom-com|étranger')]

   
    #return filtered_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Grouper par code_reg et calculer les statistiques pour chaque groupe
    result_by_regions = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',  # Prendre le premier nom de la région
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()

    result_by_regions.columns = ['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    result_by_regions.set_index('code_reg', inplace=True)
    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')

    merged_data = pd.merge(geo_data, referendum_result_by_regions, how='inner', left_on='code', right_index=True)

    # Calculer le ratio de 'Choice A' par rapport au total des votes exprimés
    merged_data['ratio'] = merged_data['Choice A'] / (merged_data['Choice A'] + merged_data['Choice B'])
    merged_data.plot(column='ratio', cmap='Blues', legend=True, figsize=(10, 10))
    plt.title("Referendum Results: Ratio of 'Choice A'")

    return merged_data[['geometry', 'ratio']]


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    print(regions_and_departments[0:2])
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(referendum_and_areas[0:2])
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()