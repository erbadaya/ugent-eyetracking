# Basic script for a Visual World Paradigm eye-tracking experiment
# Author: Esperanza Badaya
# 29/11/2023

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

# Last update: 27/08/2024

# Libraries

from psychopy import gui, visual, event, logging, data, sound, clock, core
import time, os, numpy

from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb'] # ptb library has by far the lowest latencies

# eye-tracking libraries
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder & sounds

# Set up a a variable to run the script on a computer not connected to the tracker
# We will use this variable in a series of if-else statements everytime there would be a line of code calling the tracker
# We will change it to 'False' when running the experiment in the lab

dummy_mode = True

# Get participant data

info = {"Participant number": "", "EDF_name":""}
wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Participant number'])
    edf_name = str(info['EDF_name']) # to obtain EDF file name, you could alternatively use ppt_number
    behavioural_file = '/subject_' + ppt_number + '.txt'
    edf_file = edf_name + '.EDF' # remember to add the .edf extension
    if not os.path.isfile(behavioural_file):
        ppt_number_taken = False

# Set up the folder to save .edf files in the STIM PC

results_folder = 'et_results'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
local_edf = os.path.join(results_folder, edf_file) # we call this at the end to transfer .EDF from ET PC to STIM PC

# To communicate with participants

def message(message_text = "", response_key = "space", duration = 0, height = None, pos = (0.0, 0.0), color = "black"):
    message_on_screen = visual.TextStim(win, text = "OK")
    message_on_screen.text    = message_text
    message_on_screen.height  = height
    message_on_screen.pos     = pos
    message_on_screen.color   = color
    
    message_on_screen.draw()
    win.flip()
    if duration == 0: # for the welcome and goodbye
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration) # for the feedback

# stimuli
# in this case, we have a .xlsx file (os_conditions.xlsx) that has the combination of stimuli + information about conditions
# load it in
# materials (audios and images) are stored in the materials folder
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

trial_list = data.importConditions('os_conditions.xlsx') 
trials = data.TrialHandler(trial_list, nReps = 1, method = 'random')
ThisExp = data.ExperimentHandler(dataFileName = behavioural_file, extraInfo = info)
ThisExp.addLoop(trials)

# Create screen
# You could then call win.size[0] and win.size[1] to get the width and height of the screen respectively and avoid typing it as is done in this example
# In this case, we are setting the background color to white

win = visual.Window(fullscr = True, checkTiming=False, color = (1, 1, 1), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that

# more information on this issue here:
# https://discourse.psychopy.org/t/is-there-a-way-to-skip-frame-rate-measurement-on-each-initialisation/36232
# https://github.com/psychopy/psychopy/issues/5937

win_width = win.size[0]
win_height = win.size[1]

# Start of the experiment
# 1. Open the connection to the ET PC

if dummy_mode:
    et_tracker = pylink.EyeLink(None)
    et_version = 0  # set version to 0, in case running in Dummy mode
else:
    try: # at the end of the eye-tracking section (before we move onto ioHub, there is a brief discussion on this try-except statements)
        et_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        dlg = gui.Dlg("Dummy Mode?")
        dlg.addText("Couldn't connect to tracker at 100.1.1.1 -- continue in Dummy Mode?")
        #dlg.addField('File Name:', edf_fname)
        # show dialog and wait for OK or Cancel
        ok_data = dlg.show()
        if dlg.OK:  # if ok_data is not None
            #print('EDF data filename: {}'.format(ok_data[0]))
            dummy_mode = True
            et_tracker = pylink.EyeLink(None)
        else:
            print('user cancelled')
            core.quit()
            sys.exit()

# 2. Open the .EDF file

if not dummy_mode:
    et_tracker.openDataFile(edf_file)

# Add preamble (optional)

preamble_text = 'VWP with pylink' 
et_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# 3. Configure the tracker

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    
    et_tracker.sendCommand("sample_rate 1000") 
    et_tracker.sendCommand("recording_parse_type = GAZE")
    et_tracker.sendCommand("select_parser_configuration 0")
    et_tracker.sendCommand("calibration_type = HV5")
    et_tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (1920-1, 1080-1)) # this needs to be modified to the Display PC screen size you are using
    et_tracker.sendMessage("DISPLAY_COORDS 0 0 %d %d" % (1920-1, 1080-1)) # this needs to be modified to the Display PC screen size you are using
    
    # get the tracker version to see what data can be stored
    
    vstr = et_tracker.getTrackerVersionString()
    et_version = int(vstr.split()[-1].split('.')[0])
    
    # what events to store
    
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

