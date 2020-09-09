# qri-python

```
 ██████╗ ██████╗ ██╗
██╔═══██╗██╔══██╗██║
██║   ██║██████╔╝██║
██║▄▄ ██║██╔══██╗██║
╚██████╔╝██║  ██║██║
 ╚══▀▀═╝ ╚═╝  ╚═╝╚═╝
```

Python client for qri ("query")


# Installation

```
pip install qri
```

# About

Python wrapper to enable usage of [qri](https://qri.io/), the dataset toolchain. Can
either use a locally installed qri command-line program to work with your local repository,
or can directly get datasets from the [Qri Cloud](https://qri.cloud).

Dataset objects returned by this library have the components that exist in the
[standard qri model](https://qri.io/docs/dataset-components/overview). The body is returned
as a Pandas DataFrame in order to easily integrate with other data science systems, like
Jupyter Notebook.

# Usage

The following examples assume you have the latest release of the qri command-line client
installed. You can get this from https://github.com/qri-io/qri/releases

```
import qri
```

```
# Pull a dataset from cloud and add it to your repository
$ qri.pull("b5/world_bank_population")
```
> Fetching from registry...
>
> "Added b5/world_bank_population: ..."

```
# List datasets in your repository
$ qri.list()
```
> [Dataset("b5/world_bank_population")]

```
# Get that single dataset as a variable
$ d = qri.get("b5/world_bank_population")
```

```
# Look at metadata description
$ d.meta.description
```
> ( 1 ) United Nations Population Division. World Population Prospects: 2017 Revision...

```
# Get the dataset body as a pandas DataFrame
$ d.body
```
> `.   country_name  country_code   indicator_name    ...`
>
> `0   Afghanistan   AFG            Population, total ...`
> 
> `...`

TODO: Save changes

# Development

Clone this repository

```
git clone https://github.com/qri-io/qri-python
```

Navigate to the directory where you run jupyter from:

```
cd /path/where/jupyter/is/run
```

Symlink the cloned repository's source directory here:

```
ln -s /path/to/cloned/qri-python/qri .
```

NOTE: The clone command created the directory "qri-python", and inside is the source directory named "qri". Make sure to symlink the source directory, not just the repository root

This package should now be usable from within Jupyter Notebook
