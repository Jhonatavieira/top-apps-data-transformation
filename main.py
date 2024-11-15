"""
Project: Pipeline for ETL
This code analyzes the top apps through the category rate and reviews, 
after inserting the date into the sqlite3 table
"""

import sqlite3
import pandas as pd


def extract_file(file_path):
    """Just read the file and return the object
    Arg:
        file_path: (string)

    return:
        Data: DataFrame
    """
    data = pd.read_csv(file_path)

    # Now, print details about the file
    print(f"Here is a little bit of information about the data stored in {
          file_path}")
    print(f"\nThere are {data.shape[0]} rows and {
          data.shape[1]} columns in this DataFrame.")
    print("\nThe columns in this DataFrame take the following types:")

    # Print type each column
    print(data.dtypes)

    # Finally, print a message before retorn the DataFrame
    print(f"\nto view the DataFrame extracted from {
          file_path}, display the value returned by this function!\n\n")

    return data


def transform(apps, reviews, category, min_rating, min_reviews):
    """Clean and return the data transformed
    ARGS:
        apps: DataFrame
        reviews: DataFrame
        category: String
        min_rating: int
        min_reviews: float

    return:
        Data: DataFrame
    """

    # Print statement for observability
    print(f"Transforming data to curate a dataset with all "
          f"{category} and their "
          f"corresponding reviews with a rating of at least {min_rating} and "
          f"{min_reviews} reviews\n")

    # Drop any duplicates from both DataFrames
    # (also have the option to do this in-place)
    reviews = reviews.drop_duplicates()
    apps = apps.drop_duplicates(["App"])

    # Find all of apps and reviews in the food and drink category
    subset_apps = apps.loc[apps["Category"] == category, :]
    subset_reviews = reviews.loc[reviews["App"].isin(subset_apps["App"]), [
        "App", "Sentiment_Polarity"]]

    # Aggregate the subset_reviews DataFrame
    aggregate_reviews = subset_reviews.groupby(by="App").mean()

    # Join it back the subset_apps table
    joined_apps_reviews = subset_apps.join(aggregate_reviews,
                                           on="App", how="left")

    # Keep only to the need columns
    filtered_apps_reviews = joined_apps_reviews.loc[:, [
        "App", "Rating", "Reviews", "Installs", "Sentiment_Polarity"]]

    # Convert reviews
    filtered_apps_reviews = filtered_apps_reviews.astype({"Reviews": "int32"})

    # Keep only valeus with an average rating of at least of 4 stars,
    # And at leat 1000 reviews
    top_apps = filtered_apps_reviews.loc[
        (filtered_apps_reviews["Rating"] > min_rating) &
        (filtered_apps_reviews["Reviews"] > min_reviews), :]

    # Sort the top apps, replace NaN with 0, reset the index (drop, inplace)
    top_apps.sort_values(by=["Rating", "Reviews"],
                         ascending=False, inplace=True)

    top_apps.reset_index(drop=True, inplace=True)

    # Persist this DataFrame as top_apps.csv
    top_apps.to_csv("top_apps.csv")

    print(f"The transformed DataFrame, which includes {top_apps.shape[0]} "
          f"rows and {top_apps.shape[1]} "
          "columns has been persisted, and will now be "
          "returned ")

    return top_apps


def load(dataframe, database_name, table_name):
    """Fuction to load in the sqlite3

    Args:
        dataframe: Dataframe
        database_name: string
        table_name: string

    return:
        There's no return
    """

    # Create a connection object
    con = sqlite3.connect(database_name)

    # Write the data to the specified table (table_name)
    dataframe.to_sql(name=table_name, con=con,
                     if_exists="replace", index=False)
    print("Original DataFrame has been loaded to sqlite3\n")

    # Read the data and return the result (it is to be used)
    loaded_dataframe = pd.read_sql(sql=f"select * from {table_name}", con=con)
    print("The loaded DataFrame has been read from sqlite for validation\n")

    try:
        assert dataframe.shape == loaded_dataframe.shape
        print(f"Sucess! The data in the {table_name}"
              "table has sucessfully been loaded and validated")

    except AssertionError:
        print("DataFrame shape is not consistent"
              "before and after loaded. Take a closer!")


if __name__ == '__main__':
    app_data = extract_file("apps_data.csv")
    reviews_data = extract_file("review_data.csv")

    top_app_data = transform(
        apps=app_data,
        reviews=reviews_data,
        category="FOOD_AND_DRINK",
        min_rating=4.0,
        min_reviews=1000
    )

    load(
        dataframe=top_app_data,
        database_name="market_research",
        table_name="top_apps"
    )

    print(top_app_data)
