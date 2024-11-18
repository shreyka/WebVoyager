import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse


def get_times(lines):
    # Extract timing values
    total_times = []
    encode_times = []
    api_times = []

    for line in lines:
        if 'Total processing time:' in line:
            total_times.append(float(line.split(':')[1].split()[0]))
        elif 'Time taken to encode image:' in line:
            encode_times.append(float(line.split(':')[1].split()[0]))
        elif 'API call duration:' in line:
            api_times.append(float(line.split(':')[1].split()[0]))

    return total_times, encode_times, api_times

def read_log(folder, task_name):
    file_path = os.path.join(folder, task_name, "agent.log")
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines

def plot_timing(folder, task_name = "taskCambridge Dictionary--29"): 
    # Read the log file
    lines = read_log(folder, task_name)

    total_times, encode_times, api_times = get_times(lines)

    # Create x-axis values (iteration numbers)
    x = range(len(total_times))

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, total_times, 'b-', label='Total Processing Time')
    plt.plot(x, encode_times, 'r-', label='Image Encode Time') 
    plt.plot(x, api_times, 'g-', label='API Call Duration')

    plt.xlabel('Iteration')
    plt.ylabel('Time (seconds)')
    plt.title('Processing Times per Iteration')
    plt.legend()
    plt.grid(True)

    # Save the plot
    save_path = os.path.join(folder, "timing_plot.png")
    plt.savefig(save_path)
    plt.close()


def compare_total_timing(folders):
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot total times for each folder
    for folder in folders:
        lines = read_log(folder, "taskCambridge Dictionary--29")
        total_times, _, _ = get_times(lines)
        
        # Create x-axis values (iteration numbers)
        x = range(len(total_times))
        
        # Get folder name for legend
        folder_name = os.path.basename(folder)
        plt.plot(x, total_times, '-', label=folder_name)

    plt.xlabel('Iteration')
    plt.ylabel('Time (seconds)')
    plt.title('Total Processing Times Comparison')
    plt.legend()
    plt.grid(True)

    # Save the plot
    plt.show()




if __name__ == '__main__': 
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--folder", type=str, help="Path to the folder containing task_name/agent.log")
    # args = parser.parse_args()

    # plot_timing(args.folder)
    compare_total_timing(["results/20241118_12_23_49", "results/20241118_12_29_40", "results/20241118_12_41_51"])