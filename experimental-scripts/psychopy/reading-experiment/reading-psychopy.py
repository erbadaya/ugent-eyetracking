# Basic script for a reading eye-tracking experiment
# We are not going to cover here creating functions to wrap up sections (see DataViewer proposed ideas)
# We are not covering handling errors
# We are not covering reading in itself (e.g., why 13 and not 5 points for calibration, for example). The idea with this script is to explore how to create smaller and dynamic areas of interest (what can happen outside of reading research)
# The bits of code pertaining the task itself are not commented (check the PsychoPy course to follow what's happening!)

# Objectives of this script:
# Illustrate how to define & send ROIs to the tracker
# Similar to VWP, but with the difference that ROIs are smaller (and change per trial)
# Review of eye-tracking experiment in PsychoPy with Pylink (see basic-script.py for the basic template with a mock experiment)

# The task
# This task is a short replication of one of Mariia Baltais' thesis experiments
# We have made slight modifications (e.g., fewer items, no counterbalancing)
# Stimuli consist of sentences with 5 regions (marked as IA_# in the .xlsl file)
# Participants are asked to read them silently
# They move through the experiment by pressing the spacebar once they have finished reading the sentence

# Eye-tracking
## Start the experiment:
# We want to record at 1000 Hz
# We want a 13-point calibration & validation procedure
# We want to store all the events and sample data

## During the experiment
# We want every trial to start with a drift correction
# Drift correction needs to occur at the left side of the screen (because Spanish is read left-to-right)
# We want to see in the Host PC what trial number we are recording
# We want to start and stop the recording in every trial
# We want to send a trigger when the sentence is shown
# We want to save 5 ROIs (one per segment of the sentence)
# NB ROI size changes in each trial, because of character length
# Some discussion of how this will be implemented can be found here:
# https://discourse.psychopy.org/t/extract-location-of-words-after-presenting-sentence-on-screen/3974/12
# https://discourse.psychopy.org/t/position-of-stimuli/2483/4
# Log information of sentence shown and condition.

# Additionally, we are going to write this code so that we can try it on our machines
# without the need of the eye-tracker
# we will do that via the variable dummy_mode

# Libraries

from psychopy import gui, visual, event, logging, data, core
import time, os, numpy

# eye-tracking libraries
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder

# Participant data

info = {"Participant number":0, "EDF_name":""}
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

# Screen size


win = visual.Window(fullscr = True, checkTiming=False, color = (0, 0, 0), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that
# more information on this issue here:
# https://discourse.psychopy.org/t/is-there-a-way-to-skip-frame-rate-measurement-on-each-initialisation/36232
# https://github.com/psychopy/psychopy/issues/5937

win_width = win.size[0]
win_height = win.size[1]


# stimuli
# in this case, we have a .xlsx file (os_conditions.xlsx) that has the combination of stimuli + information about conditions
# load it in
# materials (audios and images) are stored in the materials folder
# check section 7.3 to follow this bit of code
# https://docs.google.com/document/d/1bKIGYGZBmMxaqWgj31S55b8RhHIy8kqqMStaU7Ku7Vg/edit

ThisExp = data.ExperimentHandler(dataFileName = 'test.csv', extraInfo = info)
TrialList = data.importConditions('reading-psychopy.xlsx') 
trials = data.TrialHandler(TrialList, nReps = 1, method = 'random')
ThisExp.addLoop(trials)

# Open connection to the Host PC
# Here we create dummy_mode

dummy_mode = True # assuming we are piloting in our machine, set to False when using the tracker

if dummy_mode:
    et_tracker = pylink.EyeLink(None)
    et_version = 0  # set version to 0, in case running in Dummy mode
else:
    try:
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
            
if not dummy_mode:
    vstr = et_tracker.getTrackerVersionString()
    et_version = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, et_version))

# To save .edf files

results_folder = 'et_results'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
local_edf = os.path.join(results_folder, edf_file) # we call this at the end to transfer .EDF from Host to Presentation PC

