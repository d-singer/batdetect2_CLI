# Command Line Interface for batdetect2

This repository provides a python script to enable the command line interface usage of *batdetect2* for batch analyses of large audio datasets in bat monitoring programmes and research studies.

## Install batdetect2

Follow the instructions for installing *batdetect2* from here <https://github.com/macaodha/batdetect2>

## Usage of the command line interface

Given that *batdetect2* is installed you can simply use the *batdetect2_cli.py* script to start a batch analysis of folders containing ultrasonic audio recordings.

The script is specified to run *batdetect2* on an input audio folder (default: ./*01_AUDIO_DATA*), including one subfolder per study site (e.g *./01_AUDIO_DATA/SITE_01*). The subfolders are named after the ID of the study site. The script will always use the last folder from the path to identify the site ID.

1.  Open the command line interface (e.g. Anaconda Powershell Prompt)
2.  Run the following lined by copying them one by one to the command line interface and hiting "enter"

```{python}

# if you use an specific python environment, activite it first
conda activate batdetect2

# use the change directory command to navigate to your project main folder were the audio data and the "batdetect2_cli.py" script are stored. Alternatively 
cd C:\path\to\project\folder


python batdetect2_cli.py --audio-root "01_AUDIO_DATA" --output-dir "02_BATDETECT2" --batch-size 100

```
