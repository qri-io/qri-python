# qri-python

```
 ██████╗ ██████╗ ██╗
██╔═══██╗██╔══██╗██║
██║   ██║██████╔╝██║
██║▄▄ ██║██╔══██╗██║
╚██████╔╝██║  ██║██║
 ╚══▀▀═╝ ╚═╝  ╚═╝╚═╝
```

qri python client


# Installation

<span style="color:red;font-size:140%;">Out of date</span>

```
pip install qri
```

# Usage

```
import qri
```

```
# Add a dataset from cloud to your repository
$ qri.add("b5/world_bank_population")
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

Make sure it's using the "new-model" branch:

```
cd qri-python
git checkout new-model
`` `

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
