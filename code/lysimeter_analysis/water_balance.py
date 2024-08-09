# lysimeter_analysis/non_standard_events.py
'''
Script that converts load cell data (mV/V) to mass (kg) for each time step, and
calculates the actual transpiration rate (mm/t) for each time step.

The logical flow will be as follows:
1. Load the data after being processed by the DatFileMerger and 
NonStandardEvents classes.
2. Convert the load cell data to mass using the calibration equation for each
for each lysimeter type (i.e., SL or LL).
3. Calculate the actual transpiration rate (ETa) for each time step using the mass data
and the lysimeter area.
4. Identify ETa rates that are immediately prior to and after each NSE, then
linearly interpolate the ETa rate for the NSE and use that in place of the load
cell -derived ETa rate.
5. Use the ETa rates to calculate the water balance for the selected lysimeter.
'''