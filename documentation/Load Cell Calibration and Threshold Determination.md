# Load Cell Calibration Equation

**Created by:** A.J. Brown  
**Date:** 28 August 2024  
**Contact:** Ansley.Brown@colostate.edu  

---

## Generic Form of the Load Cell Calibration Equation

$$ \alpha \ \left(\frac{\text{kg}}{\text{mV}/V}\right) \left(\frac{1\,\text{m}^3}{1000\ \text{kg}}\right) \left(\frac{1}{\beta\ \text{m}^2}\right) \left(\frac{1000\,\text{mm}}{1.0\,\text{m}}\right) = 151.09 \ \left(\frac{\text{mm}}{\text{mV}/V}\right) $$

**Where:**
- **α** is the load cell conversion coefficient (i.e., mV/V to kg), which is the slope of the linear calibration equation relating mV/V to kg of weight on the lysimeter from a standard weight
- **β** is the effective surface area of the lysimeter
- Assumes water density = **1000 kg/m³**

---

## CSU AVRC Lysimeters (Provided by Lane Simmons, 18 August 2024)

### Calibration Results (2021)

- **Large Lysimeter (LL)**  
  - Slope (α): 699.5922 kg/mV/V  
  - Effective Area (β): 9.181 m²  
  - Conversion Factor: **76.20 mm/mV/V**

- **Small Lysimeter (SL)**  
  - Slope (α): 368.5381 kg/mV/V  
  - Effective Area (β): 2.341 m²  
  - Conversion Factor: **157.43 mm/mV/V**

---

## Summary Table

| Lysimeter | Slope (lbs/mV/V) | Slope α (kg/mV/V) | Surface Area β (m²) | Conversion Factor (mm/mV/V) |
|-----------|------------------|-------------------|----------------------|------------------------------|
| Large     | 1542.337         | 699.5922          | 9.181                | 76.20                        |
| Small     | 812.488          | 368.5381          | 2.341                | 157.43                       |


## Determining Threshold for Non-Standard Events (NSEs)
The threshold for detecting non-standard events (NSEs) is set to **0.0034 mV/V** for the LL and 0.0016 mV/V for the SL. This value is equivalent to 0.01 inches, or the minimum detection limit of a tipping bucket rain guage, a device often used to validate precipitation measurements derived from the lysimeter itself.The threshold is used to filter out noise in the load cell readings. It is essential for ensuring that only significant changes in weight are considered as potential NSEs, such as rainfall, irrigation, or other disturbances.

| Measurement Description         | Large Lysimeter | Small Lysimeter | Units     |
|---------------------------------|-----------------|------------------|-----------|
| Threshold for auto-detection                  | 0.0034          | 0.001613         | mV/V      |
| Conversion Factor               | 76.2            | 157.43           | mm/mV/V   |
| Minimum Detectable Change       | 0.25908         | 0.254            | mm        |
| Minimum Detectable Change       | 0.0102          | 0.01             | inches    |



