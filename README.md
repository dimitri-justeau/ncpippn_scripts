# ncpippn_scripts #

This repository contains helper scripts for NCPIPPN (New Caledonian Plant Inventory and Permanent Plot Network) field data preparation and compilation.

Three tools are available:
  
1. **easyplot**, a plot data collection software designed to run on a Windows CE platform. It is able to communicate with a Trupulse laser for recording position and height data. 
2. **easyplot_generator.py** is a command-line tool that generates easyplot databases.
3. **ncpippn_compiler.py** is a command-line tool that takes an easyplot database and compile it's data (dbh and positions) to produce a .csv file.


## Installation ##

### Python installation ###

**Linux users**: You do not need to install Python, it is already installed in your system.

**Windows users**: If you have not installed Python yet, you need to install it. To do so, go to Python's website (https://www.python.org/) and download the latest release for your system. It does not matter if you choose Python 2 or Python 3, *easyplot_generator.py* and *ncpippn_compiler.py* are compatible with both. Once the download is completed, run the installer. Finally, add the Python installation directory to your path (it should be "C:\Python<version>\"), and the Python Scripts directory (is should be "C:\Python<version>\Scripts\"), for having access to Python and pip in the Windows shell.

### Install dependencies ###

Before using the scripts, it is necessary to install the Python dependencies in requirements.txt (now there is only matplotlib, for the plot jpg output in *ncpippn_compiler.py*. To do so, execute the following command in the project folder:

`pip install -r requirements.txt`


## easyplot ##

Documentation available soon.

## easyplot_generator.py ##

easyplot_generator.py generates databases for collecting field data with easyplot. It is a command-line tool written in Python. Its usage is simple:

```
easyplot_generator.py [-h] database_path start_id end_id

  database_path  The output path of the database to generate.
                 To make it openable by EasyPlot, the suffix should be '.epdb'.      
  start_id       The starting id of the database to generate.
  end_id         The ending id of the database to generate.
```


## ncpippn_compiler.py ##

ncpippn_compiler.py takes an easyplot database, compute the dbh from the circumferences data, compute the positions from the Trupulse data (postions can be computed plot oriented, north oriented, or north oriented with relative references positioning).

It is a command-line tool written in Python, with a simple usage:

```
ncpippn_compiler.py [-h] [--csv_separator CSV_SEPARATOR]
                           [--output_plot_jpg OUTPUT_PLOT_JPG]
                           [--north_oriented NORTH_ORIENTED]
                           [--relative RELATIVE]
                           plot_azimuth input_database output_csv_file

positional arguments:
  plot_azimuth          The plot azimuth (float)
  input_database        The input easyplot database (.epdb)
  output_csv_file       The output file

optional arguments:
  -h, --help                          show this help message and exit
  --csv_separator CSV_SEPARATOR       The separator character to use for writing the output csv file.
  --output_plot_jpg OUTPUT_PLOT_JPG   If specified, NCPIPPN Compiler will generate a jpg representation 
                                          of the plot, with the positions of the trees.
  --north_oriented NORTH_ORIENTED     Compute the x, y coordinates in the north oriented coordinate system. 
                                          (boolean: true/false).
  --relative RELATIVE                 Compute the x, y coordinates in the north oriented using the
                                          relative positioning of the references 
                                          (boolean: true/false).
```