# 4. Calibration and validation

# In this example, we are customising the calibration and validation
# We are setting the background to white, to match our stimuli and the background of the experiment in general

message("The calibration will now start. If you double press 'Enter', you can see the camera, or 'c' to start calibrating afterwards.")

if not dummy_mode:
    genv = EyeLinkCoreGraphicsPsychoPy(et_tracker, win) # we are using openGraphicsEx(), cf. manual openGraphics versus this.
    foreground_color = (-1, -1, -1)
    background_color = win.color
    genv.setCalibrationColors(foreground_color, background_color)
    pylink.openGraphicsEx(genv)
    et_tracker.doTrackerSetup()

# The experiment

message("The experiment will start now. Press the spacebar to continue.")

trial_index = 0
for trial in trials:
    
    trial_index += 1

    # Load stimuli

    # presentation of visual stimuli
        
    img_width = 189
    img_height = 189
    
    # positions
    # because of EyeLinkCoreGraphicsPsychoPy, this needs to be in _pixels_
    
    y_displacement = int((win_height/2)/2) # half of the screen is the top (+) and the bottom (-), since 0 is the center. we want the image to be presented in the middle of the top and the bottom half
    x_displacement = int((win_width/2)/2)
    
    positions = [[0, 0 + y_displacement], [0 +  x_displacement, 0], [0, 0 - y_displacement], [0 - x_displacement , 0]] # NB you could also have this in your conditions file! It's just here for illustrative purposes
    numpy.random.shuffle(positions)
    
    # images
    
    image_O1 = visual.ImageStim(win, image = 'materials/images/' + trial["O1"], pos = positions[0], units = 'pix')
    print(image_O1.pos)
    image_O2 = visual.ImageStim(win, image = 'materials/images/' + trial["O2"], pos = positions[1], units = 'pix')
    image_O3 = visual.ImageStim(win, image = 'materials/images/' + trial["O3"], pos = positions[2], units = 'pix')
    image_O4 = visual.ImageStim(win, image = 'materials/images/' + trial["O4"], pos = positions[3], units = 'pix')
    
    #sound
    # to send triggers for target onset, instead of measuring at what precise time it happens in an audio
    # we have cut the audio in two, so the trigger is sent when the second audio (i.e., the target) is played
    
    carrier_sound = sound.Sound('materials/audios/' + trial["instruction_audio"],
                                      stereo = True)
    target_sound = sound.Sound('materials/audios/' + trial["target_audio"],
                                      stereo = True)


    # Mark the beginning of the trial
    # Send message to the .EDF file (for later data segmentation) and to the ET PC for us
    
    et_tracker.sendMessage('TRIALID %d' % trial_index)
    
    # record_status_message : show some info on the ET PC
    # here we show how many trial has been tested
    # you could put condition, stimuli, etc. whatever is informative for you
    status_msg = 'TRIAL number %d' % trial_index
    et_tracker.sendCommand("record_status_message '%s'" % status_msg)
    
    # Perform drift correction (drift check)
    if not dummy_mode:
        et_tracker.doDriftCorrect(int(win_width/2), int(win_height/2), 1, 1)
        
    # Start recording
    # arguments: sample_to_file, events_to_file, sample_over_link,
    # event_over_link (1-yes, 0-no)
    if not dummy_mode:
        et_tracker.startRecording(1, 1, 1, 1)

    # Draw stimuli

    image_O1.draw()
    image_O2.draw()
    image_O3.draw()
    image_O4.draw()
    
    mouse = event.Mouse(visible = False, newPos = (0,0)) # hide the mouse during preview window + audio
    
    win.flip()
    print('show images')
    # send trigger that images have been sent
    et_tracker.sendMessage('image_onset')
        
    core.wait(2) # preview window
    
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
                clock.wait(carrier_sound.getDuration() )
                carrier_sound.stop()
                instructionPlayed = True
            if instructionPlayed == True and targetPlayed == False:
                target_sound.play()
                # send trigger target onset
                et_tracker.sendMessage('target_onset')
                print("target onset")
                clock.wait(target_sound.getDuration())
                target_sound.stop()
                # send trigger target offset
                et_tracker.sendMessage('target_offset')
                print("target offset")
                targetPlayed = True
                mouse = event.Mouse(visible = False, newPos = (0,0)) 
            if targetPlayed == True and audioFinished == False:
                mouse.setVisible(visible = True)
                if mouse.getPressed()[0] == 1 and mouseIsDown == False:
                    mouseIsDown = True
                    mouse = event.Mouse(visible = False, newPos = (0,0)) 
                if mouse.getPressed()[0] == 0 and mouseIsDown:
                    mouseIsDown = False
                    mouse = event.Mouse(visible = False, newPos = (0,0)) 
                    break
                        
    # log information about areas of interest
    # in DataViewer, coordinates start at the top, left corner (i.e., 0,0)
    # RECTANGLE <id> <left> <top> <right> <bottom> [label]
    # we need to know the size of the images and the size of the screen
    
    if not dummy_mode:
        et_tracker.sendMessage('!V IAREA RECTANGLE %d %d %d %d %d %s' % (1, int(positions[0][0]) + int(win_width/2) - int(img_width/2), int(positions[0][1]) + int(win_height/2) - int(img_height/2), int(positions[0][0]) + int(win_width/2) +int(img_width/2), int(positions[0][1]) + int(win_height/2) + int(img_height/2), trial["O1_type"]))
        et_tracker.sendMessage('!V IAREA RECTANGLE %d %d %d %d %d %s' % (2, int(positions[1][0]) + int(win_width/2) - int(img_width/2), int(positions[1][1]) + int(win_height/2) - int(img_height/2), int(positions[1][0]) + int(win_width/2) +int(img_width/2), int(positions[1][1]) + int(win_height/2) + int(img_height/2), trial["O2_type"]))
        et_tracker.sendMessage('!V IAREA RECTANGLE %d %d %d %d %d %s' % (3, int(positions[2][0]) + int(win_width/2) - int(img_width/2), int(positions[2][1]) + int(win_height/2) - int(img_height/2), int(positions[2][0]) + int(win_width/2) +int(img_width/2), int(positions[2][1]) + int(win_height/2) + int(img_height/2), trial["O3_type"]))
        et_tracker.sendMessage('!V IAREA RECTANGLE %d %d %d %d %d %s' % (4, int(positions[3][0]) + int(win_width/2) - int(img_width/2), int(positions[3][1]) + int(win_height/2) - int(img_height/2), int(positions[3][0]) + int(win_width/2) +int(img_width/2), int(positions[3][1]) + int(win_height/2)  + int(img_height/2), trial["O4_type"]))
            
            
    # we also want to send the actual images presented to DataViewer
    # (just for the sake of it)
    
    if not dummy_mode:
        screenshot = str(trial_index)+'.png'
        scn_shot = os.path.join(results_folder, screenshot)
        win.getMovieFrame()
        win.saveMovieFrames(scn_shot)
        et_tracker.sendMessage('!V IMGLOAD FILL %s' % screenshot)
    
    # stop recording, save information about the trial & mark trial end in the .EDF file
    
    # clear the screen
    # send a message to clear the Data Viewer screen as well
    et_tracker.sendMessage('!V CLEAR 128 128 128')

    # stop recording; add 100 msec to catch final events before stopping
    pylink.pumpDelay(100)
    et_tracker.stopRecording()

    # log information about this trial in the EDF file
        
    et_tracker.sendMessage('!V TRIAL_VAR set type %s' % trial["set_type"])
    et_tracker.sendMessage('!V TRIAL_VAR target type %s' % trial["target_type"])
    pylink.pumpDelay(50) # adding a break to the et so we don't lose messages
    et_tracker.sendMessage('!V TRIAL_VAR O1 type %s' % trial["O1_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O2 type %s' % trial["O2_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O3 type %s' % trial["O3_type"])
    et_tracker.sendMessage('!V TRIAL_VAR O4 type %s' % trial["O4_type"])
        
    # send a 'TRIAL_RESULT' message to mark the end of trial, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    et_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)
    
    ThisExp.nextEntry()

# End of experiment

# We need to close the data file, transfer it from ET PC to STIM PC and then close the connection between both PCs (plus exist PsychoPy)

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    et_tracker.closeDataFile() # close the file
    pylink.pumpDelay(500)
    et_tracker.receiveDataFile(edf_file, local_edf) # transfer the file
    et_tracker.close() # close the link

# Close & quit PsychoPy

win.close()
core.quit()
sys.exit()