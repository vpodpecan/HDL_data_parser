
### About

This is a parser for the data published in the challenge **Predicting Parkinson's Disease Progression with Smartphone Data**. Collection of this data was supported by the [Michael J. Fox Foundation](https://www.michaeljfox.org/page.html?access-parkinsons-clinical-data-and-biospecimens) and is available on [Kaggle](https://www.kaggle.com/c/predicting-parkinson-s-disease-progression-with-smartphone-data/data).

The data contains several recording sessions for each patient. In each session, data from several sensors were collected (accelerometer, gps, compass, ...). Everything is time-labelled so we have a collection of time series for each patient. Note that this data is big (~10GB) so we are using appropriate libraries (pandas, pytables, HDF5). Because only data about single patient is held in memory at any time the parser only requires ~2GB of memory.

The aim of the parser is to collect and merge the data and prepare it for further analysis. The parser collects and stores the data for each patient and each sensor in a `pandas.DataFrame` object, concatenates sessions, sorts according to the time stamp, removes duplicates and finally stores the data in a HDF5 store. The store is organised hierarchically, e.g., `/name1/sensor1`, `/name1/sensor2`, ... , `/nameX/sensorX`.

The code is simple and quite self explanatory. There are almost no checks because we expect unmodified sensor data.

### How to use

1. First, you need to download the data. Download the file [`mjff_text_files.zip`](https://www.kaggle.com/c/predicting-parkinson-s-disease-progression-with-smartphone-data/download/mjff_text_files.zip) (10.47GB) and extract it somewhere on your disk (the archive contains 6906 .tar.bz2 archives and some hidden files which can be deleted).

2. Run the parser. If you put the data into the folder `input` and you want the HDF5 store in `output/hdl_data.h5` run:
 
        python3 source/parse_data.py -d input -s output/hdl_data.h5


3.  The result is a ~5GB HDF5 store which contains concatenated and sorted data. Now you can start with the real job and do some meaningful analysis ;)

### Requirements
In short, you need not-too-old versions of Python3, pandas and pytables (requires [HDF5](https://www.hdfgroup.org/HDF5/release/obtain5.html)). The code is known to work with:
* Python==3.4.1
* pandas==0.17.1
* pytables==3.2.2 
* hdf5==1.8.15

The code can be easily modified to use pickle instead HDF5. However, this may be less convenient because you will have to distribute the data across several files or load everything into memory when reading the processed data for the analysis.

