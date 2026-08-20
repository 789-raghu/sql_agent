# LLM Data Retrieval and Table Mapping Reference

## 1. Purpose & Overview
This document defines the official database table mappings, schema references (`epdatalake` and `epdatalake.oracle`), entity join relationships, and data-retrieval paths required for the SQL Agent to locate and query consumer, DTR, meter, AMR, consumption, and billing data accurately.

---

## 2. Quick Entity & Schema Map

| Entity Domain | Primary Table Name | Primary Schema | Key Identifier Columns |
|---|---|---|---|
| DTR to Consumer Link | `consumer_mapping` | `epdatalake` | `DTR_STRUC_CODE`, `CONS_NO` |
| DTR Master Information | `dtr_master` | `epdatalake` | `DTR_STRUCTURE_CODE`, `ID` |
| DTR AMR Meter Mapping | `fdr_dtr_newcharge` | `epdatalake` | `DTR_ID`, `NEW_MTR_MSN` |
| DTR AMR Consumption (BLP) | `t_nw_blp` | `epdatalake` | `msn`, `ts` |
| LT Consumer Master | `lt_consumer_master` | `epdatalake` | `SCNO`, `UKSCNO`, `ID` |
| Smart Meter Installation | `smart_meters_install_m` | `epdatalake` | `UKSCNO`, `MTR_SNO` |
| Smart Meter Consumption (1-Phase) | `t_blp_sp` | `epdatalake` | `msn`, `ts` |
| Smart Meter Consumption (3-Phase) | `t_blp_tp` | `epdatalake` | `msn`, `ts` |
| Non-Smart Meter Consumption | `lt_meter_data` | `epdatalake` | `CONS_NUMBER`, `PRESENT_MTRRDDATE` |
| HT Consumer Master | `ht_consumer_master` | `epdatalake` | `CONS_NUMBER`, `ID`, `MTR_NO` |
| LT Consumer Bills | `lt_billing_data` | `epdatalake` | Requires `DESCRIBE` before querying |
| HT Consumer Bills | `htbpbillprocess_t` | `epdatalake` | Requires `DESCRIBE` before querying |
| Smart Meter Bills | `smart_meters_billdata` | `epdatalake.oracle` | Requires `DESCRIBE` before querying |
| LT Category Master | `lt_category_master` | `epdatalake` | `CAT_CODE`, `NAME` |

---

## 3. Entity Resolution Decision Trees

### 3.1 Meter Data & Consumption Routing Flowchart
```text
                          [ User Question ]
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
[ DTR AMR Query ]        [ Smart Consumer ]       [ Non-Smart Consumer ]
      │                           │                           │
  consumer_mapping            lt_consumer_master          lt_consumer_master
 (DTR_STRUC_CODE)                  │ (UKSCNO)                  │ (ID)
      │                   smart_meters_install_m              │
 fdr_dtr_newcharge                │ (MTR_SNO)              lt_meter_data
 (NEW_MTR_MSN)                    │                           │
      │                  ┌────────┴────────┐             PRESENT_READING &
   t_nw_blp              ▼                 ▼             PRESENT_MTRRDDATE
 (msn, ts, vah_imp)   1-Phase           3-Phase
                         │                 │
                      t_blp_sp          t_blp_tp
                   (msn, ts, vah_imp) (msn, ts, vah_imp)
```

### 3.2 Billing Table Routing Flowchart
```text
                         [ Billing Query ]
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
[ LT Consumer ]            [ HT Consumer ]           [ Smart Consumer ]
     │                           │                           │
lt_billing_data            htbpbillprocess_t       oracle.smart_meters_billdata
(epdatalake.lt_billing_data) (epdatalake.htbpbillprocess_t) (epdatalake.oracle.smart_meters_billdata)
```

---

## 4. Detailed Mapping Specifications

### 4.1 DTR → Consumer Mapping
**Table:** `epdatalake.consumer_mapping`

| Field Requirement | Database Column Name | Data Type | Notes |
|---|---|---|---|
| DTR Structure Code | `DTR_STRUC_CODE` | VARCHAR | Link key to `dtr_master` & `fdr_dtr_newcharge` |
| Consumer Number | `CONS_NO` | VARCHAR | Link key to `lt_consumer_master.SCNO` |

**SQL Query Examples:**
- Count total distinct DTRs:
  ```sql
  SELECT COUNT(DISTINCT DTR_STRUC_CODE) AS TOTAL_DTRS
  FROM epdatalake.consumer_mapping
  WHERE DTR_STRUC_CODE IS NOT NULL;
  ```
- Count consumers under a specific DTR:
  ```sql
  SELECT COUNT(*) AS NUM_CONSUMERS
  FROM epdatalake.consumer_mapping
  WHERE DTR_STRUC_CODE = '<DTR_STRUC_CODE>';
  ```

