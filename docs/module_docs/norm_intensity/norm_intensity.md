# Intensity normalizer

## Description

:material-menu-open: **Feature list methods -> Normalization -> Intensity normalizer**

The Intensity normalizer scales each feature using a per-file normalization function.

- One normalization function is built for each reference file.
- If a file is not a reference file, its normalization is interpolated from neighboring reference
  runs using acquisition time.
- The module writes normalized values to **Normalized height** and **Normalized area**.
- Original (non-normalized) height and area are kept.

!!! warning

    This module requires valid acquisition timestamps for all processed files. It first uses the raw file start timestamp and falls back to the project metadata run-date column.

!!! Note

    Normalization works on aligned feature lists because standard rows must represent the same compounds across files.

---

## Parameters

#### Feature lists

Feature list(s) to normalize.

#### Name suffix

Suffix appended to the output feature list name.

#### Normalization type

Selects the normalization strategy. Each strategy has its own sub-parameters.

Available strategies:

- Average intensity
- Median feature intensity
- Maximum peak intensity
- TIC
- Metadata column
- Standard compounds

#### Feature measurement type

Selects which abundance is used by algorithms that operate on feature abundance values.

- Height
- Area

#### Original feature list

Choose whether to keep or remove the original feature list.

### Type-specific parameters

#### Factor-based types

These types share one sub-parameter set:

- **Reference samples**: sample types used as reference runs (default: QC).

Factor-based types:

- **Average intensity**: uses mean feature abundance per reference file.
- **Median feature intensity**: uses median feature intensity per reference file.
- **Maximum peak intensity**: uses maximum feature abundance per reference file.
- **TIC**: uses sum of MS1 scan TIC per reference file.

#### Metadata column

This type has its own sub-parameter set:

- **Metadata column**: select a numeric metadata column used to derive per-file factors.
  Every file must have a value in this column. Use `0` to disable normalization for a file (factor
  `1`).

All files in the selected feature list are used directly as references for this type.

#### Standard compounds

This type has its own sub-parameter set:

- **Reference samples**: sample types used as reference runs (default: all sample types).
- **Normalization type**:
    - Nearest standard
    - Weighted contribution of all standards
- **m/z vs RT balance**: multiplier for m/z distance in standard matching.
- **Standard compounds**: selected feature-list rows used as standards.
- **Require all standards**: if enabled, all selected standards must be present with valid abundance
  in each raw file. If disabled, missing or invalid standards are skipped. In **Nearest** mode, each
  raw file still needs at least one valid standard.

---

## Algorithm {#algorithm}

### 1. Build reference functions

For all selected reference files, the module creates one normalization function.

#### Factor-based types

For each reference file `f`, a metric `M_f` is calculated (depends on selected type). The file
factor is:

`F_f = max(M_ref) / M_f`

where `max(M_ref)` is the maximum metric among reference files.

#### Metadata column

For each file `f`, the selected metadata column provides a numeric value `V_f`.

- For `V_f > 0`: `F_f = max(V_all) / V_f`
- For `V_f = 0`: `F_f = 1`

where `max(V_all)` is the highest metadata value across all files in the feature list.

Validation rules:

- The selected metadata column must exist and be numeric.
- Each file must have a finite metadata value.
- Metadata values must be zero or positive.
- Zero will result in no normalization for that file (factor `1.0`).
- Negative values are rejected.

#### Standard compounds

For each reference file, a standard-compound normalization function is created from selected
standard rows:

- Distance for a feature `(mz, rt)` to standard point `i`:

  `d_i = mzVsRtBalance * abs(mz - mz_i) + abs(rt - rt_i)`

- **Nearest**: uses abundance of the closest standard point.
- **Weighted**:
    - If one or more standards have `d_i = 0`, uses the mean abundance of those direct matches.
    - Otherwise uses inverse-distance weighted abundance over available standards.
    - If all standards are missing and **Require all standards** is disabled, fallback abundance is
      `1.0` (factor `1.0`).

The final factor from standard abundance `A` is:

`factor = 1 / A`

(no additional fixed scaling factor is applied).

### 2. Interpolate non-reference files

For files that are not references, the module finds previous and next reference runs by acquisition
time and computes interpolation weights.

- Factor-based types interpolate scalar factors linearly:

  `F_interp = w_prev * F_prev + w_next * F_next`

- Standard compounds interpolate feature-wise factors through an interpolated function:

  `factor(mz, rt) = w_prev * factor_prev(mz, rt) + w_next * factor_next(mz, rt)`

- Metadata column uses all files as reference files, so interpolation is not required.

If only one neighboring reference exists, it is used as both previous and next.

### 3. Apply normalization to all features

For each feature with coordinates `(mz, rt)` in a file:

- `normalized_height = height * factor(mz, rt)`
- `normalized_area = area * factor(mz, rt)`

### 4. Persist functions in applied method

The final per-file normalization functions are stored in the applied method parameters so the same
normalization can be reused for future features.

---

{{ git_page_authors }}
