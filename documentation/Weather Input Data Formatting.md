# Weather Data Input Format for Lysimeter Analysis
Created by A.J. Brown 30 Aug 2024

This document outlines the required and optional columns for the weather data files used in the lysimeter analysis. The required columns are those necessary for the ASCE Penman-Monteith daily evapotranspiration calculation using the [pyfao56 Python package](https://github.com/kthorp/pyfao56/tree/main).

## Required Columns

These columns are required to perform the ASCE Penman-Monteith (ASCE PM) daily calculation for reference evapotranspiration (ETr).

| Column Name         | Description                                                    |
|---------------------|----------------------------------------------------------------|
| `TIMESTAMP`         | The timestamp for each recorded data point.                    |
| `AirTemp_Max`       | Maximum air temperature (°C).                                  |
| `AirTemp_Min`       | Minimum air temperature (°C).                                  |
| `RH_Max`            | Maximum relative humidity (%).                                 |
| `RH_Min`            | Minimum relative humidity (%).                                 |
| `SrMJ_Tot`          | Total solar radiation (MJ/m²).                                 |
| `Vap_Press_Avg`     | Average vapor pressure (kPa).                                  |
| `WS_2m_Avg`         | Average wind speed at 2 meters above ground level (m/s).       |

## Auxillary Columns

These columns are non necessary, but are included in our example dataset, since weather data often come with more parameters than what is needed for the ASCE PM calculation.

| Column Name         | Description                                                    |
|---------------------|----------------------------------------------------------------|
| `RECORD`            | The record number for each entry.                              |
| `AirTemp_TMx`       | Time of maximum air temperature (not required for ASCE PM).    |
| `AirTemp_TMn`       | Time of minimum air temperature (not required for ASCE PM).    |
| `AirTemp_Avg`       | Average air temperature (°C).                                  |
| `RH_TMx`            | Time of maximum relative humidity (not required for ASCE PM).  |
| `RH_TMn`            | Time of minimum relative humidity (not required for ASCE PM).  |
| `RH_Avg`            | Average relative humidity (%).                                 |
| `WS_2m_Max`         | Maximum wind speed at 2 meters above ground level (m/s).       |
| `WindDir_2m_Avg`    | Average wind direction at 2 meters (degrees).                  |
| `WindDir_SD_2m`     | Standard deviation of wind direction at 2 meters (degrees).    |
| `WindRun_2m_Tot`    | Total wind run at 2 meters (km/day).                           |
| `SrW_Avg`           | Average solar radiation (W/m²).                                |
| `SrW_Max`           | Maximum solar radiation (W/m²).                                |
| `WS_3m_Avg`         | Average wind speed at 3 meters above ground level (m/s).       |
| `WS_3m_Max`         | Maximum wind speed at 3 meters above ground level (m/s).       |
| `WindRun_3m_Tot`    | Total wind run at 3 meters (km/day).                           |
| `Rain_Tot`          | Total precipitation (inches).                                  |
| `Program_Signature` | Program signature, typically used for data logging integrity.  |

## Notes

- **Custom Columns:** If there are custom columns used in your weather data setup, please ensure they follow the correct format and are documented accordingly.
- **Data Format:** The weather data file should be in CSV format with each row representing a unique timestamp and all measurements taken during that time.

## References

For more information on the pyfao56 package and the ASCE PM daily calculation, please refer to the following:

- [pyfao56 GitHub Repository](https://github.com/kthorp/pyfao56/tree/main)
- Thorp, K. R., DeJonge, K. C., Pokoski, T., Gulati, D., Kukal, M., Farag, F., Hashem, A., Erismann, G., Baumgartner, T., Holzkaemper, A., 2024. Version 1.3.0 - pyfao56: FAO-56 evapotranspiration in Python. SoftwareX. In review.
