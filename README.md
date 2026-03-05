# Description
Home Assistant custom component for Satel Integra/ETHM-1 ("plus" version is not required).
Based on Python library taken from https://github.com/c-soft/satel_integra.

# Supports
- Home Assistant 2022.8.4
- Integra 64
- ETHM-1 v 1.07 (INT-RS v2.xx)

# HA Objects
This integration creates one device (for Satel INTEGRA) and all enabled zones (inputs), outputs and partitions as sensors.

# HA Events
This integration fires the following events:
- satel_ethm_zone_alarm_triggered: when the zone receives ALARM state
- satel_ethm_zone_alarm_cleared: when the zone clears ALARM state
Events data is:
```
zone_name: <name of the zone>
```

# main.py
Main program to be used for testing Satel library and Satel interaction/API.

