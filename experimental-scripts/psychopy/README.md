# How to navigate this folder

There are three folders and a file here:

### 1. Audios GraphicsEx

Contains three .wav files (error.wav, qbeep.wav, type.wav)
Download these files if you are planning on setting the calibration and validation of the tracker using openGraphicsEx.

### 2. PsychoPy 20XX

The folder Psycho v.2025.1.1. is the most up to date. 

Every folder contains a ```EyeLinkCoreGraphicsPsychoPy.py``` for graphics and the three sounds included in the Audio GraphicsEx folder.

Within these two folders, the structure is as follows:

#### 2.1. basic-functions-demos

Contains two scripts ```demo_code.py``` and ```demo_code_functions```. The former is an example of how to use pylink functions in PsychoPy. The latter extends this by implementing two of SR Research's helper functions to handle skipping trials and terminating experiments. 

#### 2.2. examples-experiments

##### 2.2.1. basic-script

```basic-script.py``` is a very basic example of an eye-tracking experiment. Participants are shown ten pictures (stored in \img) and have to decide whether the person is sad or happy.

The conditions of the experiment are saved in basicscript_conditions.xlx

##### 2.2.2. reading-experiment

```reading_tempate.py```is an example of how to implement a single-sentence reading eye-tracking experiment on PsychoPy. While it is not ideal (e.g., how areas of interest are defined), the script also illustrates how to 1) change the position of the drift correction, 2) define dynamic areas of interest (i.e., where the size changes every trial), and 3) take screenshots in every trial for later visualizations and data pre-processing. 

The conditions of the experiment are saved in reading-psychopy.xlx

This experiment is based on [Rayner and Duffy's (1986)](https://link.springer.com/article/10.3758/bf03197692) Experiment 1, where they examined fixation times in reading as a function of word frequency, verb complexity and lexical ambiguity. In this case, we are working only with the materials where they manipulated word frequency: either high or low (e.g., The slow _music_ captured her attention v The slow _waltz_ captured her attention).

##### 2.2.3. visual-world-paraidmg

```vwp_template.py``` is an example of how to implement a Visual World Paradigm eye-tracking experiment on PsychoPy. The script shows how to 1) define areas of interest, 2) send triggers, 3) play audio, and 4) take screenshots in every trial for later visualizations and data pre-processing. 

The conditions of the experiment are saved in os_conditions.xlx

If you find any typo or have any suggestions, please contact me at esperanza.badaya [at] ugent.be

### simple_iohub.py

This script is an adaptation of simply.py provided by PsychoPy to show the use of EyeLink with ioHub. The only extra element added is the naming of the .EDF file.
