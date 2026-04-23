# Shift, trim, and bin traces (Other detectors)

!!! info
    To process data from other detectors, the Other detector service of mzmine is required. This feature
    is included in the mzmine PRO subscription. Academic program and other users can reach out to
    inquire [access options](https://mzio.io/#contact).

This module preprocesses selected traces from other detectors before downstream baseline
correction, resolving, and MS correlation.

Typical use cases are:

- correcting a retention-time offset between the MS detector and another detector
- trimming away uninformative parts of the trace, for example solvent-gradient regions
- reducing the acquisition rate of high-frequency traces so they match the MS signal more closely

The module now supports both a manual RT shift and an automatic RT shift. In automatic mode,
mzmine determines one global shift for all selected raw data files from the MS base peak
chromatogram (BPC) and the selected other-detector traces.

## Parameters

![shift_traces.png](shift_traces.png)

#### Raw data files

Select the MS raw data files to process.

In automatic RT-shift mode, these files are also used to estimate one shared shift. Files that do
not yield enough valid matches are skipped, but the module only fails if none of the selected files
produces a valid automatic shift.

#### Trace selection

Select the traces to preprocess.

Only the traces matched by this parameter are binned, shifted, trimmed, and written as the
preprocessed traces of the corresponding other-detector time-series data.

For a detailed description of all sub-parameters
see [trace selection parameter](../otherdetector_glossary.md#trace-selection-parameter).

#### RT shift (manual/auto)

Select how the RT shift is determined.

`Manual` uses the entered RT offset in minutes. The value is added to the RT axis of the selected
traces. Positive values move the trace to later retention times, negative values move it to earlier
retention times.

`Auto` determines one global shift from the selected files. The preview uses the same automatic
shift calculation as the task and reports the resolved shift if it succeeds.

If automatic shift detection does not find enough validated matches in any selected file, mzmine
throws an error and asks you to set a manual shift.

#### Trim RT range

Select the RT range you want to keep.

Trimming is applied after the RT shift.

#### Bin width (manual/auto)

Enable this optional parameter to bin the selected traces before shift determination and before
trimming.

`Auto` adjusts the acquisition rate of the other-detector trace to about **four times** the MS
acquisition rate.

`Manual` bins the entered number of consecutive points together.

If binning is disabled, the original selected traces are used directly.

## Algorithm

The module processes the selected traces in this order:

1. Optional binning
2. RT shift determination
3. RT shifting
4. Optional RT trimming

### Automatic RT shift

In `Auto` mode, mzmine estimates one global RT shift from the selected files as follows:

1. The selected traces are optionally binned first. The automatic shift is always calculated from
   these binned traces.
2. For each selected raw data file, mzmine builds the MS base peak chromatogram and resolves peaks
   in the BPC and in the selected other-detector traces with the Wavelet resolver.
3. The minimum peak height is set to 0.1% of the maximum intensity of the respective signal.
4. Peaks with a direct neighbour are excluded, so only unambiguous peaks are used for alignment.
5. mzmine generates candidate shifts from apex differences between BPC peaks and other-detector
   peaks.
6. Candidate peak pairs are then validated by chromatographic shape correlation using a Pearson
   correlation threshold of at least 0.8.
7. A file contributes to the automatic shift only if at least three validated peak matches are
   found.
8. The final global shift is the median of all valid file-level shifts.

Files without enough evidence are skipped. If no selected file contributes a valid shift, the
module stops and prompts you to use a manual RT shift instead.

## Results

The module stores the processed selected traces as the preprocessed traces of the matched
other-detector time-series data.

This makes the output directly available to later modules such as
[Baseline correction](../uv_baseline_correction/uv_baseline_correction.md),
[Resolve traces](../uv_resolve_traces/uv_local_min_resolver.md), and
[Correlate MS features with other detectors](../uv_ms_other_aligner/uv_ms_other_aligner.md).

!!! tip
    If the automatic RT shift fails, start by checking that the selected trace really contains
    chromatographic peaks that are also visible in the MS BPC. If the signals differ strongly, use
    a manual RT shift instead.
