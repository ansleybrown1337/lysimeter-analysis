# Lysimeter Data Input Format
Created by A.J. Brown, 30 Aug 2024

This document outlines the required and optional columns for the lysimeter data files. Each column in the data file is identified by a unique name and associated description.

## Required Columns

These columns must be present as shown below in the lysimeter data file (`.dat`) for successful processing.

| Column Name          | Description                                                       |
|----------------------|-------------------------------------------------------------------|
| `TIMESTAMP`          | The timestamp for each recorded data point.                      |
| `RECORD`             | The record number for each entry.                                 |
| `SM50_1_Avg` or `SM25_1_Avg`        | Lysimeter load cell 1 average value (mV/V).                     |
| `SM50_2_Avg` or `SM25_1_Avg`        | Lysimeter load cell 2 average value (mV/V).                     |


## Auxillary Columns Found in the Example Dataset

These columns are included in our example dataset and are not used in the processing of the data. They are provided for reference and can be removed if not needed.

| Column Name               | Description                                                       |
|---------------------------|-------------------------------------------------------------------|
| `Tair_Avg`           | Air temperature average (°C).                                    |
| `RH_Avg`             | Relative humidity average (%).                                   |
| `PVWspeed_Avg`       | Wind speed average (m/s).                                        |
| `PVWdir_Avg`         | Wind direction average (degrees).                                |
| `Precip_Tot`         | Total precipitation (mm).                                        |
| `Q7_Rn_Avg`          | Net radiation average (mV).                                      |
| `CR1000X_batt_volt_Min`   | Minimum battery voltage for CR1000X logger (V).                |
| `VOLT116_batt_volt_Min`   | Minimum battery voltage for VOLT116 logger (V).                |
| `CR1000X_Panel_T_Avg`     | Average panel temperature for CR1000X logger (°C).            |
| `VOLT116_Panel_T_1_Avg`   | Average panel temperature for VOLT116 logger 1 (°C).          |
| `Albd_Inc_Avg`            | Incoming albedo average (mV).                                     |
| `Albd_Ref_Avg`            | Reflected albedo average (mV).                                    |
| `Rpar_Avg`                | Photosynthetically active radiation average (mV).                |
| `Lbar_1_Avg`              | Longwave radiation sensor 1 average (mV).                        |
| `HF_1_Avg`                | Heat flux sensor 1 average (mV).                                 |
| `IRTob_tgt_Avg`           | Infrared thermometer object temperature average (°C).            |
| `IRTob_bdy_Avg`           | Infrared thermometer body temperature average (°C).              |
| `IRTnd_tgt_Avg`           | Non-disperse infrared sensor object temperature average (°C).    |
| `IRTnd_bdy_Avg`           | Non-disperse infrared sensor body temperature average (°C).      |
| `SST_20_1_Avg`            | Soil surface temperature at 20 cm depth, sensor 1 average (°C).  |
| `SST_80_1_Avg`            | Soil surface temperature at 80 cm depth, sensor 1 average (°C).  |
| `DST_e_05_Avg`            | Soil temperature at 0.5 m depth, east side average (°C).         |
| `DST_w_1_Avg`             | Soil temperature at 1 m depth, west side average (°C).           |
| `SM250_Drain_Avg`         | Soil moisture sensor at 250 cm depth, drainage average (mV/V).   |
| `Canopy_Temp_Avg`         | Average canopy temperature (°C).                                 |
| `WM_30_Avg`               | Water moisture at 30 cm depth average (kPa).                     |
| `WM_70_Avg`               | Water moisture at 70 cm depth average (kPa).                     |
| `WM_130_Avg`              | Water moisture at 130 cm depth average (kPa).                    |
| `WM_190_Avg`              | Water moisture at 190 cm depth average (kPa).                    |
| `WSWspeed_Avg`            | Wind speed west average (m/s).                                   |

## Notes

- **Custom Columns:** If there are custom columns used in your lysimeter setup, please ensure they follow the correct format and are documented accordingly.
- **Data Format:** The data file should be in CSV format with each row representing a unique timestamp and all measurements taken during that time.
