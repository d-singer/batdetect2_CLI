# Command Line Interface for batdetect2

This repository provides a Python script to enable command line interface (CLI) usage of *batdetect2* for batch analysis of large audio datasets in bat monitoring programs and research studies.

It adds some extra functionality to *batdetect2* that proved helpful when analyzing large amounts of audio data from an acoustic bat monitoring program in German forests ([https://doi.org/10.5281/zenodo.14535158](https://doi.org/10.5281/zenodo.14535158)). The development of the CLI approach for *batdetect2* was inspired by the great experience with the CLI usage of the *BirdNET Analyzer* ([https://github.com/BirdNET-Team/BirdNET-Analyzer](https://github.com/BirdNET-Team/BirdNET-Analyzer)).

The functionality of the script includes:

- Analyzing large amounts of audio data in a controlled and easy way via the command line interface in batches.
- Identifying and skipping audio files that have already been analyzed before (e.g., when restarting your computer after a crash).
- Cutting the audio data into batches per study site instead of using all sites mixed.
- Merging the *batdetect2* output per study site instead of storing one single CSV per audio file.
- Adding a row containing "no calls detected" to the *batdetect2* output if no call was identified in an audio file.

## Install batdetect2

Follow the instructions for installing *batdetect2* from [here](https://github.com/macaodha/batdetect2).

## Usage of the Command Line Interface

Given that *batdetect2* is installed, you can use the *batdetect2_cli.py* script to start a batch analysis of folders containing ultrasonic audio recordings.

The script is designed to run *batdetect2* on an input audio folder (default: `./01_AUDIO_DATA`), including one subfolder per study site. The subfolders are named after the ID of the study site (e.g., `./01_AUDIO_DATA/FOREST_01`). The script will always use the last folder from the path to identify the site ID (here: "FOREST_01").

1. Open your command line interface (e.g., Anaconda Powershell Prompt).
2. Run the following lines by copying them one by one into the command line interface and hitting "enter".
3. Optional: Activate the *batdetect2* Python environment.

    ```bash
    conda activate batdetect2
    ```

4. Navigate to the folder where the *batdetect2_cli.py* script is stored on your computer.

    ```bash
    cd C:\path\to\project\folder
    ```

5. Run the *batdetect2_cli.py* script with arguments for the relative paths to your audio data (`--audio-root`), the output directory (`--output-dir`), and the batch size (default = 100).

    ```bash
    python batdetect2_cli.py --audio-root "01_AUDIO_DATA" --output-dir "02_BATDETECT2" --batch-size 100
    ```

You will receive one CSV file per study site, named as follows: `batdetect2_FOREST_01.csv` in the output directory.

The code is free to use and adapt, however, please respect the license of *batdetect2*!