---

### 4.2 DTR Master
**Table:** `epdatalake.dtr_master`

**Join Condition:** `consumer_mapping.DTR_STRUC_CODE = dtr_master.DTR_STRUCTURE_CODE`

| Requirement | Column | Description |
|---|---|---|
| DTR Identifier | `ID` | Primary Key / DTR ID |
| DTR Structure Code | `DTR_STRUCTURE_CODE` | Structure code for DTR |
| DTR Location Name | `DTR_LOCATION` | Physical location |
| Feeder Code | `FEEDER_CODE` | Parent feeder code |
| Transformer Phase | `PHASE` | Operational phase |
| Transformer Capacity | `CAPACITY` | Rated capacity (kVA) |
| Number of Meters | `NO_OF_METERS` | Total installed meters |
| Meter Numbers | `METER_NUM_1`, `METER_NUM_2`, `METER_NUM_3` | Connected meter serials |
| Geo Latitude | `GLAT` | Latitude coordinate |
| Geo Longitude | `GLONG` | Longitude coordinate |

---

### 4.3 DTR AMR Meter Mapping & BLP Data
**Table:** `epdatalake.fdr_dtr_newcharge` & `epdatalake.t_nw_blp`

**Join Flow:**
```text
epdatalake.consumer_mapping.DTR_STRUC_CODE 
  = epdatalake.fdr_dtr_newcharge.DTR_ID
epdatalake.fdr_dtr_newcharge.NEW_MTR_MSN 
  = epdatalake.t_nw_blp.msn
```

| Table | Required Field | Column |
|---|---|---|
| `fdr_dtr_newcharge` | DTR ID | `DTR_ID` |
| `fdr_dtr_newcharge` | DTR Master ID | `DTR_MASTER_ID` |
| `fdr_dtr_newcharge` | AMR Meter Serial (MSN) | `NEW_MTR_MSN` |
| `fdr_dtr_newcharge` | Meter Make & MF | `NEW_MTR_MAKE`, `NEW_MTR_MF` |
| `fdr_dtr_newcharge` | CT & PT Ratios | `NEW_MTR_CT_RATIO`, `NEW_MTR_PT_RATIO` |
| `fdr_dtr_newcharge` | Installation Date | `NEW_MTR_INSTALLATION_DATETIME` |
| `t_nw_blp` | Meter Serial Number | `msn` |
| `t_nw_blp` | Reading Timestamp | `ts` |
| `t_nw_blp` | Apparent Energy Imported | `vah_imp` |

**SQL Query Example (Latest DTR AMR Reading):**
```sql
SELECT b.msn, b.ts, b.vah_imp
FROM epdatalake.fdr_dtr_newcharge n
JOIN epdatalake.t_nw_blp b ON n.NEW_MTR_MSN = b.msn
WHERE n.DTR_ID = '<DTR_STRUC_CODE>'
ORDER BY b.ts DESC
LIMIT 1;
```

---

### 4.4 LT Consumer Master & Smart Meter Installation
**Tables:** `epdatalake.lt_consumer_master` & `epdatalake.smart_meters_install_m`

**Join Condition:**
```text
epdatalake.consumer_mapping.CONS_NO = epdatalake.lt_consumer_master.SCNO
epdatalake.lt_consumer_master.UKSCNO = epdatalake.smart_meters_install_m.UKSCNO
```

| Table | Requirement | Column |
|---|---|---|
| `lt_consumer_master` | Consumer ID | `ID` |
| `lt_consumer_master` | Consumer Service Number | `SCNO` |
| `lt_consumer_master` | Unique Key Service Number | `UKSCNO` |
| `lt_consumer_master` | Consumer Name | `NAME` |
| `lt_consumer_master` | Category | `CATEGORY` |
| `lt_consumer_master` | Phase | `PHASE` (1 Phase / 3 Phase) |
| `lt_consumer_master` | Contracted & Connected Load | `CONTRACTED_LOAD`, `CONNECTED_LOAD` |
| `lt_consumer_master` | Smart Meter Flag | `SM_MTR` |
| `smart_meters_install_m` | Unique Service Key | `UKSCNO` |
| `smart_meters_install_m` | Smart Meter Serial Number | `MTR_SNO` |
| `smart_meters_install_m` | Meter Type | `MTR_TYPE` |
| `smart_meters_install_m` | Mobile & Coordinates | `CONSUMER_MOBILENO`, `LATITUDE`, `LONGITUDE` |

---

### 4.5 Smart Meter Consumption (1-Phase & 3-Phase)
**Tables:** `epdatalake.t_blp_sp` (1-Phase) & `epdatalake.t_blp_tp` (3-Phase)

