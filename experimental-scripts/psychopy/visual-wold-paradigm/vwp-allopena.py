# Basic script for a Visual World Paradigm eye-tracking experiment
# We are not going to cover here creating functions to wrap up sections (see DataViewer proposed ideas)
# We are not covering handling errors
# The bits of code pertaining the task itself are not commented (check the PsychoPy course to follow what's happening!)

# Objectives of this script:
# Illustrate how to define & send ROIs to the tracker
# Illustrate how to send triggers
# Review of eye-tracking experiment in PsychoPy with Pylink (see basic-script.py for the basic template with a mock experiment)

# The task:
# This task is a short conceptual replication of Allopena et al. (1995)
# We have made slight modifications (e.g., no familiarisation phase, fewer items on screen)
# Display contains 4 images + a fixation cross in the middle
# Preview window of 1000 ms
# Audio begins ("Pick up the [target]")
# Participants click on the item

# Eye-tracking
## Start the experiment:
# We want to record at 1000 Hz
# We want a 9-point calibration & validation procedure
# We want to store all the events and sample data

## During the experiment
# We want every trial to start with a drift correction
# We want to see in the Host PC what trial number we are recording
# We want to start and stop the recording in every trial
# We want to send a trigger when images are shown
# We want to send a trigger for audio onset
# We want to send a trigger for target onset
# We want to send a trigger for audio offset
# We want to save ROIs
# Log information of set type, target type, RT, target position, specific items shown

# Additionally, we are going to write this code so that we can try it on our machines
# without the need of the eye-tracker
# we will do that via the variable dummy_mode

# Libraries

from psychopy import gui, visual, event, logging, data, sound, clock
import time, os, numpy
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)


# eye-tracking libraries
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder

# Participant data

info = {"Participant number":0, "EDF_name":"0"}
wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Participant number'])
    edf_name = str(info['EDF_name']) # to obtain EDF file name, you could alternatively use ppt_number
    
    behavioural_file = '/subject_' + ppt_number + '.txt'
    edf_file = edf_name + '.edf' # remember to add the .edf extension
    if not os.path.isfile(behavioural_file):
        ppt_number_taken = False

# Screen size

win_width = 1920
win_height = 1080
win = visual.Window([win_width,win_height], checkTiming=False, color = (1,1,1)) # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that
# more information on this issue here:
# https://discourse.psychopy.org/t/is-there-a-way-to-skip-frame-rate-measurement-on-each-initialisation/36232
# https://github.com/psychopy/psychopy/issues/5937

# stimuli
# in this case, w ehave a .xlsx file (os_conditions.xlsx) that has the combination of stimuli + information about conditions
# load it in
# materials (audios and images) are stored in the materials folder
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

trial_list = data.importConditions('os_conditions.xlsx') 
trials = data.TrialHandler(trial_list, nReps = 1, method = 'random')

for trial in trials:
    
    # positions
    # defined as absolute values (i.e., stay in the same places regardless of monitor dimensions)
    # the top right of the window has coordinates (1,1), the bottom left is (-1,-1)
    # in a cross, it'd be: 0, 0.5 (top of the cross); 0.5, 0 (right of the cross); 0, -0.5 (bottom of the cross), -0.5, 0 (left of the cross)
    positions = [(0, 0.5), (0.5, 0), (0, -0.5), (-0.5, 0)]
    numpy.random.shuffle(positions)
    
    print(trial)
    
    # images
    image_O1 = visual.ImageStim(win, image = 'materials/images/' + trial["O1"], pos = positions[0])
    image_O2 = visual.ImageStim(win, image = 'materials/images/' + trial["O2"], pos = positions[1])
    image_O3 = visual.ImageStim(win, image = 'materials/images/' + trial["O3"], pos = positions[2])
    image_O4 = visual.ImageStim(win, image = 'materials/images/' + trial["O4"], pos = positions[3])
    
    #sound
    # to send triggers for target onset, instead of measuring at what precise time it happens in an audio
    # we have cut the audio in two, so the trigger is sent when the second audio (i.e., the target) is played
    carrier_sound = sound.Sound('materials/audios/' + trial["instruction_audio"])
    target_sound = sound.Sound('materials/audios/' + trial["target_audio"])
    
    image_O1.draw()
    image_O2.draw()
    image_O3.draw()
    image_O4.draw()
    mouse = event.Mouse(visible = False, newPos = (0,0))
    win.flip()
    print('show images')
    time.sleep(1) # preview window
    # State variables for tracking mouse clicks
    
    mouseIsDown = False
    instructionPlayed = False 
    targetPlayed = False
    audioFinished = False
    
    print(carrier_sound.isFinished)
    print(carrier_sound.isPlaying)
    while True:
            if instructionPlayed == False:
                carrier_sound.play()
                clock.wait(carrier_sound.duration)
                carrier_sound.stop()
                instructionPlayed = True
            if instructionPlayed == True and targetPlayed == False:
                target_sound.play()
                clock.wait(target_sound.duration)
                target_sound.stop()
                targetPlayed = True
            if targetPlayed == True and audioFinished == False:
                mouse.setVisible(visible = True)
                if mouse.getPressed()[0] == 1 and mouseIsDown == False:
                    mouseIsDown = True
                if mouse.getPressed()[0] == 0 and mouseIsDown:
                    mouseIsDown = False
                    break
#            instructionPlayed = True
#            print(carrier_sound.duration)
#            carrier_sound.status = FINISHED
#            print(carrier_sound.status)
#        elif carrier_sound.isPlaying:
#            carrier_sound.stop()
#            target_sound.play(when=carrier_sound.status == FINISHED)
#            targetPlayed = True
#            print('target onset') 
#            target_sound.status = FINISHED
#        elif targetPlayed == True and audioFinished == False and target_sound.status == FINISHED:
#            audioFinished = True
#            print('target offset')
#            if mouse.getPressed()[0] == 1 and mouseIsDown == False:
#                mouseIsDown = True
#            if mouse.getPressed()[0] == 0 and mouseIsDown:
#                mouseIsDown = False
        # Check if the mouse is released
#            win.flip()
#            break
    