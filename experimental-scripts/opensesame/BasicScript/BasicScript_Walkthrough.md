# Basic Script 

In this experiment, we are *not* covering regions of interest (see Visual World Paradigm example for this)

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

We have a welcome screen where we explain participants the task and provide a bit of information about the tracker (NB this should always be on top of all the information we give them verbally).

Afterwards, we encounter the first eye-tracking, pygaze plugin: ![](images/plugincalibration.JPG). This component deals with several steps at once: (1) starts the connection with the tracker, (2) allows us to set the tracker to different options (e.g., whether we want to run the experiment in dummy mode and what kind of tracker we are using) and (3) performs the calibration and validation. It works on a default 9HV.

The experiment then starts. Trial sequence is as follows:

- We first have a drift correction. This is incorporated by using the pygaze plugin ![](images/plugindrift.JPG). For this experiment, we are going to leave it with its default values.
- We then start the tracker recording with the plugin ![](images/pluginrecord.JPG)
- We present our stimuli on a canvas and gather responses with a keyboard.
- At the end of the experiment, we are going to log all experimental variables in the eye-tracking data with the plugin ![](images/pluginlog.JPG). For the time being, we are going to log all of them (select 'Automatically log all variables'). After that, we are going to stop the recording with the plugin ![](images/pluginstop.JPG). We then save our behavioural results with a logger.

After ten trials, the experiment ends. We do not need to add any information for the tracker (e.g., close the connection).

And that's it!