# Open .EDF file

if not dummy_mode:
    et_tracker.openDataFile(edf_file)

# Configure the tracker
# Put the tracker in offline mode before changing the parameters

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    
    et_tracker.sendCommand("sample_rate 1000") 
    et_tracker.sendCommand("recording_parse_type = GAZE")
    et_tracker.sendCommand("select_parser_configuration 0")
    et_tracker.sendCommand("calibration_type = HV5")
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

message("The calibration will now start. If you double press 'Enter', you can see the camera, or 'c' to start calibrating afterwards.")

#test = visual.TextBox2(win, borderColor = "black", size = [None, 12], text = "This is a test of the Text Box function", color = "black", units = 'pix')
#test2 = visual.TextBox2(win, borderColor = "white", size = [None, 12], text = "This is the second line", color = "black", units = 'pix')
#test.draw()
#print(test.size)
#print(test.pos)
#test_dot = visual.TextStim(win, text = "+", pos = (0,0), units = 'pix')
#win.flip()
#test_dot.draw()
#win.flip()
#test_dot.boundingBox
#core.wait(1)

if not dummy_mode:
    genv = EyeLinkCoreGraphicsPsychoPy(et_tracker, win) # we are using openGraphicsEx(), cf. manual openGraphics versus this.
    pylink.openGraphicsEx(genv)
    et_tracker.doTrackerSetup()


trial_index = 0

for trial in trials:
    
    trial_index += 1
    print(trial_index)
    
    # load the stimuli
    # in this experiment, we have five areas of interest
    # we are going to use the TextStim to present stimuli and boundingBox to get the width in pixels of each IA.ab
    # note that in our .csv, there is a space at the end of each part of the sentence
    # otherwise, text will overlap
    # that way we can determine the width of our areas of interest
    # the height should be the font size (in pixels) + some pixels for margin

    ### PARAMETERS TO SET YOURSELF
    ### WHERE TEXT STARTS (x coordinate, here set to -200), NB THIS IS ALSO WHERE THE DRIFT CORRECTION IS SHOWN
    ## FONT SIZE 
    ## AMOUNT OF SPACE UP AND DOWN FOR AREAS OF INTEREST
    
    x_pos_start = -200
        
    IA_1 = visual.TextStim(win, text = trial["IA_1"], units = 'pix', pos = (x_pos_start, 0), alignText = 'left')
    IA_1_size = IA_1.boundingBox
    IA_2_posx = int(x_pos_start + int(IA_1_size[0]))
    IA_2 = visual.TextStim(win, text = trial["IA_2"], units = 'pix', pos = (IA_2_posx, 0), alignText = 'left')
    IA_2_size = IA_2.boundingBox
    IA_3_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]))
    IA_3 = visual.TextStim(win, text = trial["IA_3"], units = 'pix', pos = (IA_3_posx, 0), alignText = 'left')
    IA_3_size = IA_3.boundingBox
    IA_4_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]) + int(IA_3_size[0]))
    IA_4 = visual.TextStim(win, text = trial["IA_4"], units = 'pix', pos = (IA_4_posx, 0), alignText = 'left')
    IA_4_size = IA_4.boundingBox
    IA_5_posx = int(x_pos_start + int(IA_1_size[0]) + int(IA_2_size[0]) + int(IA_3_size[0]) + int(IA_4_size[0]))
    IA_5 = visual.TextStim(win, text = trial["IA_5"], units = 'pix', pos = (IA_5_posx, 0), alignText = 'left')
    
    IA_1.draw()
    IA_2.draw()
    IA_3.draw()
    IA_4.draw()
    IA_5.draw()
    win.flip()
    
    
    
    core.wait(5)
    
    ## SEND AREAS OF INTEREST 
    
    
    ## SEND TRIAL-SPECIFIC INFORMATION
    
    
        
    ThisExp.nextEntry()
    