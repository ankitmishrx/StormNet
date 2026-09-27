"""STORMNET Scientific Validation Experiment Safety Gate.

Guarantees scientific defensibility by strictly gating machine learning training and evaluation.
Prevents models trained on synthetic or developmental sample data from being claimed as scientifically validated.

Enforces:
- SYNTHETIC / SAMPLE: Development/testing and UI demonstration only (CANNOT be marked as real-world validation).
- PUBLIC_REAL_DATA: Allows reproducible historical experiments labeled strictly as 'PUBLIC_DATASET_VALIDATION'.
- AUTHORIZED_IMD_DATA / AUTHORIZED_MOSDAC_DATA: Allows corresponding authorized real-world validation.
"""

from enum import Enum
import logging
from typing import Optional, Tuple

from ml.data.manifest import DatasetProvenance

logger = logging.getLogger("stormnet.gating")


class ExperimentMode(str, Enum):
    """Operational mode of an experiment execution."""
    DEVELOPMENT_TEST = "DEVELOPMENT_TEST"
    SCIENTIFIC_VALIDATION = "SCIENTIFIC_VALIDATION"
    DEMO = "DEMO"


class ValidationTier(str, Enum):
    """Certified validation tier output from safety gate."""
    UNVALIDATED_DEVELOPMENT = "UNVALIDATED_DEVELOPMENT"
    PUBLIC_DATASET_VALIDATION = "PUBLIC_DATASET_VALIDATION"
    AUTHORIZED_REAL_WORLD_VALIDATION = "AUTHORIZED_REAL_WORLD_VALIDATION"


class ScientificIntegrityError(ValueError):
    """Raised when an experiment violates scientific data provenance constraints."""
    pass


def enforce_experiment_safety_gate(
    dataset_provenance: str,
    experiment_mode: str = ExperimentMode.SCIENTIFIC_VALIDATION.value,
) -> str:
    """Enforces scientific validation gating on experiment datasets.

    Args:
        dataset_provenance: Provenance tag (e.g. PUBLIC_REAL_DATA, AUTHORIZED_IMD_DATA, SYNTHETIC_DATA, SAMPLE_DATA).
        experiment_mode: Target mode (DEVELOPMENT_TEST, SCIENTIFIC_VALIDATION, or DEMO).

    Returns:
        ValidationTier string specifying the permissible validation claim.

    Raises:
        ScientificIntegrityError: If synthetic or sample data is used for scientific validation.
    """
    prov_str = str(dataset_provenance).upper()
    mode_str = str(experiment_mode).upper()

    if mode_str == ExperimentMode.SCIENTIFIC_VALIDATION.value:
        if prov_str in [
            DatasetProvenance.SYNTHETIC_DATA.value,
            DatasetProvenance.SAMPLE_DATA.value,
            "SYNTHETIC",
            "SAMPLE",
        ]:
            raise ScientificIntegrityError(
                f"\n======================================================================\n"
                f"SCIENTIFIC INTEGRITY GATE REJECTION\n"
                f"======================================================================\n"
                f"Target Mode        : {mode_str}\n"
                f"Dataset Provenance : {prov_str}\n"
                f"Violation          : Experiments intended for scientific validation cannot\n"
                f"                     consume synthetic or sample datasets.\n"
                f"Required Data Tier : PUBLIC_REAL_DATA, AUTHORIZED_IMD_DATA, or AUTHORIZED_MOSDAC_DATA\n"
                f"Resolution         : Ingest public observational archives (e.g. SEVIR, NEXRAD, GPM),\n"
                f"                     or set '--mode DEVELOPMENT_TEST' for engineering testing.\n"
                f"======================================================================"
            )

        if prov_str == DatasetProvenance.PUBLIC_REAL_DATA.value:
            print(
                f"\n>>> [PROVENANCE NOTICE] Certified for PUBLIC_DATASET_VALIDATION.\n"
                f">>> Results must be published as public-dataset experiments (NOT operational IMD validation).\n"
            )
            return True

        if prov_str in [
            DatasetProvenance.AUTHORIZED_IMD_DATA.value,
            DatasetProvenance.AUTHORIZED_MOSDAC_DATA.value,
            DatasetProvenance.REAL_AUTHORIZED_DATA.value,
            DatasetProvenance.HISTORICAL_DATA.value,
        ]:
            print(
                f"\n>>> [PROVENANCE NOTICE] Certified for AUTHORIZED_REAL_WORLD_VALIDATION.\n"
                f">>> Ingested under verified institutional meteorological authority.\n"
            )
            return True

        # Unknown provenance
        raise ScientificIntegrityError(f"Unrecognized provenance tier for scientific validation: '{prov_str}'")

    elif mode_str in [ExperimentMode.DEVELOPMENT_TEST.value, ExperimentMode.DEMO.value]:
        if prov_str in [DatasetProvenance.SYNTHETIC_DATA.value, DatasetProvenance.SAMPLE_DATA.value, "SYNTHETIC", "SAMPLE"]:
            print(
                f"\n>>> [SAFETY NOTICE] Running in {mode_str} mode on {prov_str}.\n"
                f">>> Results are for algorithmic testing/demonstration ONLY and CANNOT be cited as validated nowcasting skill.\n"
            )
        return True

    else:
        raise ValueError(f"Unknown experiment mode: '{experiment_mode}'. Expected 'DEVELOPMENT_TEST', 'DEMO', or 'SCIENTIFIC_VALIDATION'.")


def get_validation_tier(dataset_provenance: str, experiment_mode: str = ExperimentMode.SCIENTIFIC_VALIDATION.value) -> ValidationTier:
    """Returns the certified validation tier for a given provenance and mode."""
    enforce_experiment_safety_gate(dataset_provenance, experiment_mode)
    prov_str = str(dataset_provenance).upper()
    mode_str = str(experiment_mode).upper()

    if mode_str == ExperimentMode.SCIENTIFIC_VALIDATION.value:
        if prov_str == DatasetProvenance.PUBLIC_REAL_DATA.value:
            return ValidationTier.PUBLIC_DATASET_VALIDATION
        return ValidationTier.AUTHORIZED_REAL_WORLD_VALIDATION

    return ValidationTier.UNVALIDATED_DEVELOPMENT
