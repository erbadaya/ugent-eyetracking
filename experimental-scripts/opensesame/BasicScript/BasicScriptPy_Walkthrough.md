# Basic Script eye-tracking experiment

This script will walk you through the BasicScript.OS script and its eye-tracking functionalities. If you are not familiar with OpenSesame, visit their website [here](https://osdoc.cogsci.nl/) for different tutorials on how to code an experiment in OpenSesame. In this experiment, we are *not* covering regions of interest (see Visual World Paradigm example for this): Rather, we are learning the basic steps to do an eye-tracking experiments e.g., connecting to the tracker, performing a calibration, validation, and drift correction, and logging variables in the eye-tracking data.

The difference between this script and that without the ```_Py``` on its title is that here we are relying less on the plugins and instead, we refer to the functions from pygaze via the inline script. However, there are some instaces where it would be preferable to use the plugin instead (e.g., clashes between the drift correction and subsequent auditory stimuli).

In this walk through, we are going to focus on the inline script inside the loop sequence and describe the pygaze functions. To learn more about Python and OpenSesame, visit their [documentation](https://osdoc.cogsci.nl/4.0/manual/python/about/). 

# The experiment

This is a mock experiment where participants are shown faces and they have to say whether the person is sad or happy by pressing a key. Note that this design has many flaws (e.g., we are not controlling for a balanced presentation of stimuli). 

# The inline script for the experient

In this script, we are performing the drift correction, starting the recording, sending triggers and showing the stimuli. Note all of this is done in the run tab, but there is some code regarding the preparation of each trial's stimuli in the prepare tab. Further, all the eye-tracker functions (e.g., ```drift_correction()```) are called on an eye-tracker object, which is created when we initalise the tracker at that has to be referred to as ```eyetracker```.

The first step in our trial is to perform a drift correction with the ```drift_correction()``` function. This function can take as argument the position of the drift: Note that this is pass on as coordinates but in the coordinate system of the tracker, where 0,0 is the top left corner. To place the tracker in the middle of the screen, we need to write 512,384 (because our screen resolution is 1026 x 768).

```
eyetracker.drift_correction(pos=(512,384))
```

We can then start recording. We are also going to send a marker to the tracker to signal the beginning of the trial and ease trial segmentatin.

```
eyetracker.start_recording()
exp.pygaze_eyetracker.log('start_trial')
```

Next, we present the visual stimuli we had prepared in the prepare tab via the ```my_canvas.show()``` call. We also want to mark that the images are now on the display, so we will send another trigger to the tracker.

```
my_canvas.show()
exp.pygaze_eyetracker.log('display images')
```

The next lines in our script let the stimuli be on the screen until the participant perform an action with the keyboard or 2000 ms from the display of the images on the screen has elapsed. Then, we calculate participants' reaction time and accuracy.

At the end of the trial, but before we stop recording, we want to log some information in the .edf file (i.e., the eye-tracking data). For example, we want to save participants' RT and accuracy in the eye-tracking data, as well as what emotion was displayed on the screen, what picture in particular, participants' response and the correct answer. The function is ```log.var()```, which takes the name we want to give to the variable in the file within quotation marks, and the name of the variable in the environment without. In our case, this goes:

```
eyetracker.log_var('accuracy', accuracy)
eyetracker.log_var('RT', response_time)
eyetracker.log_var('emotion', emotion)
eyetracker.log_var('response', response)
eyetracker.log_var('face_item', stimuli) # stimuli is the name of the image in the script, in the .edf file this information will appear in a column called 'face_item'
eyetracker.log_var('correct_response', cor_ans)
```

We will also save all the variables in the .csv file for analysing the behavioural data. 

Finally, at the end of each trial, we want to stop the recording:

```
eyetracker.stop_recording()
```

Note that there may be some delays in the presentation of stimuli and the recording of eye-tracking data. This is why it is important to send triggers so you can properly segment your data. If you do not have any specific inter-trial interval, this should be ok-ish with you. However, it is important you pilot your own code and note any significant lags. Happy coding!