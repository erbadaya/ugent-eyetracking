"""
Basic reading script
Author: Esperanza Badaya
01/12/2023


Basic script for a reading eye-tracking experiment
We are not going to cover here creating functions to wrap up sections (see DataViewer proposed ideas)
We are not covering handling errors
We are not covering reading in itself (e.g., why 13 and not 5 points for calibration, for example). The idea with this script is to explore how to create smaller and dynamic areas of interest (what can happen outside of reading research)
The bits of code pertaining the task itself are not commented (check the PsychoPy course to follow what's happening!)

Objectives of this script:
Illustrate how to define & send ROIs to the tracker
Similar to VWP, but with the difference that ROIs are smaller (and change per trial)
Review of eye-tracking experiment in PsychoPy with Pylink (see basic-script.py for the basic template with a mock experiment)

The task
We have made slight modifications (e.g., fewer items, no counterbalancing)
Stimuli consist of sentences with 5 regions (marked as IA_in the .xlsl file)
Participants are asked to read them silently
They move through the experiment by pressing the spacebar once they have finished reading the sentence

Eye-tracking
Start the experiment:
We want to record at 1000 Hz
We want a 13-point calibration & validation procedure
We want to store all the events and sample data

During the experiment
We want every trial to start with a drift correction
Drift correction needs to occur at the left side of the screen (because English is read left-to-right)
We want to see in the Host PC what trial number we are recording
We want to start and stop the recording in every trial
We want to send a trigger when the sentence is shown
We want to save 5 ROIs (one per segment of the sentence)
NB ROI size changes in each trial, because of character length
Some discussion of how this will be implemented can be found here:
https://discourse.psychopy.org/t/extract-location-of-words-after-presenting-sentence-on-screen/3974/12
https://discourse.psychopy.org/t/position-of-stimuli/2483/4
Log information of sentence shown and condition.

Additionally, we are going to write this code so that we can try it on our machines
without the need of the eye-tracker
we will do that via the variable dummy_mode

Last update: 28/08/2024
"""
# Libraries

from psychopy import gui, visual, event, logging, data, core
import time, os, numpy

# eye-tracking libraries
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder

# Set up a a variable to run the script on a computer not connected to the tracker
# We will use this variable in a series of if-else statements everytime there would be a line of code calling the tracker
# We will change it to 'False' when running the experiment in the lab

dummy_mode = False

# Participant data

info = {"Participant number": "", "Eye-tracking file name":""}
wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Eye-tracking file name'])
    behavioural_file = 'behavioural/pp_' + ppt_number + '.txt'
    edf_file = ppt_number + '.EDF' # remember to add the .edf extension
    if not os.path.isfile(behavioural_file):
        ppt_number_taken = False

# To communicate with participants

def message(message_text = "", response_key = "space", duration = 0, height = None, pos = (0, 0), color = "black"):
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

# Set up the folder to save .edf files in the STIM PC

results_folder = 'et_results/pp_' + str(info['Participant number'])
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
local_edf = os.path.join(results_folder, edf_file) # we call this at the end to transfer .EDF from ET PC to STIM PC

# stimuli
# in this case, we have a .xlsx file (reading-psychopy).xlsx) that has the combination of stimuli + information about conditions
# load it in
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

ThisExp = data.ExperimentHandler(dataFileName = behavioural_file, extraInfo = info)
TrialList = data.importConditions('reading-psychopy.xlsx') 
trials = data.TrialHandler(TrialList, nReps = 1, method = 'random')
ThisExp.addLoop(trials)

# Create screen
# You could then call win.size[0] and win.size[1] to get the width and height of the screen respectively and avoid typing it as is done in this example

win = visual.Window(fullscr = True, checkTiming=False, color = (0, 0, 0), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that
# more information on this issue here:
# https://discourse.psychopy.org/t/is-there-a-way-to-skip-frame-rate-measurement-on-each-initialisation/36232
# https://github.com/psychopy/psychopy/issues/5937

win_width = win.size[0]
win_height = win.size[1]

# Define functions for catching errors

def skip_trial():
    """Ends recording """
    
    et_tracker = pylink.getEYELINK()
    # Stop recording
    if et_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        et_tracker.stopRecording()
    # Clean the screen
    win.flip()
    # send a message to mark trial end
    et_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)
    return pylink.TRIAL_ERROR

def abort_exp():
    """ Terminate the task gracefully and retrieve the EDF data file
    
    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """
    
    et_tracker = pylink.getEYELINK()

    if et_tracker.isConnected():
        error = et_tracker.isRecording()
        if error == pylink.TRIAL_OK:
            skip_trial() 

        # Put tracker in Offline mode
        et_tracker.setOfflineMode()

        # Clear the Host PC screen and wait for 500 ms
        et_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)

        # Close the edf data file on the Host
        et_tracker.closeDataFile()
        try:
            et_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        et_tracker.close()

    # close the PsychoPy window
    win.close()
    core.quit()
    sys.exit()

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
    try:
        et_tracker.openDataFile(edf_file)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if et_tracker.isConnected():
            et_tracker.close()
        core.quit()
        sys.exit()

