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
# We want to send a trigger for target offset
# We want to save ROIs
# Log information of set type, target type, target position, specific items shown

# Additionally, we are going to write this code so that we can try it on our machines
# without the need of the eye-tracker
# we will do that via the variable dummy_mode

# Libraries

from psychopy import gui, visual, event, logging, data, sound, clock
import time, os, numpy

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
# in this case, we have a .xlsx file (os_conditions.xlsx) that has the combination of stimuli + information about conditions
# load it in
# materials (audios and images) are stored in the materials folder
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

trial_list = data.importConditions('os_conditions.xlsx') 
trials = data.TrialHandler(trial_list, nReps = 1, method = 'random')

# Open connection to the Host PC
# Here we create dummy_mode

dummy_mode = True # assuming we are piloting in our machine, set to False when using the tracker
tracker_mode = False # assuming we are piloting in our machine, set to True when using the tracker

if dummy_mode:
    et_tracker = pylink.EyeLink(None)
    et_version = 0 # version of tracker, we will call this later in the code so we need to set a value for dummy_mode too
else:
    et_tracker = pylink.Eyelink("100.1.1.1")
    et_version = int(vstr.split()[-1].split('.')[0]) # version of the tracker, important for how we select information to save
    # different versions refer to data differently

# Open .EDF file

et_tracker.openDataFile(edf_file)

# Configure the tracker
# Put the tracker in offline mode before changing the parameters

et_tracker.setOfflineMode()
pylink.pumpDelay(100)

et_tracker.sendCommand("sample_rate 1000") 
et_tracker.sendCommand("recording_parse_type = GAZE")
et_tracker.sendCommand("select_parser_configuration 0")
et_tracker.sendCommand("calibaration_type = HV9")
et_tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (1920-1, 1080-1)) # this needs to be modified to the Display PC screen size you are using
et_tracker.sendMessage("DISPLAY_COORDS 0 0 %d %d" % (1920-1, 1080-1)) # this needs to be modified to the Display PC screen size you are using

# events to store

file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'

# samples to store

if et_version > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
et_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
et_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
et_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
et_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Experiment starts
# We first perform the calibration and validation
# In this case, we are doing it without modifying the original set up (i.e., without customizing it)

if not dummy_mode:
    et_tracker.doTrackerSetup()

trial_index = 1
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
    
    # mark trial onset for the eye-tracker
    
    et_tracker.sendMessage('TRIALID %d' % trial_index) # TRIALID is the 'trigger' that DataViewer uses to segment trials
    
    # information to be shown in the host PC
    # in this case, we want to know what trial we are recording
    
    et_tracker.sendCommand("record_status_message TRIAL number '%d'" % trial_index)
    
    # every trial starts with a drift correction
    
    if not dummy_mode:
        et_tracker.doDriftCorrect(int(win_width/2), int(win_height/2), 1, 1)
    
    
    # start recording
    et_tracker.setOfflineMode()
    if not dummy_mode:
        et_tracker.startRecording(1, 1, 1, 1)
    
    # presentation of visual stimuli
    
    win.flip()
    print('show images')
    # send trigger that images have been sent
    et_tracker.sendMessage('image_onset')
    
    time.sleep(1) # preview window
    
    # tracking mouse clicks
    mouseIsDown = False
    instructionPlayed = False 
    targetPlayed = False
    audioFinished = False
    
    # loop for audio
    while True:
            if instructionPlayed == False:
                carrier_sound.play()
                # send trigger audio onset
                et_tracker.sendMessage('audio_onset')
                print("audio onset")
                clock.wait(carrier_sound.duration)
                carrier_sound.stop()
                instructionPlayed = True
            if instructionPlayed == True and targetPlayed == False:
                target_sound.play()
                # send trigger target onset
                et_tracker.sendMessage('target_onset')
                print("target onset")
                clock.wait(target_sound.duration)
                target_sound.stop()
                # send trigger target offset
                et_tracker.sendMessage('target_offset')
                print("target offset")
                targetPlayed = True
            if targetPlayed == True and audioFinished == False:
                mouse.setVisible(visible = True)
                if mouse.getPressed()[0] == 1 and mouseIsDown == False:
                    mouseIsDown = True
                if mouse.getPressed()[0] == 0 and mouseIsDown:
                    mouseIsDown = False
                    break
                    
    # log information about this trial in the EDF file
    
    et_tracker.sendMessage('!V TRIAL_VAR set type %s' % trial["set_type"])
    et_tracker.sendMessage('!V TRIAL_VAR target type %s' % trial["target_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O1 %s' % trial["O1"])
    et_tracker.sendMessage('!V TRIAL_VAR O1_pos %s %s' % positions[0])
    et_tracker.sendMessage('!V TRIAL_VAR O2 %s' % trial["O2"])
    et_tracker.sendMessage('!V TRIAL_VAR O2_pos %s %s' % positions[1])
    et_tracker.sendMessage('!V TRIAL_VAR O3 %s' % trial["O3"])
    et_tracker.sendMessage('!V TRIAL_VAR O3_pos %s %s' % positions[2])
    et_tracker.sendMessage('!V TRIAL_VAR O4 %s' % trial["O4"])
    et_tracker.sendMessage('!V TRIAL_VAR O4_pos %s %s' % positions[3])
    et_tracker.sendMessage('!V TRIAL_VAR O1 type %s' % trial["O1_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O2 type %s' % trial["O2_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O3 type %s' % trial["O3_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O4 type %s' % trial["O4_type"])
    
    # stop recording
    if not dummy_mode:
        pylink.pumpDelay(100)
        et_tracker.stopRecording()
        et_tracker.sendMessage("TRIAL_RESULT %d" % pylink.TRIAL_OK) # used by DataViewer to segment the data
    
    trial_index += 1

# End of experiment
# save EDF file and close connection with the Host PC

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    et_tracker.closeDataFile()
    et_tracker.receiveDataFile(edf_file, os.getcwd() + "/el_data/" + edf_file)
    et_tracker.close()