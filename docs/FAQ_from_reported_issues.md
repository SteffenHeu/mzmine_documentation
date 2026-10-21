# Frequently asked questions from reported issues

> Draft for migration into the user documentation. This is a curated FAQ, not an issue index: it
> consolidates recurring user questions from open and closed reports into durable guidance. Issue
> links provide the original context and any version-specific details. Reviewed 2026-07-13.

## Data import and conversion

### Which open data format should I use?

Use centroided **mzML** when converting data to an open format. It is the newer standard and is the
best first remedy when an mzXML file is malformed or cannot be parsed. Convert again from the
original vendor file, rather than editing the failed file; use 64-bit _m/z_ encoding for
high-resolution data.

There is one important, instrument-specific exception: for **recalibrated Bruker BAF** data, the
current data-conversion guidance explains when exporting mzXML from DataAnalysis better retains scan
definition and recalibration information. Follow that specialised guidance when it applies; do not
assume that a generic conversion workaround preserves recalibration metadata.

- Documentation: [data conversion](https://mzmine.github.io/mzmine_documentation/data_conversion.html)
- Related reports: [malformed mzXML import](https://github.com/mzmine/mzmine/issues/1851) (closed),
  [Bruker DataAnalysis mzXML and MS/MS pairing](https://github.com/mzmine/mzmine/issues/2001) (closed),
  [Bruker DataAnalysis mzML import](https://github.com/mzmine/mzmine/issues/3349) (open)

### A vendor file will not import. What should I check first?

First check that the format is supported on your operating system. Some vendor readers are
platform-specific; when the native reader is unavailable or the vendor export fails, convert the
original data on Windows with MSConvert and import the resulting mzML. For folder-based vendor
formats, import the complete acquisition folder in the **MS data files** area rather than selecting
an internal file.

If only one converted file fails, treat it as a file-conversion or file-integrity problem: reconvert
that file from the original data and confirm that it can be opened independently before starting a
large batch.

- Documentation: [supported formats and platform support](https://mzmine.github.io/mzmine_documentation/data_conversion.html)
- Related reports: [corrupted import stops a batch](https://github.com/mzmine/mzmine/issues/1851)
  (closed), [Bruker folder import and conversion](https://github.com/mzmine/mzmine/issues/2001)
  (closed)

### Thermo RAW files report “No scans found” or previously working files no longer open. What can I do?

For mzmine 4.8 and newer, update to a current release and use the built-in Thermo RAW import. On
older releases that used the extracted ThermoRawFileParser, close mzmine and delete the
`mzmine_thermo_raw_parser` directory from both the mzmine temporary directory and the operating
system temporary directory; then retry. If the problem persists, convert the RAW file to mzML and
include an example RAW file and the log when reporting it.

On older Apple-silicon macOS installations, the bundled parser could fail because of Mono. The
reported workaround was installing the Mono runtime/MDK; updating mzmine is preferable to relying
on that legacy workaround.

- Documentation: [Thermo RAW handling](https://mzmine.github.io/mzmine_documentation/data_conversion.html#thermorawfileparser),
  [troubleshooting](https://mzmine.github.io/mzmine_documentation/troubleshooting.html)
- Related reports: [parser temporary-directory workaround](https://github.com/mzmine/mzmine/issues/1545)
  (closed), [older Apple-silicon Mono issue](https://github.com/mzmine/mzmine/issues/1942) (closed)

## Feature lists and MS/MS assignment

### Why can I not select my blanks in Feature list blank subtraction?

**Feature list blank subtraction** requires one *aligned feature list* containing both blank/control
and sample raw-data files. Run the Join Aligner first (or start from a complete wizard workflow),
then select the blank raw-data files in the module’s **Blank/control raw data files** parameter.
It does not subtract one separately processed feature list from another.

- Documentation: [Feature list blank subtraction](https://mzmine.github.io/mzmine_documentation/module_docs/filter_blanksubtraction/filter_blanksubtraction.html)
- Related report: [how to select blanks after processing](https://github.com/mzmine/mzmine/issues/2492)
  (closed)

### Why does alignment create far more rows than expected, or show apparent duplicate features?

Do not automatically merge rows with similar annotations: they may be chromatographically separated
isomers, in-source fragments, or incorrectly paired MS/MS spectra. Inspect the feature shapes and
the Join Aligner’s alignment columns first. Then check whether the samples are heterogeneous or
were acquired in separate instrument batches, as retention-time drift can prevent otherwise matching
features from aligning.

If batch effects are visible, apply retention-time calibration before alignment. If many
low-quality, sample-specific features are present, make mass detection/resolving more selective
(for example, raise the MS1 noise threshold) and reassess the result. Tune retention-time
tolerances using the observed drift, not a universal value.

- Documentation: [Join Aligner](https://mzmine.github.io/mzmine_documentation/module_docs/align_join_aligner/join_aligner.html),
  [retention-time calibration](https://mzmine.github.io/mzmine_documentation/module_docs/norm_rt_calibration/scan-based-rt-corr.html)
- Related reports: [excessive aligned rows](https://github.com/mzmine/mzmine/issues/3023)
  (closed), [same annotation on multiple feature IDs](https://github.com/mzmine/mzmine/issues/2815)
  (open)

### Why is an MS/MS spectrum associated with the wrong feature or isotope peak?

Run **Assign MS2 to feature** after feature detection and use **Use feature edges** for the
retention-time filter unless there is a clear reason to use a fixed RT tolerance. This limits the
candidate spectra to the chromatographic peak boundaries. Also verify the precursor _m/z_ tolerance
and inspect the paired spectra; vendor files may record a precursor value that differs from the
monoisotopic feature.

Increasing the pairing tolerance can recover spectra for standards or simple data, but it can also
create incorrect identifications in complex samples. Use that change only after inspecting the
effects, and prefer feature-edge pairing where possible.

- Documentation: [MS2 Scan Pairing](https://mzmine.github.io/mzmine_documentation/module_docs/featdet_ms2_scan_pairing/ms2_scan_pairing.html)
- Related reports: [multiply charged precursor and tolerance](https://github.com/mzmine/mzmine/issues/2001)
  (closed), [multiple IDs and MS/MS pairing](https://github.com/mzmine/mzmine/issues/2815) (open)

## Performance and batch processing

### How do I resolve `java.lang.OutOfMemoryError: Java heap space` during chromatogram building?

Increasing the JVM memory limit alone may not solve this, because chromatogram building can create
many concurrent chromatograms. First reduce the number of mzmine threads, then increase the MS1
mass-detection noise threshold so fewer data points enter feature detection. For large or profile
datasets, enable **Advanced data import** to apply mass detection while importing and remove the
later duplicate mass-detection step.

Keep the temporary directory on a fast local SSD with ample free space and use the default
memory-mapped mode unless the machine has sufficient RAM for an in-memory workflow.

- Documentation: [performance and memory options](https://mzmine.github.io/mzmine_documentation/performance.html)
- Related reports: [heap-space error during chromatogram building](https://github.com/mzmine/mzmine/issues/3025)
  (closed), [chromatogram builder memory use](https://github.com/mzmine/mzmine/issues/497) (open)

### Can I run a batch on an HPC or other headless Linux system?

Yes. Use the command-line interface with a saved `.mzbatch` file, a logged-in user file (or
`-login-console`), an explicit local temporary directory, and an appropriate `-threads` setting.
Avoid network-backed temporary storage when possible.

If an older installation fails with an `Unable to open DISPLAY` error while exporting annotation
graphics, update mzmine and regenerate the batch if necessary. As an immediate workaround, remove
the graphical annotation-export step or run that export in a graphical/X-forwarded session.

- Documentation: [command-line interface](https://mzmine.github.io/mzmine_documentation/commandline_tool.html),
  [performance guidance](https://mzmine.github.io/mzmine_documentation/performance.html)
- Related report: [headless graphical-export failure](https://github.com/mzmine/mzmine/issues/1658)
  (closed)

## Before opening a new issue

Include the exact mzmine version and operating system, the full log file (`mzmine_0_0.log`), the
batch file, expected and observed behaviour, and a small reproducible input file whenever possible.
For feature-table questions, add screenshots of the relevant feature shapes and MS/MS pairing.
These details turned recurring reports into actionable fixes much more reliably than screenshots of
the error alone.

- Documentation: [reporting issues](https://mzmine.github.io/mzmine_documentation/troubleshooting.html#reporting-issues)
- Examples: [feature-ID investigation](https://github.com/mzmine/mzmine/issues/2815),
  [import reproducibility request](https://github.com/mzmine/mzmine/issues/1851)
