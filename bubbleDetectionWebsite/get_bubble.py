import os
import subprocess


def run_r_script(r_script_path, filename):
    if not os.path.exists(r_script_path):
        print(f"Error: File '{r_script_path}' does not exist.")
        exit()

    if not os.path.exists('data/'+filename+'.csv'):
        print(
            f"Error: File 'data/{filename}.csv' does not exist in 'data/'.")
        exit()

    if not os.path.exists('data/'+filename+'.csv'):
        print(
            f"Error: File 'data/'+{filename}+'.csv' does not exist in 'data/ind95/'.")
        print("Please run the 'get_ind95 first.")
        exit()

    # Run R script using subprocess and pass the CSV file path as an argument
    process = subprocess.Popen(['Rscript', r_script_path, filename],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output
    stdout, stderr = process.communicate()

    # Print output and error messages
    print("Output:", stdout.decode())
    print("Errors:", stderr.decode())

    # Check the return code
    if process.returncode == 0:
        print("R script executed successfully.")
    else:
        print("Error executing R script. Return code:", process.returncode)


if __name__ == "__main__":
    # Define the path to the CSV file
    r_script_path = 'r_scripts/bubble.R'
    filename = 'BTCUSDT_2022_2024'
    run_r_script(r_script_path, filename)
