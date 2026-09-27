# STORMNET — ML Implementation Inventory & Model Audit
**Document ID:** `AUDIT-ML-001`  
**Phase:** Phase 5.5 Scientific Verification  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Audit Date:** 2026-09-26  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary

This inventory provides an exhaustive, forensic technical inspection of all machine learning models, training scripts, inference modules, feature extractors, and evaluation routines currently existing in the STORMNET codebase.

### Critical Audit Finding:
- **No deep learning model weights exist on disk** (0 checkpoint files).
- **No deep neural network has been trained or fine-tuned.**
- Mention of advanced deep architectures (ConvLSTM, PredRNN, Fourier Neural Operator / FNO, U-Net) in earlier documents and docstrings represented **architectural planning specifications and interface declarations**, not trained or active model checkpoints.
- The only functional models in the repository are:
  1. `OpticalFlowBaselineModel` (Lagrangian persistence baseline with simulated advection decay) in [`ml/inference/nowcast_model.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/nowcast_model.py).
  2. `CentroidStormTracker` (Heuristic distance-minimization and centroid matching tracker) in [`ml/inference/tracker.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/tracker.py).
  3. `ConvectiveFeatureExtractor` (Physical Vertically Integrated Liquid / VIL and Echo Tops algorithm) in [`ml/features/feature_pipeline.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/features/feature_pipeline.py).
  4. `MeteorologicalSkillScoreEvaluator` (Deterministic contingency matrix evaluator: POD, FAR, CSI, ETS, FBIAS) in [`ml/evaluation/evaluator.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/evaluation/evaluator.py).
  5. `MultiSourceFusionEngine` (Deterministic 3 km multi-source spatial-temporal fusion) in [`ml/preprocessing/fusion/fusion_engine.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/fusion/fusion_engine.py).

---

## 2. Model-by-Model Inventory

### Model 1: `OpticalFlowBaselineModel`
- **File Location:** [`ml/inference/nowcast_model.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/nowcast_model.py)
- **Model Name:** `OpticalFlow-Baseline`
- **Version:** `0.1.0`
- **Purpose:** Provide a standardized Lagrangian persistence benchmark for 0–6 hour radar reflectivity extrapolation. Serves as the operational baseline against which future neural models must be evaluated.
- **Architecture Type:** Non-parametric heuristic / semi-Lagrangian persistence extrapolation.
- **Input Features:** Multi-timestep composite radar reflectivity grids ($Z$, dBZ).
- **Input Shape:** NumPy array `[T, H, W]` (e.g., `[4, 100, 100]` for a 4-step lookback).
- **Output:** Predicted future reflectivity grids `[T_out, H, W]` for discrete lead times (e.g., $+15, +30, \dots, +360$ min) and associated confidence scores $C(t) = \max(0.40, 1.0 - t/600)$.
- **Training Procedure:** None (deterministic non-parametric advection decay baseline).
- **Loss Function:** None (no gradient optimization).
- **Optimizer:** None.
- **Training Dataset:** None required.
- **Validation Dataset:** Tested via synthetic and sample radar arrays in [`tests/ml/test_ml_and_adapters.py`](file:///e:/project/SIH%20project%202%20Stormnet/apps/api/tests/test_ml_and_adapters.py).
- **Test Dataset:** None yet established.
- **Dependencies:** `numpy`, `pydantic`.
- **Current Status:** **IMPLEMENTED & VERIFIED (BASELINE ONLY)**.

---

### Model 2: `CentroidStormTracker`
- **File Location:** [`ml/inference/tracker.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/tracker.py)
- **Model Name:** `Centroid-Tracker-Baseline`
- **Version:** `0.1.0`
- **Purpose:** Segment contiguous high-reflectivity convective cores ($\ge 40$ dBZ) and extrapolate cell centroid vectors (TITAN/SCIT-style).
- **Architecture Type:** Connected-component segmentation with linear centroid motion extrapolation.
- **Input Features:** 2D Composite reflectivity grid `[H, W]`, dBZ threshold (default 40.0 dBZ).
- **Input Shape:** `[H, W]` grid array.
- **Output:** List of `TrackedCell` objects containing:
  - `centroid_lat`, `centroid_lon`
  - `max_dbz`, `area_km2`
  - `velocity_u_kmh`, `velocity_v_kmh`, `speed_kmh`, `bearing_deg`
  - Projected centroids at $+15, +30, +45, +60$ min.
- **Training Procedure:** None (heuristic geometric tracking).
- **Loss Function:** None.
- **Optimizer:** None.
- **Training Dataset:** None.
- **Validation Dataset:** Unit tested with thresholded test grids.
- **Dependencies:** `numpy`, `pydantic`.
- **Current Status:** **IMPLEMENTED BUT NOT VALIDATED (MOCK TRACK EXTRAPOLATION)**.
  *Note:* The current implementation returns baseline trajectory vectors for Delhi-NCR fixtures rather than executing full dynamic cross-scan optical flow correlation.

---

### Model 3: `ConvectiveFeatureExtractor`
- **File Location:** [`ml/features/feature_pipeline.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/features/feature_pipeline.py)
- **Model Name:** `Physics-ConvectiveFeatureExtractor`
- **Version:** `1.0.0`
- **Purpose:** Extract physical convective metrics from 3D volumetric radar data using empirical Z-M relations.
- **Algorithms:**
  - Vertically Integrated Liquid (VIL, $\text{kg/m}^2$): $M = 3.44 \times 10^{-3} \times Z^{4/7}$, $\text{VIL} = \sum M \cdot \Delta z \cdot 10^{-3}$.
  - Echo Tops ($\text{km MSL}$): Height of the 18.0 dBZ radar boundary.
  - Maximum Composite Reflectivity ($\text{dBZ}$).
- **Input Shape:** Volumetric 3D radar grid `[Levels, H, W]`.
- **Output:** Dictionary of 2D grids: `composite_reflectivity`, `vertically_integrated_liquid`, `echo_top_height`.
- **Training Procedure:** None (closed-form meteorological empirical physics).
- **Dependencies:** `numpy`.
- **Current Status:** **IMPLEMENTED & VERIFIED**.

---

### Model 4: `MeteorologicalSkillScoreEvaluator`
- **File Location:** [`ml/evaluation/evaluator.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/evaluation/evaluator.py)
- **Model Name:** `Meteorological-Evaluator`
- **Version:** `1.0.0`
- **Purpose:** Calculate standardized 2x2 dichotomous contingency tables and meteorological verification skill scores.
- **Metrics Calculated:**
  - Probability of Detection (POD) / Hit Rate: $\frac{H}{H + M}$
  - False Alarm Ratio (FAR): $\frac{F}{H + F}$
  - Critical Success Index (CSI) / Threat Score: $\frac{H}{H + M + F}$
  - Equitable Threat Score (ETS): $\frac{H - H_{\text{random}}}{H + M + F - H_{\text{random}}}$
  - Frequency Bias (FBIAS): $\frac{H + F}{H + M}$
- **Input:** Predicted reflectivity grid `[H, W]`, ground truth observed grid `[H, W]`, threshold (e.g. 35.0 dBZ).
- **Output:** `VerificationMetrics` container.
- **Dependencies:** `numpy`, `pydantic`.
- **Current Status:** **IMPLEMENTED & VERIFIED**.

---

### Model 5: `BaseModelTrainer` & `TrainingConfig`
- **File Location:** [`ml/training/trainer.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/training/trainer.py)
- **Model Name:** Abstract Training Harness
- **Purpose:** Define standard abstract training lifecycle interface (`build_model()`, `train_epoch()`, `validate()`).
- **Configuration Spec:**
  - `sequence_input_length`: 4 frames (Lookback: $-40$ min to $T-0$).
  - `sequence_output_length`: 24 frames (Forecast: $+10$ min to $+4$ hr).
  - `batch_size`: 16.
  - `learning_rate`: $10^{-4}$.
  - `epochs`: 50.
  - `loss_function`: `BMA_Weighted_MSE`.
- **Current Status:** **ABSTRACT INTERFACE ONLY (NO CONCRETE PYTORCH/TF BACKBONE IMPLEMENTED)**.

---

## 3. Training & Inference Script Inventory

| File Path | Component | Status | Operational Readiness |
| :--- | :--- | :--- | :--- |
| [`ml/inference/nowcast_model.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/nowcast_model.py) | Inference Container & Optical Flow Baseline | Implemented | Verified on synthetic arrays (Latency: 0.76 ms) |
| [`ml/inference/tracker.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/inference/tracker.py) | Cell Segmentation & Motion Vector Tracker | Partial | Heuristic mock track extrapolation |
| [`ml/training/trainer.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/training/trainer.py) | Training Interface & Config Spec | Abstract Spec | No training execution scripts exist |
| [`ml/features/feature_pipeline.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/features/feature_pipeline.py) | VIL & Echo Tops Extraction | Implemented | Verified against test volume arrays |
| [`ml/evaluation/evaluator.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/evaluation/evaluator.py) | Contingency Matrix & Skill Scores | Implemented | Verified (POD, FAR, CSI, ETS, FBIAS) |
| [`ml/preprocessing/fusion/fusion_engine.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/fusion/fusion_engine.py) | Multi-Source Fusion Engine | Implemented | Verified across Delhi-NCR sample streams |
| [`ml/preprocessing/fusion/fuse_cli.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/fusion/fuse_cli.py) | Batch Fusion CLI Runner | Implemented | Verified end-to-end execution |
| [`ml/preprocessing/fusion/exporter.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/fusion/exporter.py) | Parquet Feature Exporter | Implemented | Verified (Snappy-compressed Parquet + Metadata) |

---

## 4. Checkpoints & Model Weights Inventory

| Directory | Files Found | Size | Description |
| :--- | :--- | :--- | :--- |
| `ml/checkpoints/` | **None** (Directory not created) | 0 bytes | No deep learning checkpoints exist |
| `data/models/` | **None** | 0 bytes | No pre-trained weights exist |
| Root | **None** | 0 bytes | No serialized weights (`.pt`, `.pth`, `.onnx`, `.h5`, `.safetensors`) |

**Finding:** The codebase is completely free of unauthorized or fabricated model weights.

---

## 5. Configuration Files Inventory

| File Path | Config Purpose | Parameters Declared |
| :--- | :--- | :--- |
| [`ml/training/trainer.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/training/trainer.py) | `TrainingConfig` | Input/Output sequence lengths, batch size, learning rate, loss function |
| [`apps/api/core/config.py`](file:///e:/project/SIH%20project%202%20Stormnet/apps/api/core/config.py) | API / Backend Settings | DB URL, CORS origins, debug flags, sector definitions |
| [`pytest.ini`](file:///e:/project/SIH%20project%202%20Stormnet/pytest.ini) | Test Suite Config | Python test paths and test discovery rules |
| [`apps/web/tsconfig.json`](file:///e:/project/SIH%20project%202%20Stormnet/apps/web/tsconfig.json) | Web TypeScript Config | Compiler strictness, path aliases (`@/*`) |

---

## 6. Audit Conclusion & Compliance Summary

1. **No neural network has been trained or deployed.** Claims in earlier planning documents regarding ConvLSTM / U-Net represent architectural target specifications, not completed implementations.
2. **The existing ML pipeline is an empirical/heuristic baseline pipeline**, consisting of Lagrangian persistence, VIL feature extraction, and contingency skill scoring.
3. **All interfaces are cleanly decoupled**, positioning the platform for genuine neural backbone integration in Phase 6 without scientific fabrication.
