# condiana-jones
Try to approximately rewind time for a conda environment. A new conda file is generated with a version constraint correspondin to the date.

## Installation

The script needs `tqdm` and `pyyaml` to run. They can be, for example, installed using `environment.yaml`.

```shell
conda env create -f environment.yml
conda activate condiana-jones
```


## Usage

The script is called with the environment file and a date. The date is parsed by dateutils parser and should follow those conventions.
By default, the output is written to `stdout`, but a file can be specified using th `-o` argument.

```
usage: process.py [-h] [-o OUTPUT] environment-file date

positional arguments:
  environment-file      conda environment file
  date                  target date, e.g. 2022-11-20

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output environment file
```