# Add preamble (optional)

preamble_text = 'Basic Reading experiment in PsychoPy' 
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

# In this example, we are not customising the calibration and validation

message("The calibration will now start. Press the space bar to start. If you double press 'Enter', you can see the camera on the STIM PC, or 'c' to start calibrating afterwards.")

if not dummy_mode:
    genv = EyeLinkCoreGraphicsPsychoPy(et_tracker, win) # we are using openGraphicsEx(), cf. manual openGraphics versus this.
    pylink.openGraphicsEx(genv)
    try:
        et_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        et_tracker.exitCalibration()

# Communicate that the experiment is about to start

message("The experiment will start now. Press the spacebar to continue.")

# The experiment

trial_index = 0

for trial in trials:
    
    trial_index += 1

    # load the stimuli
    # in this experiment, we have five areas of interest
    # we are going to use the TextStim to present stimuli and boundingBox to get the width in pixels of each IA.ab
    # note that in our .csv, there is a space at the end of each part of the sentence
    # otherwise, text will overlap
    # that way we can determine the width of our areas of interest
    # the height should be the font size (in pixels) + some pixels for margin

    ### PARAMETERS TO SET YOURSELF
    ### WHERE TEXT STARTS (x coordinate, here set to 200 from the start of the left side), NB THIS IS ALSO WHERE THE DRIFT CORRECTION IS SHOWN
    ## FONT SIZE 
    ## AMOUNT OF SPACE UP AND DOWN FOR AREAS OF INTEREST
    
    x_pos_start = -int(win_width/2) + 200
    
    IA_1 = visual.TextStim(win, text = trial["IA_1"], units = 'pix', pos = (x_pos_start, 0), alignText = 'left', anchorHoriz = 'left')
    IA_1_size = IA_1.boundingBox
    print(IA_1_size)
    IA_2_posx = int(x_pos_start + int(IA_1_size[0]))
    IA_2 = visual.TextStim(win, text = trial["IA_2"], units = 'pix', pos = (IA_2_posx, 0), alignText = 'left', anchorHoriz = 'left')
    IA_2_size = IA_2.boundingBox
    IA_3_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]))
    IA_3 = visual.TextStim(win, text = trial["IA_3"], units = 'pix', pos = (IA_3_posx, 0), alignText = 'left', anchorHoriz = 'left')
    IA_3_size = IA_3.boundingBox
    print(IA_3_posx)
    print(IA_3.pos[0])
    IA_4_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]) + int(IA_3_size[0]))
    IA_4 = visual.TextStim(win, text = trial["IA_4"], units = 'pix', pos = (IA_4_posx, 0), alignText = 'left', anchorHoriz = 'left')
    IA_4_size = IA_4.boundingBox
    IA_5_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]) + int(IA_3_size[0]) + int(IA_4_size[0]))
    IA_5 = visual.TextStim(win, text = trial["IA_5"], units = 'pix', pos = (IA_5_posx, 0), alignText = 'left', anchorHoriz = 'left')
    IA_5_size = IA_5.boundingBox

    # Mark the beginning of the trial
    # Send message to the .EDF file (for later data segmentation) and to the ET PC for us
    
    et_tracker.sendMessage('TRIALID %d' % trial_index)
    
    # record_status_message : show some info on the ET PC
    # here we show how many trial has been tested
    # you could put condition, stimuli, etc. whatever is informative for you
    
    status_msg = 'TRIAL number %d' % trial_index
    et_tracker.sendCommand("record_status_message '%s'" % status_msg)
    
    # Perform drift correction (drift check)
    
    while not dummy_mode:
        if (not et_tracker.isConnected()) or et_tracker.breakPressed():
            abort_exp()
        try:
            error = et_tracker.doDriftCorrect(200, int(win_height/2), 1, 1)
            # break following a success drift-check
            if error is not pylink.ESC_KEY:
                break
        except:
            pass
    
    # Start recording
    
    # put tracker in idle/offline mode before recording
    et_tracker.setOfflineMode()

    # Start recording
    # arguments: sample_to_file, events_to_file, sample_over_link,
    # event_over_link (1-yes, 0-no)
    if not dummy_mode:
        try:
            et_tracker.startRecording(1, 1, 1, 1)
        except RuntimeError as error:
            print("ERROR:", error)
            skip_trial()
            
    # Draw stimuli
    
    IA_1.draw()
    IA_2.draw()
    IA_3.draw()
    IA_4.draw()
    IA_5.draw()
    win.flip()
    
    # Wait two seconds to test the abort & skip trial functions
    
    keypress = False
    timeout = core.getTime()
    while not keypress:
        if core.getTime() - timeout >= 2.0:
            break
        error = et_tracker.isRecording()
        if error is not pylink.TRIAL_OK:
            et_tracker.sendMessage('tracker_disconnected')
            skip_trial()
            # End the while loop
            keypress = True
        for keycode, modifier in event.getKeys(modifiers=True):
            if keycode == 'escape': # for skipping a trial
                et_tracker.sendMessage('trial_skipped')
                skip_trial()
                keypress = True
            if keycode == 'c' and (modifier['ctrl'] is True): # for terminating experiment
                et_tracker.sendMessage('experiment_aborted')
                abort_exp()
    
    ## SEND AREAS OF INTEREST 
    
    # in DataViewer, coordinates start at the top, left corner (i.e., 0,0)
    # RECTANGLE <id> <left> <top> <right> <bottom> [label]
    # we need to know the size of the images and the size of the screen
    
    ## NOTE: YOU WILL HAVE TO ADD MORE/REMOVE DEPENDING ON HOW MANY ROIS YOUR EXPERIMENT HAS
    ## NOTE: Adapt variable 'y_displacement' for adding margings to ROIs for text
    
    y_displacement = 10
    
    if not dummy_mode:
        et_tracker.sendMessage("!V IAREA RECTANGLE %d %d %d %d %d %s" % (1, 200, -IA_1_size[1]/2 + int(win_height/2) - y_displacement, 200 + IA_1_size[0], IA_1_size[1]/2 + int(win_height/2) + y_displacement, "IA1"))
        et_tracker.sendMessage("!V IAREA RECTANGLE %d %d %d %d %d %s" % (2, 200 + IA_1_size[0] , -IA_2_size[1]/2 + int(win_height/2) - y_displacement, 200 + IA_1_size[0] + IA_2_size[0], IA_2_size[1]/2 + int(win_height/2) + y_displacement, "IA2"))
        et_tracker.sendMessage("!V IAREA RECTANGLE %d %d %d %d %d %s" % (3, 200 + IA_1_size[0] + IA_2_size[0], -IA_3_size[1]/2 + int(win_height/2) - y_displacement, 200 + IA_1_size[0] + IA_2_size[0] + IA_3_size[0], IA_3_size[1]/2 + int(win_height/2) + y_displacement, "IA3"))
        et_tracker.sendMessage("!V IAREA RECTANGLE %d %d %d %d %d %s" % (4, 200 + IA_1_size[0] + IA_2_size[0] + IA_3_size[0], -IA_4_size[1]/2 + int(win_height/2) - y_displacement, 200 + IA_1_size[0] + IA_2_size[0] + IA_3_size[0] + IA_4_size[0], IA_4_size[1]/2 + int(win_height/2) + y_displacement, "IA4"))
        et_tracker.sendMessage("!V IAREA RECTANGLE %d %d %d %d %d %s" % (5, 200 + IA_1_size[0] + IA_2_size[0] + IA_3_size[0] + IA_4_size[0], -IA_5_size[1]/2 + int(win_height/2) - y_displacement, 200 + IA_1_size[0] + IA_2_size[0] + IA_3_size[0] + IA_4_size[0] + IA_5_size[0], IA_5_size[1]/2 + int(win_height/2) + y_displacement, "IA5"))
    
    ## SEND TEXT TO TRACKER & FOR DATA ANALYSIS IN DATAVIEWER
    
    # imageBackdrop() uses the PIL module, works with all versions of EyeLink Host PC
    # bitmapBackdrop() works with EyeLInk 1000 + and Portabele duo only & EyeLink Developers Kit 2.0 and up
    # using the latter
    
    
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
    # in this case, what specific stimuli was shown
    # and the emotion shown

    ## SEND TRIAL-SPECIFIC INFORMATION
    ## Note: you need to adapt this to the specifics of your experiment
    
    if not dummy_mode:
        et_tracker.sendMessage('!V TRIAL_VAR IA_1 %s' % trial["IA_1"])
        et_tracker.sendMessage('!V TRIAL_VAR IA_2 %s' % trial["IA_2"])
        et_tracker.sendMessage('!V TRIAL_VAR IA_3 %s' % trial["IA_3"])
        et_tracker.sendMessage('!V TRIAL_VAR IA_4 %s' % trial["IA_4"])
        pylink.pumpDelay(50) # adding a break to the et so we don't lose messages
        et_tracker.sendMessage('!V TRIAL_VAR IA_5 %s' % trial["IA_5"])
        et_tracker.sendMessage('!V TRIAL_VAR item %s' % trial["item"])
        et_tracker.sendMessage('!V TRIAL_VAR condition %s' % trial["condition"])
        et_tracker.sendMessage('!V TRIAL_VAR counterbalance %s' % trial["counterbalance"])
        pylink.pumpDelay(50) # adding a break to the et so we don't lose messages
        et_tracker.sendMessage('!V TRIAL_VAR type %s' % trial["type"])        
        et_tracker.sendMessage('!V TRIAL_VAR identifier %s' % trial["identifier"])
    
    # send a 'TRIAL_RESULT' message to mark the end of trial, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    et_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)

    # Next trial
    
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

message("That's the end of the experiment. Press the spacebar to exit.")

win.close()
core.quit()
sys.exit()
