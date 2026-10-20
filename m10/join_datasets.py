import csv
import re
import sys
from pathlib import Path


FOLDER = Path(__file__).resolve().parent
OUTPUT_PREFIX = "combined_dataset"
PHONE_JOIN_FILES = {"datasetb", "datasetc"}


def input_suffix(path):
    prefix = "dataset"
    if path.stem.casefold().startswith(prefix):
        return path.stem[len(prefix):]
    return path.stem


def list_input_files():
    return sorted(
        path
        for path in FOLDER.glob("*.csv")
        if not path.stem.casefold().startswith(OUTPUT_PREFIX.casefold())
    )


def choose_input_files(files):
    if len(files) < 2:
        raise ValueError("At least two input CSV files must be in this folder.")

    print("CSV files available to join:")
    for index, path in enumerate(files, start=1):
        print(f"{index}. {path.name}")

    choices = []
    for label in ("first", "second"):
        while True:
            answer = input(f"Enter the number for the {label} file: ").strip()
            try:
                choice = int(answer)
                if 1 <= choice <= len(files):
                    if choice - 1 not in choices:
                        choices.append(choice - 1)
                        break
                    print("Choose a different file; each input must be distinct.")
                else:
                    print(f"Enter a number from 1 to {len(files)}.")
            except ValueError:
                print("Enter a file number.")

    return files[choices[0]], files[choices[1]]


def read_dataset(path, key_name):
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)
        if not headers:
            raise ValueError(f"{path.name} is empty or has no header row.")

        headers = [header.strip() for header in headers]
        normalized_headers = [header.casefold() for header in headers]
        if any(not header for header in headers):
            raise ValueError(f"{path.name} contains an empty column name.")
        if len(set(normalized_headers)) != len(headers):
            raise ValueError(f"{path.name} contains duplicate column names.")
        try:
            key_index = normalized_headers.index(key_name)
        except ValueError as error:
            raise ValueError(
                f"{path.name} must contain a '{key_name}' column."
            ) from error

        rows = []
        for row_number, values in enumerate(reader, start=2):
            if len(values) != len(headers):
                raise ValueError(
                    f"{path.name} row {row_number} has {len(values)} values; "
                    f"expected {len(headers)}."
                )
            row = dict(zip(headers, values))
            if key_name == "phone":
                row[headers[key_index]] = normalize_phone(row[headers[key_index]])
            rows.append(row)

    return headers, key_index, rows


def normalize_phone(phone):
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:]
    return digits


def unique_column_name(header, used_names, source_name):
    candidate = header
    if candidate.casefold() in used_names:
        candidate = f"{header}_{source_name}"
        suffix = 2
        while candidate.casefold() in used_names:
            candidate = f"{header}_{source_name}_{suffix}"
            suffix += 1
    used_names.add(candidate.casefold())
    return candidate


def join_datasets(first_path, second_path):
    output_file = FOLDER / (
        f"{OUTPUT_PREFIX}{input_suffix(first_path)}{input_suffix(second_path)}.csv"
    )
    phone_join = {
        first_path.stem.casefold(),
        second_path.stem.casefold(),
    } == PHONE_JOIN_FILES
    key_name = "phone" if phone_join else "email"
    first_headers, first_key_index, first_rows = read_dataset(first_path, key_name)
    second_headers, second_key_index, second_rows = read_dataset(
        second_path, key_name
    )
    first_key = first_headers[first_key_index]
    second_key = second_headers[second_key_index]

    output_headers = list(first_headers)
    used_names = {header.casefold() for header in output_headers}
    second_columns = []
    for index, header in enumerate(second_headers):
        if index == second_key_index:
            continue
        output_name = unique_column_name(
            header, used_names, second_path.stem
        )
        output_headers.append(output_name)
        second_columns.append((header, output_name))

    second_rows_by_key = {}
    for row in second_rows:
        key = row[second_key].strip().casefold()
        if key:
            second_rows_by_key.setdefault(key, []).append(row)

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=output_headers)
        writer.writeheader()
        joined_count = 0
        for first_row in first_rows:
            key = first_row[first_key].strip().casefold()
            if not key:
                continue
            for second_row in second_rows_by_key.get(key, []):
                output_row = dict(first_row)
                output_row.update(
                    {
                        output_name: second_row[header]
                        for header, output_name in second_columns
                    }
                )
                writer.writerow(output_row)
                joined_count += 1

    return joined_count, output_file


def main():
    try:
        first_path, second_path = choose_input_files(list_input_files())
        joined_count, output_file = join_datasets(first_path, second_path)
    except (OSError, csv.Error, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(
        f"Joined {joined_count} matching rows from {first_path.name} and "
        f"{second_path.name}."
    )
    print(f"Output saved to {output_file.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
