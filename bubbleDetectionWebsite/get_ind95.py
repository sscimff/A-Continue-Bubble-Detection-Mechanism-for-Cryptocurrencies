import os
import subprocess

# Replace 'path/to/your/script.R' with the actual path to your R script
r_script_path = 'r_scripts/get_ind95.R'
filename = 'BTCUSDT_2024-01-01_2024-03-03'


if not os.path.exists(r_script_path):
    print(f"Error: File '{r_script_path}' does not exist.")
    exit()

if not os.path.exists('data/'+filename+'.csv'):
    print(f"Error: File 'data/{filename}.csv' does not exist.")
    exit()
# Run R script using subprocess and pass the CSV file path as an argument
process = subprocess.Popen(['Rscript', r_script_path, filename],
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
