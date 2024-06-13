# Basic Script eye-tracking experiment

This script will walk you through the BasicScript.OS script and its eye-tracking functionalities. If you are not familiar with OpenSesame, visit their website [here](https://osdoc.cogsci.nl/) for different tutorials on how to code an experiment in OpenSesame. In this experiment, we are *not* covering regions of interest (see Visual World Paradigm example for this): Rather, we are learning the basic steps to do an eye-tracking experiments e.g., connecting to the tracker, performing a calibration, validation, and drift correction, and logging variables in the eye-tracking data.

# The experiment

This is a mock experiment where participants are shown faces and they have to say whether the person is sad or happy by pressing a key. Note that this design has many flaws (e.g., we are not controlling for a balanced presentation of stimuli). 

# The set up

- Welcome the participant and present instructions about the calibration and the validation procedures.
- Initialise the tracker (i.e., establish the connection with the tracker and do a calibration and a validation).
- Start the experiment (i.e., the loop form, twice, one per group).
- The trial sequence:
  - Drift correction (shown where the sentence starts).
  - Start recording
  - Presentation of stimuli 
  - Keyboard response
  - Log variables in the .edf file
  - Log variables in the .csv file
  - Stop recording
- A goodbye screen

# The eye-tracking components

1. At the beginning of the experiment

Start the experiment:
We want a calibration & validation procedure

2. During the experiment

We want every trial to start with a drift correction
We want to see in the Host PC what trial number we are recording (done automatically by OS)
We want to start and stop the recording in every trial
We want to save the variable of emotion and the image presented

# The experiment code

1. Welcome screen

We have a welcome screen where we explain participants the task and provide a bit of information about the tracker (NB this should always be on top of all the information we give them verbally).

2. Initialise the tracker

Afterwards, we encounter the first eye-tracking, pygaze plugin: ![](images/plugincalibration.JPG). This component deals with several steps at once: (1) starts the connection with the tracker, (2) allows us to set the tracker to different options (e.g., whether we want to run the experiment in dummy mode and what kind of tracker we are using) and (3) performs the calibration and validation. It works on a default 9HV.

3. Start the experiment 

To better understand the loop plugin and its function within the experiment, visit [this page](https://osdoc.cogsci.nl/4.0/manual/structure/loop/). In our experiment, we have the image to be presented, the actual emotion displayed, and what key is the right answer.

4. The trial sequence

4.1. Drift correction

  We first have a drift correction. This is incorporated by using the pygaze plugin ![](images/plugindrift.JPG). For this experiment, we are going to leave it with its default values. This means that the drift correction will appear in the middle of the screen (0, 0 coordinates)

4.2. Start recording

We then start the tracker recording with the plugin ![](images/pluginrecord.JPG). This will mark the start of the trial in our data.

4.3. Presentation of stimuli

We present our stimuli on a canvas and gather responses with a keyboard.

4.4. Log in variables in the .edf file

At the end of the experiment, we are going to log all experimental variables in the eye-tracking data with the plugin ![](images/pluginlog.JPG). For the time being, we are going to log all of them (select 'Automatically log all variables'). Note that, in reality, you should not do this as this will impact your intertrial interval.

4.5. Log in variables in the .csv file

We also want to save all the trial information in the behavioural file (the .csv file). We do this with the logger component.

4.6. Stop  the recording

After that, we are going to stop the recording with the plugin ![](images/pluginstop.JPG). This will segment the data to mark when the trial ended. We do it by adding the pygaze stop recording plugin.

After ten trials, the experiment ends. We do not need to add any information for the tracker (e.g., close the connection).

5. Goodbye screen

Once our participants have gone through all the selected rows of our loop (e.g., all, a section, depending on what we specify), we want to show them a goodbye screen to thank them for their time and inform them the experiment is over. We do this with a canvas plugin.

Happy coding!