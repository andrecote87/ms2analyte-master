# ms2analyte

Processing platform for mass spectrometry data, optimized for natural products research

## Getting Started

MS2Analyte accepts centroided mass spectrometry data from multiple instrument vendors (Waters, Thermo, Agilent) in a range of formats. mzML is the standard.

All files must have filenames in the format:

samplename_R1 where the R number is the replicate number. Samples without replicates should all be R1. Experiments with replicates should be R1, R2, R3 etc.

Samples must be in a directory named 'Samples'

Blanks (if available) must be in a directory named 'Blanks'

To run an analysis:

Clone the repository, and run run_ms2analyte.py

```
python run_ms2analyte.py
```

This starts the GUI for selecting input and output directories, and providing information about instrument and experiment variables

### Prerequisites

Requires Python 3.6+

Many dependencies. More information coming soon.

### Installing

Coming soon

## Running the tests

from parent directory run:

```
python -m unittest discover
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/rlinington/ms2analyte/tags).

## Authors

* **Roger Linington** - *Initial work* - [rlinington](https://github.com/rlinington)

See also the list of [contributors](https://github.com/rlinington/ms2analyte/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details