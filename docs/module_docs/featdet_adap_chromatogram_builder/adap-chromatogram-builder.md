# **ADAP chromatogram builder**

The _ADAP chromatogram builder_ module is one of the LC-MS feature detection algorithms provided by
MZmine 3. The module essentially builds
an [EIC](../../terminology/general-terminology.md#extracted-ion-chromatogram) for each _m/z_ value
that was detected over a minum number of consecutive scans in the LC-MS run. Each data file is
processed individually. The [mass list](../../terminology/general-terminology.md#mass-list)
associated to each MS1 scan (see [Mass detection](../featdet_mass_detection/mass-detection.md)
module) are taken as input and [feature list](../../terminology/general-terminology.md#feature-list)
is returned as output. Since mass lists must be, the _Mass detection_ module must be run first.

The _ADAP chromatogram builder_ algorithm operates as follow. The MS1 spectra in the LC-MS are
processed individually following a "chronological order" (_i.e._ increasing RT). Only MS1 scans are
processed. The [masses](../../terminology/general-terminology.md#masses-and-features) detected in
each MS1 spectrum (_i.e._ the mass list) are first sorted in order of decreasing intensity and the
processing starts from the most intense mass. Since no EICs have yet been created, a new EIC is
initialized and associated to the corresponding _m/z_ value. The same is repeated for all the masses
in MS1 scan and a set of EICs is created (constituting the _feature list_). The processing proceeds
with the second MS1 scan in the LC-MS run. Each mass is checked to determine if it "belongs" to an
existing EIC based on its _m/z_ and the user-defined tolerance (_i.e._ "Scan to scan accuracy (m/z)"
parameter). If a matching EIC is found, a new data point is added to the EIC and the
EIC-associated _m/z_ is updated. If no matching EIC is found, a new EIC is initialized. When no new
data point can be added to an EIC, the latter is terminated. The same is repeated for all the MS1
scans in the LC-MS run. When all the MS1 scans have been processed, the so-built set of EICs is
checked according to the user-defined parameters (_i.e._ minimum number of data points and
intensity). The EICs matching the requirements are retained in the feature list, whereas the rest
are discarded. The so-built EICs can then be deconvoluted into individual features by one of the
deconvolution algorithms provided by MZmine 3 (_
e.g._ [Local mimimum resolver](../featdet_resolver_local_minimum/local-minimum-resolver.md) module).

---

## Parameters settings

:material-menu-open: Feature detection → LC-MS → ADAP chromatogram builder
![ADAP Chromatogram Builder](adap_chromatogram_builder.png)

#### **Raw data files**

Select the input raw data files for chromatogram building. Mass lists associated with the data files
will be automatically selected. See option descriptions
in [Mass detection](../featdet_mass_detection/mass-detection.md#parameters-settings) module.

#### **Scans**

Select (or filter out) the MS scans to be processed. Several filters are avialble (see option
descriptions in [Mass detection](../featdet_mass_detection/mass-detection.md#parameters-settings)
module) but setting the _MS level = 1_ is usually sufficient for this module.

#### **Min group size in # of scans**

Minimum number of consecutive MS1 scans where a _m/z_ must be detected with a non-zero intensity in
order for the corresponding EICs to be considered valid and retained in the feature list.
:octicons-light-bulb-16: **Tip**. This parameter largely depends on the chromatographic system
setup (_e.g._ HPLC vs UHPLC) and the acquisition rate (_a.k.a._ MS scan speed) of the mass
spectrometer. The best way to optimize this setting is by manually inspecting the the raw data and
determining the typical minimum number of data points of the LC peaks. Usually, no less than 4-5
should be used.

#### **Group intensity threshold**

Minimum signal intensity that the group scans (see previous parameter) must exceed in order for the
corresponding EICs to be considered valid and retained in the feature list.
:octicons-light-bulb-16: **Tip**. A good starting point for this parameter is 3 times the noise
level used in the [Mass detection](../featdet_mass_detection/mass-detection.md).

#### **Min highest intensity**

Minimum intensity that the highest point in the EIC must exceed in order for the corresponding trace
to be considered valid and retained in the feature list.

#### **Scan to scan accuracy (m/z)**

Maximum allowed difference between an EIC-associated _m/z_ and a new data point to be added to the
existing EIC trace. It is essentially the maximum allowed mass accuracy deviation between
consecutive data points in the EICs. The tolerance can be set in _m/z_, ppm or both. It is
an [inter-scan _m/z_ tolerance](../../terminology/general-terminology.md#intra--and-inter-scan-tolerances) and it
depends on the mass accuracy, resolution and stabiity of the instrument.
:octicons-light-bulb-16: **Tip**. The best way to optimize this parameter is by manually inspecting
the the raw data and determining the typical fluctuation of the accurate mass measurement over
consecutive scans. A good starting point is 0.002-0.005 _m/z_ and 5-10 ppm for Orbitrap instruments,
while 0.005 _m/z_ and 10-15 ppm can be used for TOF devices.

#### **Suffix**

String added to the filename as suffix when creating the corresponding feature list.