**Phase Selection Rule:**
- Check `lt_consumer_master.PHASE`:
  - `1 Phase` or `Single Phase` -> Query `epdatalake.t_blp_sp` ON `t_blp_sp.msn = smart_meters_install_m.MTR_SNO`
  - `3 Phase` or `Three Phase` -> Query `epdatalake.t_blp_tp` ON `t_blp_tp.msn = smart_meters_install_m.MTR_SNO`

**SQL Query Example (Latest Smart Meter Reading):**
```sql
-- For 1-Phase:
SELECT s.MTR_SNO, b.ts, b.vah_imp
FROM epdatalake.lt_consumer_master c
JOIN epdatalake.smart_meters_install_m s ON c.UKSCNO = s.UKSCNO
JOIN epdatalake.t_blp_sp b ON s.MTR_SNO = b.msn
WHERE c.SCNO = '<CONSUMER_NO>'
ORDER BY b.ts DESC
LIMIT 1;

-- For 3-Phase:
SELECT s.MTR_SNO, b.ts, b.vah_imp
FROM epdatalake.lt_consumer_master c
JOIN epdatalake.smart_meters_install_m s ON c.UKSCNO = s.UKSCNO
JOIN epdatalake.t_blp_tp b ON s.MTR_SNO = b.msn
WHERE c.SCNO = '<CONSUMER_NO>'
ORDER BY b.ts DESC
LIMIT 1;
```

---

### 4.6 Non-Smart Metered LT Consumer Readings
**Table:** `epdatalake.lt_meter_data`

**Join Condition:** `lt_consumer_master.ID = lt_meter_data.CONS_NUMBER`

| Requirement | Column | Notes |
|---|---|---|
| Consumer ID | `CONS_NUMBER` | Matches `lt_consumer_master.ID` |
| Present Reading | `PRESENT_READING` | kWh reading |
| Previous Reading | `PREV_READING` | kWh reading |
| Present Reading Date | `PRESENT_MTRRDDATE` | Timestamp of current reading |
| Previous Reading Date | `PREV_MTRRDDATE` | Timestamp of previous reading |

**SQL Query Example:**
```sql
SELECT m.CONS_NUMBER, m.PRESENT_MTRRDDATE, m.PRESENT_READING, m.PREV_MTRRDDATE, m.PREV_READING
FROM epdatalake.lt_consumer_master c
JOIN epdatalake.lt_meter_data m ON c.ID = m.CONS_NUMBER
WHERE c.SCNO = '<CONSUMER_NO>'
ORDER BY m.PRESENT_MTRRDDATE DESC
LIMIT 1;
```

---

### 4.7 HT Consumer Master
**Table:** `epdatalake.ht_consumer_master`

| Requirement | Column | Description |
|---|---|---|
| Consumer ID | `ID` | Primary ID |
| Consumer Number | `CONS_NUMBER` | HT Consumer Service Number |
| Consumer Name | `NAME` | Name of HT entity |
| Supply Details | `TYPE_OF_SUPPLY`, `CATEGORY` | Supply type & classification |
| Load & Demand | `POWER_LOAD`, `CONTRACT_DEMAND`, `CONNECTED_LOAD` | Power limits (kVA/kW) |
| Voltage Ratings | `SUPPLY_VOLTAGE`, `ACTUAL_VOLTAGE` | Voltage levels |
| Transformer & Feeder | `FEEDER_NUM`, `FEEDER_CODE`, `TRANS_STRUC_CODE` | Grid linkage |
| Metering Details | `MTR_NO`, `METER_MAKE`, `METER_TYPE`, `METERING_TYPE` | Meter attributes |
| Coordinates & Smart Flag | `LATITUDE`, `LONGITUDE`, `SMT_MTR` | Location & smart status |

---

### 4.8 Electricity Billing Tables

| Billing Domain | Schema & Table | Key Pre-query Rule |
|---|---|---|
| LT Consumer Billing | `epdatalake.lt_billing_data` | Execute `DESCRIBE TABLE epdatalake.lt_billing_data;` before final SELECT |
| HT Consumer Billing | `epdatalake.htbpbillprocess_t` | Execute `DESCRIBE TABLE epdatalake.htbpbillprocess_t;` before final SELECT |
| Smart Meter Billing | `epdatalake.oracle.smart_meters_billdata` | Execute `DESCRIBE TABLE epdatalake.oracle.smart_meters_billdata;` before final SELECT |

> [!WARNING]
> Do not mix consumption reading tables (`t_blp_sp`, `t_blp_tp`) with billing tables (`oracle.smart_meters_billdata`).

---

