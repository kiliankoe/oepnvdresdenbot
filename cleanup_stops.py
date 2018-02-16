import csv

with open('stations.csv', encoding='ISO-8859-1') as infile, open('all_stops.csv', 'w', encoding='utf-8') as outfile:
    csv_reader = csv.DictReader(infile, delimiter=';')
    csv_writer = csv.writer(outfile, delimiter=';')
    for idx, row in enumerate(csv_reader):
        csv_writer.writerow([idx,
                            row['Name ohne Ort'],
                            row['Ort'],
                            float(row['WGS84_Y'].replace(',', '.')),
                            float(row['WGS84_X'].replace(',', '.'))])
