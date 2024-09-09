# Manual NSE File Format for Lysimeter Analysis
Created by A.J. Brown

This document outlines the format for the manual Non-Standard Event (NSE) file, which is used in the lysimeter data analysis. Proper management of a weighing lysimeter involves identifying and accounting for NSEs to ensure the accuracy of evapotranspiration (ET) measurements. NSEs can be detected automatically by the system or manually defined by the user.

## Understanding Non-Standard Events (NSEs)

Non-Standard Events (NSEs) refer to periods during the lysimeter measurement cycle where conditions deviate from normal (i.e., weight changing only due to ET) due to factors such as irrigation, precipitation, drainage, harvests, counter weight adjustments, or other activities. These events can significantly impact the accuracy of ET measurements. 

### Key Concepts

- **Non-Standard Day (NSD):** A day where one or more NSEs occur.
- **NSE (Non-Standard Event):** Specific events such as rain, irrigation, or other activities that affect lysimeter measurements.


Identifying and managing NSEs is crucial because these events can introduce spikes or anomalies in the data, which, if not accounted for, can lead to incorrect ET calculations. Best practices involve both automatic detection of NSEs and the manual identification of events to ensure a comprehensive understanding of the data.

## Manual NSE File Format

The manual NSE file is a CSV file containing the following columns. The file allows users to manually define NSEs that might not be automatically detected but are crucial for accurate data analysis.

### Required Columns

| Column Name        | Description                                                         |
|--------------------|---------------------------------------------------------------------|
| `Event Type`       | The type of event (e.g., Rain, Irrigation, Drain, Unknown).         |
| `Start Datetime`   | The starting date and time of the event (format: MM/DD/YYYY HH:MM). |
| `Stop Datetime`    | The ending date and time of the event (format: MM/DD/YYYY HH:MM).   |
| `Notes`            | Any additional notes or comments about the event (optional).        |

### Example File Content

```plaintext
Event Type,Start Datetime,Stop Datetime,Notes
Rain,6/1/2022 0:10,6/1/2022 10:20,
Irrigation,6/3/2022 10:35,6/3/2022 11:30,
Rain,6/6/2022 14:55,6/6/2022 15:10,
Unknown,6/12/2022 7:30,6/12/2022 8:00,Unsure what caused this
Irrigation,6/13/2022 8:35,6/13/2022 10:05,
...
