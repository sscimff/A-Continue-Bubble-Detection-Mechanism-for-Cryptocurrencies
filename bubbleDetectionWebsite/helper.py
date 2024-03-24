import subprocess
import os
from dotenv import load_dotenv
from binance.client import Client
import csv
import pandas as pd
import pytz
import pyreadr
from datetime import datetime
from django.utils import timezone
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'bubbleDetectionWebsite.settings')
django.setup()
from crypto.models import Crypto, PriceData, BubbleDuration

# Get data by Binance API


def get_data(pair, start, end):
    print("{:<35}".format("get_data") + "running...", end="")
    
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")

    client = Client(API_KEY, SECRET_KEY)
    interval = Client.KLINE_INTERVAL_4HOUR
    candles = client.get_historical_klines(pair, interval, start, end)
    
    print(" Done!")

    return candles

# Store data into csv


def price_to_csv(pair, candles, filepath):
    print("{:<35}".format("price_to_csv") + "running...", end="")

    data = []
    for candle in candles:
        open_time = datetime.fromtimestamp(
            candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        close_time = datetime.fromtimestamp(
            candle[6] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        data.append({
            "pair": pair,
            "open_time": open_time,
            "close_time": close_time,
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            "volume": candle[5]
        })
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(" Done!")



def price_to_db(pair, candles):
    print("{:<35}".format("price_to_db") + "running...", end="")
    
    try:
        crypto_instance = Crypto.objects.get(pair=pair)
    except Crypto.DoesNotExist:
        # If the Crypto instance doesn't exist, create a new one
        crypto_instance = Crypto.objects.create(pair=pair)

    data = []
    for candle in candles:
        open_time = datetime.fromtimestamp(
            candle[0]/1000).astimezone(pytz.utc)
        close_time = datetime.fromtimestamp(
            candle[6]/1000).astimezone(pytz.utc)

        crypto_data = PriceData(
            pair=crypto_instance,
            open_time=open_time,
            close_time=close_time,
            open=candle[1],
            high=candle[2],
            low=candle[3],
            close=candle[4],
            volume=candle[5]
        )
        data.append(crypto_data)

    PriceData.objects.bulk_create(data)
    print(" Done!")


def run_r_script(r_script, filename):
    print("{:<35}".format(r_script) + "running...")

    if (check_path == False):
        exit()

    # Run R script using subprocess and pass the CSV file path as an argument
    process = subprocess.Popen(['Rscript', r_script, filename],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output
    stdout, stderr = process.communicate()

    # Decode output if needed (Python 3)
    stdout = stdout.decode()
    stderr = stderr.decode()

    # Print output and error messages
    print("Output:", stdout)
    print("Errors:", stderr)

    # Check the return code
    if process.returncode == 0:
        print("R script executed successfully.")
    else:
        print("Error executing R script. Return code:", process.returncode)
    print(filename + ": Done!")


def check_path(r_script, filename):
    if not os.path.exists(r_script):
        print(f"Error: File '{r_script}' does not exist.")
        return False

    if not os.path.exists('data/'+filename+'.csv'):
        print(
            f"Error: File 'data/{filename}.csv' does not exist in 'data/'.")
        return False

    if not os.path.exists('data/'+filename+'.csv'):
        print(
            f"Error: File 'data/'+{filename}+'.csv' does not exist in 'data/ind95/'.")
        print("Please run the 'get_ind95 first.")
        return False


def bubble_to_db(pair, rds_file_path):
    try:
        # Read the CSV file
        with open(rds_file_path, 'r') as file:
            reader = csv.DictReader(file)

            # Iterate over each row in the CSV file
            for row in reader:
                # Skip rows with NA values
                if 'NA' in row.values():
                    print("Skipping row with NA values.")
                    continue

                # Convert string dates from CSV to datetime objects
                start_date = datetime.strptime(
                    row['start_date'], '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(
                    row['end_date'], '%Y-%m-%d %H:%M:%S')
                print(start_date)

                # Get or create the Crypto instance
                crypto_instance, created = Crypto.objects.get_or_create(
                    pair=pair)

                # Create a BubbleDuration instance
                bubble_duration = BubbleDuration.objects.create(
                    pair=crypto_instance,
                    start_date=start_date,
                    end_date=end_date
                )

                # Save the BubbleDuration instance
                bubble_duration.save()
            print("ALL DONE!")

    except Exception as e:
        print(f"An error occurred: {e}")

# For testing
# def add_bubble():
#     data = [
#         {"pair_id": 2, "start_date": "2022-07-09 00:00:00",
#             "end_date": "2022-07-09 00:00:00"},
#         {"pair_id": 2, "start_date": "2022-07-20 04:00:00",
#             "end_date": "2022-07-21 00:00:00"},
#         {"pair_id": 2, "start_date": "2022-08-19 12:00:00",
#             "end_date": "2022-08-20 16:00:00"},
#         {"pair_id": 2, "start_date": "2022-08-21 00:00:00",
#             "end_date": "2022-08-21 00:00:00"}
#     ]

#     for item in data:
#         pair_id = item['pair_id']
#         start_date = timezone.make_aware(datetime.strptime(
#             item['start_date'], "%Y-%m-%d %H:%M:%S"))
#         end_date = timezone.make_aware(datetime.strptime(
#             item['end_date'], "%Y-%m-%d %H:%M:%S"))

#         bubble_duration = BubbleDuration(
#             pair_id=pair_id, start_date=start_date, end_date=end_date)
#         bubble_duration.save()


if __name__ == "__main__":
    pair = 'BTCUSDT'
    start = '2023-02-01'
    end = '2024-03-20'

    filename = pair + "_" + start + "_" + end
    
    if not os.path.exists('data/'+filename+'.csv'):
        data = get_data(pair, start, end)

        price_to_csv(pair, data, "data/" + filename + ".csv")
        price_to_db(pair, data)

        run_r_script('r_scripts/get_ind95.R', filename)
        run_r_script('r_scripts/get_bubble.R', filename)

        bubble_file_path = "data/bubble/" + pair + \
            "_" + start + "_" + end + "_bubble.RDS"
    else :
        print("This duration has been calculate!")
    # bubble_to_db(pair, bubble_file_path)
    # add_bubble()
