# Sensor Coefficients File for Lysimeter Analysis
Created by A.J. Brown, 30 August 2024

This document outlines the format for the sensor coefficients file, which provides calibration coefficients for any relevant sensors associated with the lysimeter data. This input is optional and is only necessary if there are working environmental sensors placed appropriately with the weighing lysimeter and included in the same `.dat` file.

## Purpose of the Sensor Coefficients File

The sensor coefficients file allows users to apply specific calibration equations to environmental sensor data recorded alongside lysimeter measurements. These coefficients adjust the raw sensor readings to provide more accurate measurements in the desired units. This file is particularly useful when environmental sensors such as radiation sensors, heat flux sensors, or light bars are integrated with the lysimeter system.

### When to Use This File

- **Optional Input:** This file is optional and should only be used if you have environmental sensors that require calibration coupled with the lysimeter `.dat` file. 

## File Format

The sensor coefficients file is a CSV file containing the following columns:

### Required Columns

| Column Name            | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `Variable`             | The name of the environmental variable being measured (e.g., Albd_Inc).     |
| `Sensor`               | The specific sensor used for measurement (e.g., CM14 Incident).             |
| `Coefficient`          | The calibration coefficient to be applied to the sensor data.               |
| `Col_Name`             | The corresponding column name in the lysimeter `.dat` file where the raw data is stored. |
| `Calibration_Equation` | The equation used to calibrate the sensor data, incorporating the coefficient. Purely for notes, but not actually used by the python code. |

### Example File Content

```plaintext
Variable,Sensor,Coefficient,Col_Name,Calibration_Equation
Albd_Inc,CM14 Incident,197.62845,Albd_Inc_Avg,Albd_Inc_Avg * 197.62845
Albd_Ref,CM14 Reflected,196.07843,Albd_Ref_Avg,Albd_Ref_Avg * 196.07843
Rpar,LI-190 Reflected PAR,236.13,Rpar_Avg,Rpar_Avg * 236.13
Lbar_1,LI-191 Light Bar 1,335.15,Lbar_1_Avg,Lbar_1_Avg * 335.15
Lbar_2,LI-191 Light Bar 2,381.48,Lbar_2_Avg,Lbar_2_Avg * 381.48
Q7_Rn_Plus,Q7 Net Radiation (+ Wind),10.85,Q7_Rn_Avg,"=IF(PVWspeed_Avg>0, 10.85000*(1+(0.066*0.2*PVWspeed_Avg)))*PVWspeed_Avg, 13.81000*((0.00174*PVWspeed_Avg)+0.99755)*Q7_Rn_Avg"
Q7_Rn_Minus,Q7 Net Radiation (- Wind),13.81,Q7_Rn_Avg,"=IF(PVWspeed_Avg>0, 10.85000*(1+(0.066*0.2*PVWspeed_Avg)))*PVWspeed_Avg, 13.81000*((0.00174*PVWspeed_Avg)+0.99755)*Q7_Rn_Avg"
HF_1,Heat Flux 1,46.65,HF_1_Avg,HF_1_Avg * 46.65
HF_2,Heat Flux 2,52.29,HF_2_Avg,HF_2_Avg * 52.29
HF_3,Heat Flux 3,37.86,HF_3_Avg,HF_3_Avg * 37.86
HF_4,Heat Flux 4,47.39,HF_4_Avg,HF_4_Avg * 47.39
