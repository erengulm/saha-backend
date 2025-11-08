# members/management/commands/load_locations.py
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from members.location_models import City, District, Neighborhood


class Command(BaseCommand):
    help = 'Load Turkish administrative data (cities, districts, neighborhoods) from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='turkiye-administrative.csv',
            help='CSV file name (default: turkiye-administrative.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing location data before loading'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        csv_path = os.path.join(settings.BASE_DIR, csv_file)
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_path}')
            )
            return

        if options['clear']:
            self.stdout.write('Clearing existing location data...')
            Neighborhood.objects.all().delete()
            District.objects.all().delete()
            City.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        self.stdout.write(f'Loading data from {csv_path}...')
        
        cities_created = 0
        districts_created = 0
        neighborhoods_created = 0
        
        city_cache = {}
        district_cache = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Debug: Print column headers
                headers = reader.fieldnames
                self.stdout.write(f'CSV Headers: {headers}')
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 since header is row 1
                    try:
                        city_name = row.get('city', '').strip() if 'city' in row else row.get('City', '').strip()
                        district_name = row.get('district', '').strip() if 'district' in row else row.get('District', '').strip()
                        neighborhood_name = row.get('neighborhood', '').strip() if 'neighborhood' in row else row.get('Neighborhood', '').strip()
                        
                        # Additional cleaning for any extra whitespace issues
                        city_name = ' '.join(city_name.split())
                        district_name = ' '.join(district_name.split())
                        neighborhood_name = ' '.join(neighborhood_name.split())
                        
                        # Handle potential trailing spaces in column names
                        if not neighborhood_name:
                            for key in row.keys():
                                if 'neighborhood' in key.lower():
                                    neighborhood_name = row[key].strip()
                                    break
                        
                        if not all([city_name, district_name, neighborhood_name]):
                            self.stdout.write(
                                self.style.WARNING(f'Row {row_num}: Skipping empty data - City: "{city_name}", District: "{district_name}", Neighborhood: "{neighborhood_name}"')
                            )
                            self.stdout.write(f'Row data: {row}')
                            continue
                        
                        # Get or create city
                        if city_name not in city_cache:
                            city, created = City.objects.get_or_create(name=city_name)
                            city_cache[city_name] = city
                            if created:
                                cities_created += 1
                        else:
                            city = city_cache[city_name]
                        
                        # Get or create district
                        district_key = f"{city_name}|{district_name}"
                        if district_key not in district_cache:
                            district, created = District.objects.get_or_create(
                                city=city,
                                name=district_name
                            )
                            district_cache[district_key] = district
                            if created:
                                districts_created += 1
                        else:
                            district = district_cache[district_key]
                        
                        # Create neighborhood (allow duplicates in case of CSV data inconsistencies)
                        neighborhood, created = Neighborhood.objects.get_or_create(
                            district=district,
                            name=neighborhood_name
                        )
                        if created:
                            neighborhoods_created += 1
                        
                        # Progress indicator
                        if row_num % 1000 == 0:
                            self.stdout.write(f'Processed {row_num} rows...')
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Row {row_num}: Error processing data - {str(e)}')
                        )
                        continue
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {str(e)}')
            )
            return
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nData loading completed!\n'
                f'Cities created: {cities_created}\n'
                f'Districts created: {districts_created}\n'
                f'Neighborhoods created: {neighborhoods_created}\n'
                f'Total cities: {City.objects.count()}\n'
                f'Total districts: {District.objects.count()}\n'
                f'Total neighborhoods: {Neighborhood.objects.count()}'
            )
        )