# Debris Flow–Transmission Tower Impact Dataset

This repository provides an analysis-ready benchmark of coupled SPH–FEM simulations of debris-flow impact on a lattice transmission tower. The release contains **1,119 quality-controlled records** spanning debris-flow volumes of 503–5,437 m³ and slope angles of 30–60°.

The variables follow the physical sequence of the event:

1. **Pre-event descriptors:** debris-flow volume, slope angle, and gravitational potential energy.
2. **Impact descriptors:** contact duration, impact energy, maximum impact force, and impulse.
3. **Damage responses:** accumulated plastic energy in the front and rear lower-leg members.

## Repository contents

| Path | Purpose |
|---|---|
| `simulation_summary_github.csv` | Quality-controlled dataset used by the benchmark |
| `metadata/data_dictionary.csv` | Machine-readable variable definitions, units, roles, and availability |
| `metadata/dataset_statistics.csv` | Descriptive statistics for all released variables |
| `metadata/benchmark_split.csv` | Fixed 80:20 train–test split and five CV folds for the training rows |
| `docs/simulation_and_qc.md` | Simulation scope, parameter ranges, extraction, and quality-control procedure |
| `scripts/generate_metadata.py` | Recreates the split and descriptive statistics |
| `scripts/run_baselines.py` | Runs reproducible regression baselines for two predictor-availability tasks |
| `results/baseline_metrics.csv` | Held-out baseline results on the recommended split |

## Predictor-availability tasks

The repository distinguishes two tasks to prevent impact quantities from being mistaken for pre-event information.

### Task A: pre-event screening

Inputs available before impact:

- `volume_m3`
- `slope_deg`
- `potential_energy_MJ`

Targets:

- `plastic_energy_MJ_front`
- `plastic_energy_MJ_rear`

### Task B: descriptor-assisted interpretation

Inputs include the three pre-event descriptors and the four impact descriptors. This task supports retrospective or simulation-assisted interpretation; it is not a purely pre-event forecasting task.

## Recommended benchmark split

`metadata/benchmark_split.csv` fixes an 80:20 split generated with scikit-learn `train_test_split(..., test_size=0.20, random_state=42)`. Training records also receive a shuffled five-fold CV assignment (`cv_fold` 0–4, seed 42). The test records must remain untouched during model selection.

The split uses zero-based `row_index` values from `simulation_summary_github.csv`. `record_id` is a stable convenience label derived from that index.

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/validate_release.py
python scripts/generate_metadata.py --check
python scripts/run_baselines.py
```

The baseline script evaluates linear regression, random forest, gradient boosting, support vector regression, and a multi-layer perceptron. It reports held-out R², MAE, and RMSE separately for the front- and rear-leg responses.

## Quality-control note

The public CSV contains 1,119 complete numeric records. The local aggregation preceding release contained 1,207 candidate rows. A joint 1.5-IQR screen was applied to the seven pre-event and impact descriptors, retaining 1,119 rows; no additional hard force threshold was applied. The released file contains no missing values or duplicate rows. Details are provided in [`docs/simulation_and_qc.md`](docs/simulation_and_qc.md).

## Units

The stored impact energy, peak force, and impulse are in J, N, and N·s, respectively. Divide these columns by `1e6` to obtain MJ, MN, and MN·s for plotting or interpretation. Plastic energies and potential energy are already stored in MJ.

## Scope and limitations

The dataset represents one tower configuration, one numerical-modeling setup, and the sampled debris-flow design space. It should not be treated as direct evidence of transferability to other tower geometries, foundation conditions, material systems, terrains, impact directions, or field events without additional calibration and validation.

## Citation

If you use this dataset, please cite the associated manuscript and this repository. Citation metadata are available in [`CITATION.cff`](CITATION.cff).

## Contact

For questions about the dataset or benchmark, please open a GitHub issue.
