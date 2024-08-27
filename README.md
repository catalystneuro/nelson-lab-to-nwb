# nelson-lab-to-nwb
NWB conversion scripts for the [Nelson lab](https://nelsonlab.ucsf.edu/) data to the
[Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.

## Installation
The package can be installed from this GitHub repo, which has the advantage that the source code can be modifed if you need to amend some of the code we originally provided to adapt to future experimental differences. To install the conversion from GitHub you will need to use `git` ([installation instructions](https://github.com/git-guides/install-git)). The package also requires `Python > 3.9`. We also recommend the installation of `conda`
([installation instructions](https://docs.conda.io/en/latest/miniconda.html)) as it contains all the required machinery in a single and simple install.

From a terminal (note that conda should install one in your system) you can do the following:

```
git clone https://github.com/catalystneuro/nelson-lab-to-nwb
cd nelson-lab-to-nwb
conda env create --file make_env.yml
conda activate env_nelson
python -m ipykernel install --user --name env_nelson
```

This creates a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html)
which isolates the conversion code from your system libraries.  We recommend that you run all your conversion related tasks and analysis from the created environment in order to minimize issues related to package dependencies.

Alternatively, if you have Python > 3.9 on your machine and you want to avoid conda altogether (for example if you use another virtual environment tool), you can install the repository with the following commands using only pip:

```
git clone https://github.com/catalystneuro/nelson-lab-to-nwb
cd nelson-lab-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs).


## Conversion
At each experiment's folder you will find:
- The conversion scripts `convert_session.py`.
- The converter code `<experiment>_converter.py`.
- Example metadata files `metadata_example.yaml`.
- Jupyter notebooks `example_conversion.ipynb` demonstrating the usage of the conversion scripts and basic exploratory data analysis.
- A `README.md` file with a basic description of the data.

To run the example notebooks, just navigate to the experiment's folder and run from the terminal:

```bash
jupyter notebook
```

 This will open a new tab in your browser with the Jupyter interface. From there you can open the `example_conversion.ipynb` notebook and follow along.


## Upload to DANDI archive
Detailed instructions on how to upload the data to the DANDI archive can be found [here](https://github.com/catalystneuro/nelson-lab-to-nwb/blob/main/dandi.md).