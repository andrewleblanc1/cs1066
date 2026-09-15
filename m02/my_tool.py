import csv
import io
import os
import re

from trends_save import get_interest_data
from trends_plot import plot_interest_data


def normalize_query(query):
	"""Return a lowercase query containing alphabetic characters only."""
	return re.sub(r'[^a-z]', '', query.lower())


def main():
	query = input("Enter a phrase or search term: ")
	interest_data = get_interest_data(query)
	filename_query = normalize_query(query)
	output_file = f"interest_data_{filename_query}.png"

	# Keep the CSV representation in memory for the plotting function.
	csv_data = io.StringIO()
	writer = csv.DictWriter(csv_data, fieldnames=['Region', 'Interest'])
	writer.writeheader()
	for region, interest in interest_data.items():
		writer.writerow({'Region': region, 'Interest': interest})

	csv_data.seek(0)
	if os.path.exists(output_file):
		while True:
			overwrite = input(
				f"The file {output_file} already exists. Override it? (y/n): "
			).lower()
			if overwrite == 'y':
				break
			if overwrite == 'n':
				print(f"Keeping existing file {output_file}")
				return
			print("Please enter y or n.")

	plot_interest_data(csv_data, output_file)


if __name__ == "__main__":
	main()
