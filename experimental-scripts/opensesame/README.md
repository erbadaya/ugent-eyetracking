The following scripts do assume a basic knowledge of OpenSesame (e.g., stimuli presentation). If you're starting with it, you may want to have a look at their [website](https://osdoc.cogsci.nl/) - their tutorials are very illustrative, and the forum users very helpful.

Most of these scripts are built in OpenSesame version 4.0.1. For eye-tracking, we are using the _pygaze_ module (you can find instructions on how to install it here, including installing _pylink_ if you are going to set the tracker to one manufactured by SR Research). SR Research also has its own plugins. However, there are some compatibility issues with different versions of OpenSesame. For that reason, we will only focus on the pygaze module (which also allows you to use trackers other than those manufactured by SR Research).

These scripts are divided into those relying mostly on plugins (i.e., minimal coding) and those mostly using Python. 

As a reminder, this is the flow of an eye-tracking experiment in OpenSesame:

1. Calibration and validation.
2. Drift correction
3. Start recording
4. Send triggers (e.g., when an image in shown, when an audio starts playing) [optional]
5. Send information about the visual display (i.e., Areas of Interest) [optional]
6. Log variables for the .edf file (e.g., what kind of trial it was, what level of manipulation was shown)
7. Stop recording


In this folder you can find:

- BasicScript.os and BasicScriptPy.os: The former relies more on plugins, the latter on Python. They are two experiments where participants are shown faces and they have to decide whether they are happy or sad.
    - The .md files are the walkthrough of the scripts.
    - What does it cover in terms of eye-tracking?
        - Calibration & validation
        - Drift correction
        - Start & stop recording
        - Log variables in the .EDF file 
        - Send triggers
- VWPAllopenna.os and VWPAllopenaPy.os: They are two adaptations of Allopena et al. (1998) where participants see four images on the screen and are asked to click on one of them.
    - The .md files are the walk through of the scripts.
    - What does it cover in terms of eye-tracking?
        - Areas of Interest
        - Triggers
- SingleSentence.os and SingleSentencePy.os: They are two adaptations of Frisson et al. () where participants are presented sentences on the screen and are asked to read them.
    - The .md files are the walk through of the scripts.
    - What does it cover in terms of eye-tracking?
        - Areas of Interest (where size changes between trials)
