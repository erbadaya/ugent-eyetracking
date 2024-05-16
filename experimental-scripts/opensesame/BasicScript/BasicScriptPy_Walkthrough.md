# Basic Script with Python

In this experiment, we are *not* covering regions of interest (see Visual World Paradigm example for this). This is the same task as BasicScript, but for those who prefer to use the inline script plugins and not rely on the plugins.

1. The task:

Emotion detection: Say whether a face is happy or sad
Participants are shown a face and press 'h' for happy or 's' for sad
They have a timeout of 2000 ms
We are going to have 10 trials
NB this design has many flaws (e.g., we are not controlling for a balanced presentation of stimuli). 

2. Eye-tracking

Start the experiment:
We want to record at 1000 Hz
We want a 5-point calibration & validation procedure

3. During the experiment

We want every trial to start with a drift correction
We want to see in the Host PC what trial number we are recording (done automatically by OS)
We want to start and stop the recording in every trial
We want to save the variable of emotion and the image presented

The script: