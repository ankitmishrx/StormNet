# IMD Doppler Weather Radar Data Receipt & Intake Checklist

This checklist must be executed by the technical team immediately upon receiving data from the India Meteorological Department (IMD) before any ingestion, model training, or evaluation begins.

---

## 1. Legal & Authorization Verification
- [ ] **Official Source Authorization**: Confirm delivery from authorized IMD email domain (`@imd.gov.in`) or signed physical media with official letterhead.
- [ ] **Documentation & Order Number**: Record IMD data supply invoice, dispatch number, or MoU reference ID.
- [ ] **Licensing & Usage Agreement**: Verify permitted usage tier (Academic/Non-commercial).
- [ ] **Redistribution Terms**: Confirm raw data is isolated to private research storage and excluded from public Git repositories.
- [ ] **Attribution Requirements**: Record exact citation text required by IMD in research publications.

---

## 2. File & Cryptographic Verification
- [ ] **Physical Delivery Location**: Ingest files into designated dropzone: `data/external/imd_radar/`.
- [ ] **Total File Count**: Count files delivered against IMD manifest list.
- [ ] **File Integrity & Format**: Verify files are readable standard formats:
  - ODIM_H5 (`.h5` / `.hdf5`)
  - Cf-Radial / NetCDF (`.nc`)
  - BUFR (`.bufr` / `.bin`)
- [ ] **Cryptographic Checksum**: Compute SHA-256 hash for every file and generate top-level directory hash via `ml.data.manifest.compute_directory_sha256()`.

---

## 3. Metadata & Spatiotemporal Sanity Check
- [ ] **Radar Station Identifier**: Verify station ID matches target radar (e.g. `DWR-DEL-SAF` or `DWR-DEL-PAL`).
- [ ] **Geodetic Coordinates**: Verify antenna latitude, longitude, and elevation AMSL ($28.5847^\circ\text{ N}, 77.2069^\circ\text{ E}, 230\text{ m}$).
- [ ] **Observation Timestamps**: Verify UTC/IST timestamps for every volume scan; check chronological monotonicity and note any gaps $> 20\text{ min}$.
- [ ] **Elevation Sweeps**: Verify elevation angles are present (e.g. $0.5^\circ, 1.0^\circ, 2.0^\circ, \dots, 21.0^\circ$).
- [ ] **Spatial Coverage Range**: Verify maximum unambiguous range ($120\text{--}250\text{ km}$) covers the target Delhi NCR sector.
- [ ] **Native Resolution**: Document gate length (e.g. $250\text{ m}$ / $500\text{ m}$) and azimuthal spacing ($1.0^\circ$).

---

## 4. Meteorological Variable Verification
- [ ] **Reflectivity Factor ($Z$)**:
  - Present: Yes / No
  - Unit: dBZ
  - Range sanity: $-32.0\text{ dBZ} \le Z \le +75.0\text{ dBZ}$
- [ ] **Radial Doppler Velocity ($V_r$)**:
  - Present: Yes / No
  - Unit: m/s
  - Nyquist velocity documented: Yes / No
- [ ] **Spectrum Width ($\sigma_v$)**:
  - Present: Yes / No
  - Unit: m/s
- [ ] **Polarimetric Variables ($Z_{DR}, K_{DP}, \rho_{HV}$)**:
  - Present: Yes / No / Optional
- [ ] **Quality Flags / Clutter Masks**:
  - Present: Yes / No / To be filtered via STORMNET `ReflectivityProcessor`

---

## 5. System Registration & Provenance Gating
- [ ] **Dataset Registration**: Execute `ml.data.register`:
  ```bash
  python -m ml.data.register \
    --path data/external/imd_radar/ \
    --dataset-id imd_delhi_dwr_2024 \
    --provider "IMD" \
    --product "DWR_VOLUMETRIC" \
    --provenance "AUTHORIZED_IMD_DATA" \
    --license "IMD Academic MoU"
  ```
- [ ] **Provenance Tag Verified**: Verify manifest declares `provenance="AUTHORIZED_IMD_DATA"`.
- [ ] **Validation Report Generated**: Check `data/processed/quality_reports/imd_delhi_dwr_2024.json`.
- [ ] **Validation Gate Certification**: Confirm [`ml.data.gating.enforce_provenance_gating()`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/gating.py) unlocks `AUTHORIZED_REAL_WORLD_VALIDATION` mode.
