# STORMNET — AI-Powered Convective Nowcasting Platform

[![Problem Statement](https://img.shields.io/badge/SIH%202026-SIH26084-blue.svg)](https://sih.gov.in)
[![Domain](https://img.shields.io/badge/Domain-Disaster%20Management%20%2F%20Meteorology-orange.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)]()

> **Problem Statement SIH26084:** Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr Lead Time)  
> **Target Institutions:** India Meteorological Department (IMD), Ministry of Earth Sciences (MoES), National Disaster Management Authority (NDMA), State EOCs.

---

## 1. System Overview

**STORMNET** is a high-resolution, research prototype convective nowcasting platform engineered to predict high-impact severe weather phenomena—localized cloudbursts (>100 mm/hr), destructive hail cores, severe convective squalls, and lightning swarms—at 0–6 hour lead times.

By assimilating multi-source observations—Doppler Weather Radar (DWR reflectivity $Z$, radial velocity $V$, spectrum width $W$), INSAT-3D/3DR geostationary satellite imagery, Lightning Location Networks (LLN), and Automatic Weather Stations (AWS)—STORMNET couples physics-informed deep learning models with automated storm cell segmentation and kinematic tracking algorithms.

---

## 2. Repository Layout

```
stormnet/
├── apps/
│   ├── web/                    # Next.js 15, React 19, TypeScript, Tailwind CSS, MapLibre GL
│   └── api/                    # FastAPI, Pydantic v2, SQLAlchemy, GeoAlchemy2, PostGIS
├── ml/
│   ├── preprocessing/          # Radar volume and satellite ingestion pipelines
│   ├── features/               # Convective parameter extraction (VIL, Echo Top, CAPE proxy)
│   ├── training/               # Spatio-temporal model training interfaces (ConvLSTM, U-Net)
│   ├── inference/              # High-throughput nowcasting prediction engine
│   └── evaluation/             # CSI, POD, FAR, ETS, and spatial FSS validation metrics
├── packages/
│   ├── ui/                     # Design tokens and shared matte cream component primitives
│   ├── shared/                 # Core domain models, schemas, and typed data contracts
│   └── geo/                    # Geospatial transformations, cell buffering, and coordinate conversions
├── data/
│   ├── raw/                    # Raw ingest data directory (gitignored)
│   ├── processed/              # Normalized radar grids and tensors (gitignored)
│   └── samples/                # Sample formats for local validation
├── docs/
│   ├── design/                 # UI architectural specs, design tokens, and component map
│   ├── architecture/           # Full system architecture and dataflow documentation
│   ├── research/               # Meteorological problem formulations and literature notes
│   └── model-cards/            # Scientific ML model documentation
├── infra/
│   └── docker/                 # Production & local Docker Compose definitions
├── .env.example                # Canonical environment variable template
└── README.md
```

---

## 3. Technology Stack

- **Frontend:** Next.js (App Router), React, TypeScript (strict), Tailwind CSS, Lucide Icons, MapLibre GL
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, GeoAlchemy2, Alembic
- **Database & Spatial:** PostgreSQL 16, PostGIS 3.4
- **Cache & Message Broker:** Redis 7
- **Machine Learning & Scientific:** PyTorch, NumPy, Pandas, Xarray, Scikit-learn
- **Geospatial Processing:** GeoPandas, Shapely, Rasterio, PyProj
- **Containerization:** Docker, Docker Compose

---

## 4. Quick Start (Development)

### Prerequisites
- Node.js `≥ 20.x` & `npm` / `pnpm`
- Python `≥ 3.11`
- Docker & Docker Compose

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```

### 2. Launch Local Database & Redis (Docker)
```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres redis
```

### 3. Backend Setup
```bash
cd apps/api
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Verify backend health: `http://localhost:8000/health`

### 4. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
Open web application: `http://localhost:3000`

---

## 5. Design Philosophy: Matte Cream & Government Weather Intelligence

The platform visual design follows the approved specifications in `docs/design/`:
- **Palette:** Soft matte cream background (`#FAF8F5`) preventing eye fatigue during 24/7 forecaster shifts.
- **Hierarchy:** 3-pane operational layout featuring GIS Convective Map, 0–6h Forecast Timeline, and Right-side Storm Intelligence Panel.
- **Standards:** Strict alignment with India Meteorological Department (IMD) 4-stage color-coded warnings (Green, Yellow, Orange, Red).

---

## 6. Project Roadmap & SIH Milestone Phases

- [x] **Phase 1: Design Analysis & Architectural Blueprint**
- [x] **Phase 2: Engineering Foundation (Monorepo, Database Schemas, API & ML Abstractions)**
- [ ] **Phase 3: Interactive GIS Map & Spatial Data Layer**
- [ ] **Phase 4: Convective Cell Tracking & Physical Diagnostics (VIL, Echo Top)**
- [ ] **Phase 5: Spatio-temporal Deep Learning Model Integration (0–6h Nowcast)**
- [ ] **Phase 6: Multi-Sensor Data Ingestion & CAP Warning Dispatch**
