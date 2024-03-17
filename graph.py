import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file line by line and parse it manually
data = []
with open("output.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        team_name = parts[0]
        submission_time = pd.to_datetime(parts[1])
        data.append({"team_name": team_name, "submission_time": submission_time})

# Create DataFrame from parsed data
df = pd.DataFrame(data)

# Sort DataFrame by submission time
df = df.sort_values(by="submission_time")

# Group by team and calculate cumulative count of submissions
df["cumulative_submissions"] = df.groupby("team_name").cumcount() + 1

# Calculate total submissions for each team
total_submissions = df.groupby("team_name")["cumulative_submissions"].max()

# Select top 10 teams based on cumulative submission count
top_10_teams = total_submissions.nlargest(10).index
df_top_10 = df[df["team_name"].isin(top_10_teams)]

# Plot the graph
plt.figure(figsize=(12, 6))

for team_name, team_data in df_top_10.groupby("team_name"):
    truncated_team_name = team_name[:10]  # Truncate team name to at most 10 characters
    plt.step(
        team_data["submission_time"],
        team_data["cumulative_submissions"],
        label=truncated_team_name,
    )

    # Mark final submission with an 'X'
    final_submission_time = team_data["submission_time"].iloc[-1]
    final_submission_count = team_data["cumulative_submissions"].iloc[-1]
    plt.scatter(final_submission_time, final_submission_count, marker="x", color="red")

plt.title("Progress of Top 10 Teams Over Time")
plt.xlabel("Submission Time")
plt.ylabel("Cumulative Submissions")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.xticks(rotation=45)
plt.yticks(
    range(1, df_top_10["cumulative_submissions"].max() + 1, 10)
)  # Set y-axis ticks from 1 to max cumulative submissions
plt.tight_layout()

# Save the graph as an image
plt.savefig(
    "top_10_teams_progress_over_time_with_final_submission_and_y_increment.png",
    bbox_inches="tight",
)

plt.show()
