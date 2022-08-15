# Description
Home Assistant custom component for Satel Integra/ETHM-1 ("plus" version is not required).
Based on Python library taken from https://github.com/c-soft/satel_integra.

# Supports
- Integra 64
- ETHM-1 v 1.07 (INT-RS v2.xx)

# TODO
- number of outputs and zones should be related to INTEGRA type (currently: hardcoded)
- add troubles, and other valuable information
- handle arm/disarm, select partition to arm, disable exit time if needed
- add unit tests
- any config to detect night/day arm mode? (currently hardcoded: night mode if some partitions are not armed)
- detect INT-RS v1/v2? Any other options? (currently v2 hardcoded)
- detect Integra version and automatically use correct number of zones, outputs and partitions
- translations
- progress bar/notification while initializing component

# main.py
Main program to be used for testing satel library and satel interaction/API.
