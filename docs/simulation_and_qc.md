# Simulation scope and quality control

## Numerical-model scope

The benchmark represents debris-flow impact on one lattice transmission-tower configuration.

- Debris flow: Smoothed Particle Hydrodynamics (SPH), modeled as a dense non-Newtonian granular mixture.
- Structure: Finite Element Method (FEM), using beam elements for the global lattice and three-dimensional solid elements for the lower leg segments.
- Interaction: penalty-based fluid–structure contact.
- Integration: explicit time integration with a Courant-controlled time step.

The numerical framework was evaluated against the rigid-wall flume tests of Moriguchi et al. at 45°, 55°, and 65°. The corresponding peak-force errors were 3.95%, 5.50%, and 0.82%.

## Principal numerical settings

| Setting | Value or description |
|---|---|
| Reference debris density | 2,000 kg/m³ |
| Weakly compressible SPH exponent | 7 |
| Numerical speed of sound | 20 times the characteristic maximum flow velocity |
| Gravity | 9.81 m/s² |
| Debris rheology | Cross-type apparent-viscosity model; calibrated parameters follow the associated study |
| Structural Young's modulus | 210 GPa |
| Structural Poisson ratio | 0.3 |
| Yield-strength range | 250–410 MPa, depending on member thickness |
| Strain-based erosion threshold | 14–18% accumulated plastic strain |
| Penalty-contact soft-constraint scale | 0.1 |

Parameters not included in the tabular release, including geometry files, proprietary solver inputs, and detailed calibrated rheology coefficients, are outside the scope of this dataset repository.

## Scenario generation

Debris-flow volume and slope angle were independently sampled using a Monte Carlo rejection-sampling procedure. Candidate SPH configurations were retained when their generated values satisfied the target criteria within the prescribed tolerance. Potential energy was then calculated from the accepted particle configuration as the sum of particle gravitational potential energies.

The released records span:

- debris-flow volume: 503–5,437 m³;
- slope angle: 30–60°;
- potential energy: 381–6,178 MJ.

## Descriptor extraction

Impact descriptors were extracted from the force and motion histories:

- contact duration: time interval of debris–tower contact;
- impulse: time integral of impact force;
- impact energy: time integral of force multiplied by velocity;
- peak force: maximum of the impact-force history.

Damage was quantified as accumulated plastic energy in the lowest front- and rear-leg members.

## Quality-control procedure

The release was produced as follows:

1. Aggregate 1,207 candidate summary rows from the simulation batches.
2. Convert all nine published variables to numeric values.
3. Apply a joint 1.5-IQR screen to the seven pre-event and impact descriptors. For each descriptor, retain values within `[Q1 - 1.5 IQR, Q3 + 1.5 IQR]`; a row must pass every descriptor screen.
4. Do not apply the optional hard peak-force threshold present in the development notebook.
5. Remove the internal folder-path column before public release.
6. Verify that the resulting 1,119 rows contain no missing values and no exact duplicate rows.

The current public release is therefore an analysis-ready, quality-controlled subset rather than an archive of raw solver output.

## Recommended use

- Use the fixed split in `metadata/benchmark_split.csv` for comparable benchmarks.
- Fit preprocessing transformations only on the training partition.
- Reserve the test partition for one final evaluation.
- Clearly distinguish pre-event prediction from descriptor-assisted interpretation when impact-derived variables are used.
- Report results separately for front- and rear-leg plastic energy.
