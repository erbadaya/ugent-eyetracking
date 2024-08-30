# How to navigate this folder

There are three folders here:

### 1. Audios GraphicsEx

Contains three .wav files (error.wav, qbeep.wav, type.wav)
Download these files if you are planning on setting the calibration and validation of the tracker using openGraphicsEx.

### 2. PsychoPy 20XX

The other two folders, PsychoPy 2022.1.1. and PsychoPy 2024.2.1 have the same folders and same structure. The difference in that each set of scripts works in different PsychoPy versions. This is because in PsychoPy 2024.2.1., sound was not played in the lab when the loudspeakers were connected. Apparently, by default PsychoPy was picking up a different set of speakers. Therefore, at the top of each script we have added the following code to get sounds playing (especially important for eye-tracker sounds and in VWP). Note that the reference for the speaker may change in a different set-up.

```
deviceManager = hardware.DeviceManager()
deviceManager.addDevice(
        deviceName='LoudSpeakers_2ndfloor',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=4.0
    )
```

Every folder contains a ```EyeLinkCoreGraphicsPsychoPy.py``` for graphics and the three sounds included in the Audio GraphicsEx folder.

Within these two folders, the structure is as follows:

#### 2.1. basic-functions-demos

Contains two scripts ```demo_code.py``` and ```demo_code_functions```. The former is an example of how to use pylink functions in PsychoPy. The latter extends this by implementing two of SR Research's helper functions to handle skipping trials and terminating experiments. 

#### 2.2. examples-experiments

##### 2.2.1. basic-script

```basic-script.py``` is a very basic example of an eye-tracking experiment. Participants are shown ten pictures (stored in \img) and have to decide whether the person is sad or happy.

The conditions of the experiment are saved in basicscript_conditions.xlx

##### 2.2.2. reading-experiment

```reading-psychopy.py```is an example of how to implement a single-sentence reading eye-tracking experiment on PsychoPy. While it is not ideal (e.g., how areas of interest are defined), the script also illustrates how to 1) change the position of the drift correction, 2) define dynamic areas of interest (i.e., where the size changes every trial), and 3) take screenshots in every trial for later visualizations and data pre-processing. 

The conditions of the experiment are saved in reading-psychopy.xlx

This experiment is based on [Rayner and Duffy's (1986)](https://link.springer.com/article/10.3758/bf03197692) Experiment 1, where they examined fixation times in reading as a function of word frequency, verb complexity and lexical ambiguity. In this case, we are working only with the materials where they manipulated word frequency: either high or low (e.g., The slow _music_ captured her attention v The slow _waltz_ captured her attention). There were three areas of interest: the word preceding the target word (in italics), the target word, and the word following the target word. We additionally add two more: The first word of the sentence and the rest of the sentence (i.e., five areas of interest). **Note** that this divide will vary depending on the specifics of each reading experiment, here we are doing it this way for learning purposes. Likewise, these areas of interest could be smaller or larger vertically. 

##### 2.2.3. visual-world-paraidmg

```vwp-allopena``` is an example of how to implement a Visual World Paradigm eye-tracking experiment on PsychoPy. The script shows how to 1) define areas of interest, 2) send triggers, 3) play audio, and 4) take screenshots in every trial for later visualizations and data pre-processing. 

The conditions of the experiment are saved in os_conditions.xlx

This task is a short conceptual replication of [Allopena et al. (1995)](), where they examined the time course of lexical access of a given word. In their experiment(s), participants were shown the target word, an object that phonologically overlapped with it (i.e., its cohort competitor), an object that rhymed with it, and an unrelated object. This experiment is a simplification of theirs (e.g., no familiarisation phase, fewer items on screen, shorter instructions). In our experiment participants are shown four images on the screen for 1000 ms, and then they hear an instruction referring to one of the objects on the screen ("Pick up the [target]"). 

If you find any typo or have any suggestions, please contact me at esperanza.badaya [at] ugent.be
