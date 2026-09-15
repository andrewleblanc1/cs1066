### Plot the scraped and saved Google Trends data
### m01e/trends_plot.py
### 
### Author: Sharon Zhou and Mike Smith
### Date: 20250916
###
### Original idea and code from https://brightdata.com/blog/web-data/how-to-scrape-google-trends

import pandas as pd
import matplotlib.pyplot as plt


def plot_interest_data(csv_file, output_file='interest_data.png'):
    """Create the interest bar graph from a CSV filename or file-like object."""
    df = pd.read_csv(csv_file)
    print("Read CSV data")
    print(df.head())

    # Plot the data in a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(df['Region'], df['Interest'], color='skyblue')

    # Add labels and title
    plt.xlabel('Region')
    plt.ylabel('Interest')
    plt.title('Google Trends Interest by Region')

    # Rotate the x-axis labels for readability
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    print(f"Saved plot to {output_file}")


def main():
    plot_interest_data('scraped_data.csv')


if __name__ == "__main__":
    main()