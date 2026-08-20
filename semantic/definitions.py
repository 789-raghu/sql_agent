BUSINESS_DEFINITIONS = """
- Schema Qualification: Production data lake tables MUST be prefixed with 'epdatalake.' (or 'epdatalake.oracle.').
- DTR vs Consumer Attributes:
  * DTR attributes (Capacity, Phase, Location, Coordinates) -> epdatalake.dtr_master (CAPACITY, PHASE, DTR_LOCATION, GLAT, GLONG).
  * Consumer attributes (Contracted Load, Connected Load, Phase, Category) -> epdatalake.lt_consumer_master (CONTRACTED_LOAD, CONNECTED_LOAD, PHASE, CATEGORY) or epdatalake.ht_consumer_master (CONTRACT_DEMAND, CONNECTED_LOAD, POWER_LOAD, SUPPLY_VOLTAGE).
- Smart Meter Reading Routing:
  * lt_consumer_master (SCNO) -> JOIN smart_meters_install_m ON UKSCNO -> Branch on lt_consumer_master.PHASE:
    - 1-Phase -> JOIN epdatalake.t_blp_sp ON smart_meters_install_m.MTR_SNO = t_blp_sp.msn.
    - 3-Phase -> JOIN epdatalake.t_blp_tp ON smart_meters_install_m.MTR_SNO = t_blp_tp.msn.
- Non-Smart LT Consumer Reading:
  * lt_consumer_master (SCNO) -> JOIN epdatalake.lt_meter_data ON lt_consumer_master.ID = lt_meter_data.CONS_NUMBER (PRESENT_READING, PREV_READING, PRESENT_MTRRDDATE).
- DTR AMR Reading Routing:
  * consumer_mapping (DTR_STRUC_CODE) -> JOIN epdatalake.fdr_dtr_newcharge ON DTR_STRUC_CODE = DTR_ID -> JOIN epdatalake.t_nw_blp ON NEW_MTR_MSN = msn.
- Date Filtering Standard: Always use half-open intervals 'timestamp >= start AND timestamp < end' to avoid boundary duplicates.
- Column Listing: Never use 'SELECT *'. Explicitly list required columns only.
"""
