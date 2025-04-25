import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculate_glucose_ranges(data):
    """
    Calculate low, high, bg_min, and bg_max for a participant's data. 
    """
    low_value = data['blood_glucose_value'].quantile(0.05)  # 5th percentile as low value
    high_value = data['blood_glucose_value'].quantile(0.95)  # 95th percentile as high value
    bg_min = data['blood_glucose_value'].min()  # Minimum blood glucose value
    bg_max = data['blood_glucose_value'].max()  # Maximum blood glucose value
    return low_value, high_value, bg_min, bg_max

def calculate_glucose_analysis(data, low_range=70, high_range=140):
    """
    Calculate glucose analysis metrics for a participant's data.
    """
    mean_blood_glucose = data['blood_glucose_value'].mean()
    std_dev = data['blood_glucose_value'].std()
    cv_percent = (std_dev / mean_blood_glucose) * 100
    tir_percent = len(data[(data['blood_glucose_value'] >= low_range) & (data['blood_glucose_value'] <= high_range)]) / len(data) * 100
    tar_percent = len(data[data['blood_glucose_value'] > high_range]) / len(data) * 100
    tbr_percent = len(data[data['blood_glucose_value'] < low_range]) / len(data) * 100
    return mean_blood_glucose, std_dev, cv_percent, tir_percent, tar_percent, tbr_percent

def plot_and_save_graph(data, pid, output_dir, low_value, high_value, bg_min, bg_max):
    """
    Plot and save the blood glucose graph for a participant.
    """
    # Extract the day from the timestamp
    data = data.copy()
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['time_in_hours'] = (data['timestamp'] - data['timestamp'].min()).dt.total_seconds() / 3600  # Convert to hours
    data['time_in_days'] = data['time_in_hours'] / 24  # Convert to days
    data.loc[:, 'day'] = data['timestamp'].dt.date

    # Assign a unique color to each day
    unique_days = data['day'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_days)))
    day_color_map = dict(zip(unique_days, colors))

    # Plot the data with colors representing each day
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle(f'Blood glucose vs time for Participant {pid}. Range: [{bg_min}, {bg_max}]\n \
                    Alerts for Low, High are mapped to {low_value}, {high_value:.4f}\n \
                    Study Group: {data["study_group"].values[0]}\n')

    for day, color in day_color_map.items():
        day_data = data[data['day'] == day]
        ax.plot(day_data['time_in_days'], day_data['blood_glucose_value'], label=str(day), color=color)

    # Calculate glucose analysis metrics
    mean_blood_glucose, std_dev, cv_percent, tir_percent, tar_percent, tbr_percent = calculate_glucose_analysis(data)

    # Add glucose analysis results below the graph in the second column
    analysis_text = (
        f"Participant `{pid}` Glucose Analysis:\n"
        f"Mean Blood Glucose (MBG): {mean_blood_glucose:.2f} mg/dL\n"
        f"Glucose Variability (S.D.): {std_dev:.2f} mg/dL\n"
        f"Coefficient of Variation (CV%): {cv_percent:.2f}%\n"
        f"Time in Range (TIR): {tir_percent:.2f}%\n"
        f"Time Above Range (TAR): {tar_percent:.2f}%\n"
        f"Time Below Range (TBR): {tbr_percent:.2f}%"
    )
    ax.text(1.02, 0, analysis_text, transform=ax.transAxes, fontsize=10, verticalalignment='center', bbox=dict(facecolor='white', alpha=0.5))

    ax.set_xlabel("Time (Days)")  # Set x-axis label
    ax.set_ylabel("Blood Glucose Value (mg/dL)")  # Set y-axis label
    ax.set_title("Blood Glucose value vs time index")
    ax.legend(title="Day", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot
    plot_path = os.path.join(output_dir, f'participant_{pid}.png')
    plt.savefig(plot_path)
    plt.close(fig)



pilot_data_root = "C:/Users/nikhi/Box/AI-READI/nikhil working dataset/dataset/"  # change this to your own path
# List of batch files to process
indices = [0, 100, 200, 300, 400, 500, 600, 700, 784]
batch_files = [f"cleaned_data/batch_{indices[i]}_{indices[i+1]}.csv" for i in range(len(indices) - 1)]


# Create the directory if it doesn't exist
output_dir = os.path.join(pilot_data_root, "healthy_plots")
os.makedirs(output_dir, exist_ok=True)

# Process each batch file
for batch_file in batch_files:
    batch_path = os.path.join(pilot_data_root, batch_file)
    if os.path.exists(batch_path):
        # Read the batch file using pandas
        df = pd.read_csv(batch_path)

        # Get the list of participant IDs
        participants = df['participant_id'].unique()  # List of all participants

        # Plot and save the graph for each participant
        for pid in participants:
            participant_data = df[df['participant_id'] == pid]
            # Calculate glucose ranges
            low_value, high_value, bg_min, bg_max = calculate_glucose_ranges(participant_data)
            # Plot and save the graph
            plot_and_save_graph(participant_data, pid, output_dir, low_value, high_value, bg_min, bg_max)

print(f"Plots saved in {output_dir}")
