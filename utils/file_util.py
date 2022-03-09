import csv


def read_from_file(file_name):
    opts = list()
    try:
        with open(file_name, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                opts.append(row)
    except IOError:
        print("I/O error")

    return opts


def save_to_file(file_name, csv_columns, opts):
    csv_file = file_name
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in opts:
                writer.writerow(data.__dict__)
    except IOError:
        print("I/O error")