### 4.9 Consumer Category Lookup
**Table:** `epdatalake.lt_category_master`

```sql
SELECT ID, NAME, CAT_CODE, SCDESC
FROM epdatalake.lt_category_master
WHERE NAME ILIKE '%domestic%';
```

---

## 5. DTR vs Consumer Attribute Reference Matrix

| Query Intent | Attribute | Correct Source Table & Column |
|---|---|---|
| DTR Capacity | Capacity | `epdatalake.dtr_master.CAPACITY` |
| DTR Phase | Phase | `epdatalake.dtr_master.PHASE` |
| DTR Location | Location Name | `epdatalake.dtr_master.DTR_LOCATION` |
| DTR Latitude / Longitude | Coordinates | `epdatalake.dtr_master.GLAT`, `epdatalake.dtr_master.GLONG` |
| Consumer Contracted Load | Contracted Load | `epdatalake.lt_consumer_master.CONTRACTED_LOAD` |
| Consumer Connected Load | Connected Load | `epdatalake.lt_consumer_master.CONNECTED_LOAD` |
| Consumer Phase | Consumer Phase | `epdatalake.lt_consumer_master.PHASE` |
| Consumer Category | Category | `epdatalake.lt_consumer_master.CATEGORY` |
| HT Contract Demand | Contract Demand | `epdatalake.ht_consumer_master.CONTRACT_DEMAND` |
| HT Supply Voltage | Supply Voltage | `epdatalake.ht_consumer_master.SUPPLY_VOLTAGE` |

---

## 6. Official Key Join Reference Matrix

| Source Table | Source Column | Target Table | Target Column | Join Relationship Type |
|---|---|---|---|---|
| `epdatalake.consumer_mapping` | `CONS_NO` | `epdatalake.lt_consumer_master` | `SCNO` | Many-to-One |
| `epdatalake.consumer_mapping` | `DTR_STRUC_CODE` | `epdatalake.dtr_master` | `DTR_STRUCTURE_CODE` | Many-to-One |
| `epdatalake.consumer_mapping` | `DTR_STRUC_CODE` | `epdatalake.fdr_dtr_newcharge` | `DTR_ID` | Many-to-One |
| `epdatalake.fdr_dtr_newcharge` | `NEW_MTR_MSN` | `epdatalake.t_nw_blp` | `msn` | One-to-Many |
| `epdatalake.lt_consumer_master` | `UKSCNO` | `epdatalake.smart_meters_install_m` | `UKSCNO` | One-to-One |
| `epdatalake.smart_meters_install_m` | `MTR_SNO` | `epdatalake.t_blp_sp` | `msn` | One-to-Many (1-Phase) |
| `epdatalake.smart_meters_install_m` | `MTR_SNO` | `epdatalake.t_blp_tp` | `msn` | One-to-Many (3-Phase) |
| `epdatalake.lt_consumer_master` | `ID` | `epdatalake.lt_meter_data` | `CONS_NUMBER` | One-to-Many |
| `epdatalake.lt_consumer_master` | `CATEGORY` | `epdatalake.lt_category_master` | `NAME` | Many-to-One |

---

## 7. Mandatory LLM Query Generation Rules

1. **Schema Qualification**: Prefix all production data lake table names with `epdatalake.` (or `epdatalake.oracle.`).
2. **Entity Isolation**: Never confuse DTR attributes (e.g. `CAPACITY`, `GLAT`, `GLONG`) with consumer attributes (e.g. `CONTRACTED_LOAD`, `CATEGORY`).
3. **Smart vs Non-Smart Branching**:
   - For Smart Meters: Join `lt_consumer_master` -> `smart_meters_install_m` on `UKSCNO`. Branch by `PHASE` to `t_blp_sp` (1-Phase) or `t_blp_tp` (3-Phase).
   - For Non-Smart LT: Join `lt_consumer_master` -> `lt_meter_data` on `lt_consumer_master.ID = lt_meter_data.CONS_NUMBER`.
   - For DTR AMR: Join `consumer_mapping` -> `fdr_dtr_newcharge` on `DTR_STRUC_CODE = DTR_ID` -> `t_nw_blp` on `NEW_MTR_MSN = msn`.
4. **Explicit Column Lists**: Never use `SELECT *`. Always list required output columns explicitly.
5. **Timestamp Half-Open Intervals**: Use `timestamp >= start AND timestamp < end` for temporal queries to avoid boundary overlap.
6. **Billing Table Inspection**: Before querying `lt_billing_data`, `htbpbillprocess_t`, or `oracle.smart_meters_billdata`, generate a `DESCRIBE TABLE` command if exact column definitions are required.

This document serves as the canonical mapping reference for constructing database queries for the SQL Agent.
