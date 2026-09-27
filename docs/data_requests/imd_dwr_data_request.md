# Formal Academic & Research Data Request to IMD

**To:**  
The Director General of Meteorology  
India Meteorological Department (IMD)  
Mausam Bhawan, Lodhi Road  
New Delhi – 110003, India  

**Date:** [DATE]  
**Through:** Head of Department / Head of Institution, [COLLEGE / INSTITUTION]  

---

### Subject: Request for Historical Doppler Weather Radar Data for Academic / Research Prototype on Convective-Scale Nowcasting (Smart India Hackathon 2024 — Problem Statement SIH26084)

Respected Sir/Madam,

We are writing to formally request historical Doppler Weather Radar (DWR) data for academic research, algorithmic development, and scientific evaluation within the **StormNet** project.

### 1. Project Background & Context
Our research team, **[TEAM NAME]** from **[COLLEGE / INSTITUTION]**, is actively participating in the **Smart India Hackathon (SIH)** addressing **Problem Statement 26084**: *"AI-Powered Convective-Scale Nowcasting (0–6 Hours) for Thunderstorms, Lightning, Hail, and Cloudbursts"*.

The primary objective of StormNet is to build a modern, high-resolution AI/ML nowcasting framework capable of assimilating multi-source observations—specifically Doppler Weather Radar reflectivity, geostationary satellite telemetry, lightning counts, and surface Automatic Weather Station (AWS) records—to generate calibrated probabilistic hazard forecasts for vulnerable urban and semi-urban populations.

### 2. Purpose of Data Request
The requested data will be utilized **strictly for non-commercial academic research, software prototype testing, and retrospective scientific evaluation**. Specifically, the data will be used to:
1. Evaluate spatiotemporal deep-learning architectures (e.g. U-Net and spatiotemporal neural operators) against standard meteorological baselines (Lagrangian persistence, optical flow).
2. Validate automated storm-cell tracking, convective core identification, and rapid intensification algorithms during high-impact monsoon and pre-monsoon episodes in the National Capital Region (NCR).
3. Benchmark quantitative precipitation estimation (QPE) and hail probability indices against ground observations.

### 3. Geographic & Station Focus
- **Geographic Area**: Delhi National Capital Region (NCR) and surrounding catchment areas ($28.0^\circ\text{--}29.2^\circ\text{ N}, 76.5^\circ\text{--}77.8^\circ\text{ E}$).
- **Target Radar Station**: **Delhi DWR (Safdarjung Airport / Palam Airport)**, or any nearby representative radar installation operated by IMD covering the NCR.

### 4. Desired Historical Temporal Coverage
Rather than requesting extensive multi-year archives, we request a targeted, minimum viable subset of historical data corresponding to **selected severe convective weather events** (thunderstorms, squalls, severe hailstorms, or extreme localized rainfall) during recent convective seasons:
- **Pre-Monsoon & Monsoon 2023**: Selected severe thunderstorm/squall episodes (e.g., May–August 2023).
- **Pre-Monsoon & Monsoon 2024**: Selected severe convective/cloudburst episodes (e.g., May–July 2024, including the June 28, 2024 extreme event).

*Note*: If event-specific extraction is inconvenient, we respectfully request guidance on an alternative standard historical archival block that IMD routinely provides to academic researchers.

### 5. Requested Radar Variables & Products
1. **Primary Product**:
   - **Reflectivity ($Z$ / dBZ)**: Plan Position Indicator (PPI) elevation sweeps, Constant Altitude PPI (CAPPI), or Column Maximum (Max-Z) composite reflectivity.
2. **Secondary Products (if available)**:
   - **Radial Doppler Velocity ($V_r$ / m/s)**: Hydrometeor velocity component for gust front and microburst shear detection.
   - **Spectrum Width ($\sigma_v$ / m/s)**: Turbulence and shear characterization.
   - **Quantitative Precipitation Estimation (QPE / PAC)**: Derived rainfall accumulation products, if routinely generated.
   - **Dual-Polarimetric Parameters ($Z_{DR}, K_{DP}$)**: If polarimetric variables are archived for the selected events.

### 6. Desired Formats & Associated Metadata
We do not demand a specific proprietary format. StormNet includes a flexible preprocessing bridge and can consume any standard format supplied by IMD:
- **Formats Accepted**: NetCDF4 / Cf-Radial, HDF5 (ODIM_H5 standard), BUFR, or standard Cartesian gridded matrices.
- **Required Accompanying Metadata**:
  - Exact radar geodetic location (antenna latitude, longitude, and elevation AMSL).
  - Accurate UTC/IST timestamps for each volume scan.
  - Elevation angles and sweep numbers.
  - Georeferencing, projection definition, and spatial resolution (bin length / azimuth interval).
  - Calibration constants and quality flags, where available.

### 7. Enquiries Regarding IMD Procedure & Data Policy
To ensure complete compliance with the Ministry of Earth Sciences (MoES) National Data Sharing and Accessibility Policy (NDSAP) and IMD regulations, we respectfully request your guidance on the following:
1. **Application Procedure**: Does IMD require submission through a specific online portal (such as the IMD Data Supply Portal), or is a formal hard-copy/email application sufficient?
2. **Institutional Endorsement**: We are prepared to submit a formal letter endorsed by our Head of Institution / Faculty Mentor on official college letterhead.
3. **Data Sharing Agreement / MoU**: We are prepared to execute a standard Non-Disclosure Agreement (NDA) or Academic MoU restricting data usage solely to the declared academic project.
4. **Fees & Tariffs**: Please advise whether academic fee concessions or waivers apply to students participating in Government of India initiatives such as the Smart India Hackathon.
5. **Attribution & Publication Conditions**: We undertake to provide formal citation and acknowledgment of IMD in all reports, papers, and hackathon presentations resulting from this research.
6. **Redistribution Restrictions**: We confirm that raw radar data will remain strictly on secure, access-controlled institutional research environments and will not be redistributed publicly or committed to open source repositories.

We look forward to your positive consideration and valuable guidance.

Thanking you,

Yours sincerely,

**[STUDENT NAME]**  
Lead Student Researcher / Team Leader, [TEAM NAME]  
Department of [DEPARTMENT]  
[COLLEGE / INSTITUTION]  
Email: [EMAIL] | Phone: [PHONE]  

**Endorsed By:**  

**[FACULTY MENTOR]**  
Faculty Mentor / Guide  
Department of [DEPARTMENT]  
[COLLEGE / INSTITUTION]  
Email: [MENTOR EMAIL] | Phone: [MENTOR PHONE]  

**[HEAD OF INSTITUTION / PRINCIPAL / DIRECTOR]**  
[DESIGNATION]  
[COLLEGE / INSTITUTION]  
Official Seal / Stamp  
