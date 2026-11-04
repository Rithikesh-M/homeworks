from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    folder = Path(__file__).resolve().parent
    # Some counts use thousands separators, such as "1,071".
    data = pd.read_csv(folder / "bicycle_data.csv", thousands=",")
    # Count each reading once if an export contains identical duplicate rows.
    data = data.drop_duplicates().copy()

    # Date is the start of each hour and should be a datetime, not a string.
    # East and West are bicycle counts on each sidewalk. They should be whole
    # numbers; pandas' nullable Int64 also allows a count to be missing.
    # Some exports include a total column, which is also an integer count.
    # Shorten the sidewalk labels, including names used in earlier exports.
    data = data.rename(columns={
        "Fremont Bridge East Sidewalk": "East",
        "Fremont Bridge West Sidewalk": "West",
        "Fremont Bridge NB": "East",
        "Fremont Bridge SB": "West",
        "Fremont Bridge Total": "Reported total",
        "Fremont Bridge Sidewalks, south of N 34th St Cyclist East Sidewalk": "East",
        "Fremont Bridge Sidewalks, south of N 34th St Cyclist West Sidewalk": "West",
        "Fremont Bridge Sidewalks, south of N 34th St Total": "Reported total",
    })
    # format="mixed" accepts ISO dates as well as the CSV's AM/PM dates.
    # In ISO dates, T is a literal separator, not a tab character.
    data["Date"] = pd.to_datetime(data["Date"], format="mixed", errors="raise")
    if data["Date"].isna().any():
        raise ValueError("Some rows have no date, so their year is unknown.")
    for column in ["East", "West", "Reported total"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="raise").astype("Int64")

    # Addition keeps a total missing if either sidewalk count is missing.
    data["Total"] = data["East"] + data["West"]
    data["Hour"] = data["Date"].dt.hour
    data["Year"] = data["Date"].dt.year
    data_2016 = data.loc[data["Year"] == 2016].copy()
    if data_2016.empty:
        raise ValueError("The CSV contains no data for 2016.")

    missing_counts = data_2016[["East", "West"]].isna().any(axis=1)
    # Also check for hourly timestamps that are absent from the CSV entirely.
    expected_hours = pd.date_range("2016-01-01", "2016-12-31 23:00", freq="h")
    absent_hours = expected_hours.difference(data_2016["Date"])
    print(f"2016 rows with missing counts: {missing_counts.sum()}")
    print(f"2016 timestamps absent from the CSV: {len(absent_hours)}")
    # 2016 has 1 point with missing counts: March 13 at 02:00.
    # No hourly timestamps are absent in the 2016 data.
    # Exclude incomplete hours instead of treating an unknown count as zero.
    # Absent timestamps contribute no observations to the hourly averages.
    data_2016 = data_2016.loc[~missing_counts].copy()
    if data_2016.empty:
        raise ValueError("There are no complete bicycle counts for 2016.")

    hourly_counts = data_2016.groupby("Hour")["Total"].mean().reindex(range(24))
    busiest_hour = int(hourly_counts.idxmax())
    # Busiest hour: 17:00-18:00 (5-6 p.m.), averaging 399.03 bicycles.
    print(f"Busiest hour: {busiest_hour:02d}:00-{busiest_hour + 1:02d}:00")
    print(f"Average count at that hour: {hourly_counts.loc[busiest_hour]:.2f}")

    ax = hourly_counts.plot(marker="o", figsize=(9, 5))
    ax.set_title("Fremont Bridge bicycle counts by hour, 2016")
    ax.set_xlabel("Hour of day (0-23)")
    ax.set_ylabel("Average daily bicycle count (East + West)")
    ax.set_xticks(range(24))
    ax.grid(axis="y", alpha=0.3)
    ax.figure.tight_layout()
    output = folder.parents[1] / "counts_by_hour.png"
    ax.figure.savefig(output, dpi=150)
    plt.close(ax.figure)
    print(f"Saved plot to {output}")


if __name__ == "__main__":
    main()
