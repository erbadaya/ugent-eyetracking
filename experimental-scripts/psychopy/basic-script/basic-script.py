# Basic script eye-tracking
# Author: Esperanza Badaya
# 21/11/2023

# NB we have created a very simple experiment to illustrate the steps described in Chapter 11
# In this experiment, we are *not* covering regions of interest (see Visual World Paradigm example for this)
# We are sending minimal (and redundant triggers) to illustrate how it is done, but NB that these triggers are redundant
# because that information is already sent to the tracker by other means (namely, TRIALID)
# We are not going to cover here creating functions to wrap up sections (see DataViewer proposed ideas)
# We are not covering handling errors
# The bits of code pertaining the task itself are not commented (check the PsychoPy course to follow what's happening!)

# The task:
# Emotion detection: Say whether a face is happy or sad
# Participants are shown a face and press 'h' for happy or 's' for sad
# We are going to have 10 trials
# NB this design has many flaws (e.g., we are not controlling for a balanced presentation of stimuli). 

# Eye-tracking
## Start the experiment:
# We want to record at 1000 Hz
# We want a 5-point calibration & validation procedure
# We want to store all the events and sample data

## During the experiment
# We want every trial to start with a drift correction
# We want to see in the Host PC what trial number we are recording
# We want to start and stop the recording in every trial
# We want to send a trigger when images are shown
# We want to save the variable of emotion and the image presented

# Additionally, we are going to write this code so that we can try it on our machines
# without the need of the eye-tracker
# we will do that via the variable dummy_mode

# Last update: 28/08/2024

# Libraries

from psychopy import gui, visual, event, logging, data, core
import time, os, numpy

# eye-tracking libraries
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder

# Set up a a variable to run the script on a computer not connected to the tracker
# We will use this variable in a series of if-else statements everytime there would be a line of code calling the tracker
# We will change it to 'False' when running the experiment in the lab

dummy_mode = True

# Participant data

info = {"Participant number": "", "Eye-tracking file name":""}
wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Participant number'])
    edf_name = str(info['EDF_name']) # to obtain EDF file name, you could alternatively use ppt_number
    behavioural_file = 'behavioural/pp_' + ppt_number + '.txt'
    edf_file = edf_name + '.EDF' # remember to add the .edf extension
    if not os.path.isfile(behavioural_file):
        ppt_number_taken = False

# Set up the folder to save .edf files in the STIM PC
# All .edf are saved in the same folder

results_folder = 'et_results'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
local_edf = os.path.join(results_folder, edf_file) # we call this at the end to transfer .EDF from ET PC to STIM PC

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

# Load stimuli
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

ThisExp = data.ExperimentHandler(dataFileName = behavioural_file, extraInfo = info)
TrialList = data.importConditions('basicscript_conditions.xlsx') 
trials = data.TrialHandler(TrialList, nReps = 1, method = 'random') # we only want 10 trials, not 20
ThisExp.addLoop(trials)

# Define response keys

response_keys = ['s', 'h']

# Create screen
# You could then call win.size[0] and win.size[1] to get the width and height of the screen respectively and avoid typing it as is done in this example

win = visual.Window(fullscr = True, checkTiming=False, color = (0, 0, 0), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that
# more information on this issue here:
# https://discourse.psychopy.org/t/is-there-a-way-to-skip-frame-rate-measurement-on-each-initialisation/36232
# https://github.com/psychopy/psychopy/issues/5937

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

preamble_text = 'Basic Script in PsychoPy - Facial emotion detection' 
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
    et_tracker.doTrackerSetup()

# Communicate that the experiment is about to start

message("The experiment will start now. Press the spacebar to continue.")

# The experiment

trial_index = 0

for trial in trials:
    trial_index += 1
    
    # hide mouse
    
    mouse = event.Mouse(visible = False) 

    # Load the images to display

    image_stimuli = visual.ImageStim(win, image = trial["image"], pos = (0, 0), units = 'pix') # NB pos coordinates are in pixels: Required by the Graphics Environment, for all units, (0,0) is the center
    image_stimuli.size/=6 # rescale
    text_position_y = 0 - int(image_stimuli.size[1]/2) - int(50) 
    text_stimuli = visual.TextStim(win, text = "Press 's' if the face is sad, 'h' if the face is happy",
    pos = (0, text_position_y), color = "black", units = 'pix') 

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
        et_tracker.doDriftCorrect(int(1920/2), int(1080/2), 1, 1)

    # Start recording
    
    # put tracker in idle/offline mode before recording
    et_tracker.setOfflineMode()

    # Start recording
    # arguments: sample_to_file, events_to_file, sample_over_link,
    # event_over_link (1-yes, 0-no)
    if not dummy_mode:
        et_tracker.startRecording(1, 1, 1, 1)
    
    # Draw stimuli and wait for participants response
    # Mark in the .EDF file when images were shown (i.e., send a trigger)

    text_stimuli.draw()
    image_stimuli.draw()
    win.flip()
    
    # send trigger that images have been sent
    if not dummy_mode:
        et_tracker.sendMessage('image_onset')
    img_onset_time = core.getTime()  # record the image onset time
    
    # show the image for 5-secs or until a key is pressed
    
    event.clearEvents()  # clear cached PsychoPy events
    RT = -1  # keep track of the response time
    get_keypress = False
    
    while not get_keypress:
        # present the picture for a maximum of 5 seconds
        if core.getTime() - img_onset_time >= 5.0:
            et_tracker.sendMessage('time_out')
            break
        # check keyboard events
        for keycode, modifier in event.getKeys(modifiers=True):
            # Stop stimulus presentation when the spacebar is pressed
            if keycode == 'h' or keycode == 's':
                # send over a message to log the key press
                et_tracker.sendMessage('key_pressed')
                # get response time in ms, PsychoPy report time in sec
                RT = int((core.getTime() - img_onset_time)*1000)
                get_keypress = True
                
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
    et_tracker.sendMessage('!V TRIAL_VAR image %s' % trial["image"])
    et_tracker.sendMessage('!V TRIAL_VAR emotion %s' % trial["emotion"])

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
