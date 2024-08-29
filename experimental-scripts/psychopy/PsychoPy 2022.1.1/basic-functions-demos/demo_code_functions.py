# Basic commands for eye-tracking in PsychoPy using pylink
# Author: Esperanza Badaya
# 26/08/2024

# This script illustrates all the steps discussed in Chapter 10, eye-tracking section 10.4.1
# There is no experimental task in this script
# The objective is to see the sequence in which commands are sent to the tracker

# Last updated: 28/08/2024

# Before the experiment
# Load libraryes

import pylink
import os # for path creation
from psychopy import gui, visual, event, logging, data, core
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # for calibration and validation 

# Set up a a variable to run the script on a computer not connected to the tracker
# We will use this variable in a series of if-else statements everytime there would be a line of code calling the tracker
# We will change it to 'False' when running the experiment in the lab

dummy_mode = False

# Get participant data

info = {"Participant number": "", "Eye-tracking file name":""}
wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Participant number'])
    edf_name = str(info['Eye-tracking file name']) # to obtain EDF file name, you could alternatively use ppt_number
    behavioural_file = 'behavioural/pp_' + ppt_number + '.txt'
    edf_file = edf_name + '.EDF' # remember to add the .edf extension
    if not os.path.isfile(behavioural_file):
        ppt_number_taken = False
        
# Set up the folder to save .edf files in the STIM PC

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

preamble_text = 'Demo code_Basics of ET with pylink' 
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

message("The calibration will now start. Press the space bar to start. If you double press 'Enter', you can see the camera on the STIM PC, or 'c' to start calibrating afterwards.")

# In this example, we are not customising the calibration and validation

if not dummy_mode:
    genv = EyeLinkCoreGraphicsPsychoPy(et_tracker, win) # we are using openGraphicsEx(), cf. manual openGraphics versus this.
    pylink.openGraphicsEx(genv)
    try:
        et_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        et_tracker.exitCalibration()
    
# The experiment

# As there is no experimental task in this demo code, we are just going to iterate through a loop 6 times (~ 6 trials)
# Where every trial starts with a drift check

# Create trial_index to keep track of where in the loop we are

trial_index = 0

for i in range(6):
    
    trial_index += 1
    
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
            error = et_tracker.doDriftCorrect(int(1920/2.0),
                                              int(1080/2.0), 1, 1)
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
            keypress = True
        for keycode, modifier in event.getKeys(modifiers=True):
            if keycode == 'escape': # for skipping a trial
                et_tracker.sendMessage('trial_skipped')
                skip_trial()
                # End the while loop
                keypress = True
            if keycode == "c" and (modifier['ctrl'] is True): # for terminating experiment
                et_tracker.sendMessage('experiment_aborted')
                abort_exp()
    
    # End of trial
    
    if not dummy_mode:
        et_tracker.sendMessage('!V CLEAR 128 128 128')
        pylink.pumpDelay(100) # give some time to catch everything
        et_tracker.stopRecording() # stop recording
        et_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK) # mark the end of the trial

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

    
    
    
