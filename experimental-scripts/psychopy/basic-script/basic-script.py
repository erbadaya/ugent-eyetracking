# Basic script eye-tracking
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

# Libraries

from psychopy import gui, visual, event, logging
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


# Load stimuli

faces = ['S1.jpg', 'S2.jpg', 'S3.jpg', 'S4.jpg', 'S5.jpg', 'S6.jpg', 'S7.jpg', 'S8.jpg', 'S9.jpg', 'S10.jpg', 'S11.jpg',
    'H1.jpg', 'H2.jpg', 'H3.jpg', 'H4.jpg', 'H5.jpg', 'H6.jpg', 'H7.jpg', 'H8.jpg', 'H9.jpg', 'H10.jpg', 'H11.jpg']

response_keys = ['s', 'h']

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
et_tracker.sendCommand("calibaration_type = HV5")
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

# 10 trials, iterate through the loop of faces

for i in range(10):
    
    # load and create trial stimuli on the fly
    
    i += 1
    numpy.random.shuffle(faces)
    face_st = faces[i]
    if face_st.startswith ('S'):
        emotion = 'sad'
    else:
        emotion = 'happy'
    image_stimuli = visual.ImageStim(win, image = face_st, pos = (0.0, -0.2))
    image_stimuli.size/=6 # rescale
    text_stimuli = visual.TextStim(win, text = "Press 's' if the face is sad, 'h' if the face is happy",
    pos = (0.0, 0.6), color = (0,0,0))
    
    # mark trial onset for the eye-tracker
    
    et_tracker.sendMessage('TRIALID' % trial_index) # TRIALID is the 'trigger' that DataViewer uses to segment trials
    
    # information to be shown in the host PC
    # in this case, we want to know what trial we are recording
    
    et_tracket.sendCommand("record_status_message TRIAL number '%d'" % trial_index)
    
    # every trial starts with a drift correction
    
    if not dummy_mode:
        et_tracker.doDriftCorrect(int(win_width/2), int(win_height/2), 1, 1)
    
    
    # start recording
    et_tracker.setOfflineMode()
    if not dummy_mode:
        et_tracker.startRecording(1, 1, 1, 1)
    
    # presentation of visual stimuli
    text_stimuli.draw()
    image_stimuli.draw()
    win.flip()
    
    # send trigger that images have been sent
    
    et_tracker.sendMessage('image_onset')
    
    resp = event.waitKeys(keyList = response_keys)
    
    # log information about this trial in the EDF file
    # in this case, what specific stimuli was shown
    # and the emotion shown
    
    et_tracker.sendMessage('!V TRIAL_VAR image %s' face_st)
    et_tracker.sendMessage('!V TRIAL_VAR emotion %s' emotion)
    
    # stop recording
    if not dummy_mode:
        pylink.pumpDelay(100)
        et_tracker.stopRecording()
        et_tracker.sendMessage("TRIAL_RESULT %d" % pylink.TRIAL_OK) # used by DataViewer to segment the data
    
# End of trials
# save EDF file and close connection with the Host PC

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    et_tracker.closeDataFile()
    et_tracker.receiveDataFile(edf_file, os.getcwd() + "/el_data/" + edf_file)
    et_tracker.close()