"""
Basic script for a single sentence reading eye-tracking experiment
Author: Esperanza Badaya
Course: Eye-tracking in Language Research
26/01/2026

This is a template script for a single sentence reading experiment. At the top of the script, you can find the customisable parts. You can also edit the script further to adapt it to your needs, but ideally the script covers all the possible experiments following what is discussed in the course.
The code relies on a series of functions to ease communication with participants and drawing areas of interest.

The assumed structure of this template is as follows:

- Welcome participant screen
- Eye-tracking instructions screen
- Calibration and validation
- Instructions experiment screen
- Experiment starts (no breaks, random presentation of stimuli) (Optional: Practice session)
- Goodbye screen

"""

#############################
## PARAMETER CUSTOMISATION ##
#############################

# ET or no ET?

dummy_mode = True # set to False when you are going to collect data (you can alternatively add this in the GUI)

# Pilot IAs?

pilot_IAs = True # set to False when you are going to collect data or if you do not want to see the rectangles for IAs while piloting on your own machine

# Practice or no practice?

practice = False

# communication with participant

welcome_text = u'Welcome'
explanation_eyetracking = u'Explanation'
instructions_text = u'Instructions'
goodbye_text = u'Tot ziens!'
# optional: if you have practice/breaks in your experiment
practice_text = u''
break_text = u''

# file names

excel_conditions = 'template_reading.xlsx' # write the filename of the excel with the experiment information
excel_practice = ''  # write the filename of the excel that has information about the practice session, if there is

# information for the GUI

info = {"Participant number": ""} # You can add more if you want

# eye-tracker configuration

preamble_text = ''
sampling_frequency = 1000
calibration_type = "HV5"

# single sentence reading components

# text parameters
position_start_text = (-200, 0) # this value is used to place the text and to perform the drift correction, in PsychoPy coordinates
fontStim = 'Courier New'
sizeStim = 14 # in pixels, first check the conversion ~
padding = 30 # amount of extra space for areas of interest at the top and bottom
anchorHorizStim = 'left'
alignTextStim = 'left'
languageStyleStim = 'LTR'
colorText = 'black'

# optional: timeout parameters
timeout = False
timeout_time = None

##################################
## END COSTUMISATION PARAMETERS ##
##################################

##################################
##### CUSTOMISATION RUN_TRIAL ####
##################################

# open the run_trial function to customise the trial as needed (i.e., save conditions of interest, add triggers where necessary)

def run_trial(trial, nr_ias, position_start_text, timeout, fontExp, sizeExp, anchorHorizExp, alignTextExp, 
              languageStyleExp, timeout_time = None):

    # draw the text
    # this part is a bit convoluted as we are using the position from the previous piece of text to draw the next one
    # and also to draw areas of interest
    # alternative: just send an image to the tracker and then draw the areas in preprocessing (time consuming, error prone)

    # mark the beginning of the trial
    # # Send message to the .EDF file (for later data segmentation) and to the ET PC for us
    
    et_tracker.sendMessage('TRIALID %d' % trials.thisN)

    # Draw text

    sentence_stimulus = visual.TextStim(win, text = trial['sentence'], units = 'pix', pos = position_start_text,
                                languageStyle = languageStyleExp, anchorHoriz = anchorHorizExp, alignText = alignTextExp,
                                font = fontExp, color = colorText)
    
    sentence_stimulus.size = sizeExp
    sentence_stimulus.draw()
    wS, hS = sentence_stimulus.boundingBox

    # Calculate widths

    widthStims = calculate_WidthIA(sentence_stimulus, wS, hS, trial, nr_ias)
    left_IAs_EDF, right_IAs_EDF = create_xcoors_ias(nr_ias, widthStims, position_start_text[0])
    top_EDF, bottom_EDF = create_ycoors_ias(hS, padding, position_start_text[1])
    msgs_IAs = create_msg_ias(nr_ias, left_IAs_EDF, top_EDF, right_IAs_EDF, bottom_EDF)

    # If you want to pilot the IAs
    
    if pilot_IAs:
        for ia in range(nr_ias):
            rectIA = pilot_IARect(left_IAs_EDF[ia], right_IAs_EDF[ia], top_EDF, bottom_EDF)
            rectIA.draw()

    # record_status_message : show some info on the ET PC
    # here we show how many trial has been tested
    # you could put condition, stimuli, etc. whatever is informative for you
    status_msg = 'TRIAL number %d' % trials.thisN
    et_tracker.sendCommand("record_status_message '%s'" % status_msg)

    # Perform drift correction (drift check)
    # 
    while not dummy_mode:
        if (not et_tracker.isConnected()) or et_tracker.breakPressed():
            abort_exp()
        try:
            error = et_tracker.doDriftCorrect(position_start_text[0],
                                              position_start_text[1], 1, 1)
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

    win.flip() # display text on screen
    et_tracker.sendMessage('text_onset')
    my_clock.reset()

    if not timeout:
        event.waitKeys(keyList = ['space'])
        et_tracker.sendMessage('space_pressed')
        RT = round(my_clock.getTime() * 1000)
    else:
        keys = event.waitKeys(maxWait = timeout_time, keyList = ['space'])
        if keys is None:
            et_tracker.sendMessage('timeout_trial')
            RT = 'timeout'
        else:
            et_tracker.sendMessage('space_pressed')
            RT = round(my_clock.getTime() * 1000)

    # stop recording; add 100 msec to catch final events before stopping
    pylink.pumpDelay(100)
    et_tracker.stopRecording()

    # log information about this trial in the EDF file
    # send Areas of Interest

    for ia in range(nr_ias):
        et_tracker.sendMessage(msgs_IAs[ia])
        
        ## SEND TEXT TO TRACKER & FOR DATA ANALYSIS IN DATAVIEWER
    
    # imageBackdrop() uses the PIL module, works with all versions of EyeLink Host PC
    # bitmapBackdrop() works with EyeLInk 1000 + and Portabele duo only & EyeLink Developers Kit 2.0 and up
    # using the latter
    
    
    if not dummy_mode:
        screenshot = str(trial_index) + '_' + str(ppt_number)+'.png'
        scn_shot = os.path.join(results_folder, screenshot)
        win.getMovieFrame()
        win.saveMovieFrames(scn_shot)
        et_tracker.sendMessage('!V IMGLOAD FILL %s' % screenshot)

    ### COSTUMISE WITH WHATEVER INFORMATION YOU WANT TO STORE IN THE EDF FILE
        
    et_tracker.sendMessage('!V TRIAL_VAR full_sentence %s' % trial["sentence"])
    et_tracker.sendMessage('!V TRIAL_VAR frequency %s' % trial["frequency"])
    pylink.pumpDelay(50) # adding a break to the et so we don't lose messages
    
    ### COSTUMISE WITH WHATEVER INFORMATION YOU WANT TO STORE IN THE BEHAVIOURAL FILE
    
    trials.addData('frequency', trial["frequency"])
    trials.addData('RT', RT)
    
    # send a 'TRIAL_RESULT' message to mark the end of trial, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    et_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)

######################################
##### END CUSTOMISATION RUN_TRIAL ####
######################################

# These are helper functions

def translate_coordinates(coor_val, scr_width, scr_height, axis = 'x', direction = 'to_edf'):
    if direction == 'to_edf':
        if axis == 'x':
            new_val = coor_val + (scr_width/2)
        else:
            new_val = (scr_height/2) - coor_val
    else:
        if axis == 'x':
            new_val = coor_val - (scr_width/2)
        else:
            new_val = (scr_height/2) - coor_val
    return new_val

def pilot_IARect(left_edf, right_edf, top_edf, bottom_edf):
    left_pix = translate_coordinates(left_edf, scr_width=scr_width, scr_height=scr_height, axis = 'x', direction = 'to_pix')
    right_pix = translate_coordinates(right_edf, scr_width=scr_width, scr_height=scr_height, axis = 'x', direction = 'to_pix')
    top_pix = translate_coordinates(top_edf, scr_width=scr_width, scr_height=scr_height, axis = 'y', direction = 'to_pix')
    bottom_pix = translate_coordinates(bottom_edf, scr_width=scr_width, scr_height=scr_height, axis = 'y', direction = 'to_pix')
    
    center_x = (left_pix + right_pix)/2
    center_y = (top_pix + bottom_pix)/2

    width = abs(right_pix - left_pix)
    height = abs(bottom_pix - top_pix)

    rectIA = visual.Rect(win, width=width, height=height, pos=(center_x, center_y), fillColor = 'None', lineColor = 'red', units = 'pix')
    return rectIA

def calculate_WidthIA(text_stimulus, wS, hS, trial, nr_ias):
    
    size_character = wS/len(text_stimulus.text)

    IA_widths = []

    for ia in range(nr_ias):
        nr_characters = trial[f'nr_ch_IA{ia+1}']
        width = nr_characters * size_character
        IA_widths.append(width)

    return IA_widths

def create_xcoors_ias(nr_ias, IA_widths, start_x_coordinate):

    left_IAs = []
    right_IAs = []

    for ia in range(nr_ias):
        if len(left_IAs) == 0:
            point_left = start_x_coordinate
            left_IAs.append(point_left)
            point_right = start_x_coordinate + IA_widths[ia]
            right_IAs.append(point_right)
        else:
            point_left = right_IAs[-1]
            left_IAs.append(point_left)
            point_right = right_IAs[-1] + IA_widths[ia]
            right_IAs.append(point_right)

    # transform into EDF coordinates

    left_IAs_EDF = []
    right_IAs_EDF = []

    for i in range(nr_ias):
        left_EDF = translate_coordinates(left_IAs[i], scr_width=scr_width, scr_height=scr_height, axis = 'x')
        right_EDF = translate_coordinates(right_IAs[i], scr_width=scr_width, scr_height=scr_height, axis = 'x')
        left_IAs_EDF.append(left_EDF)
        right_IAs_EDF.append(right_EDF)
    print(left_IAs_EDF, right_IAs_EDF)
    
    return left_IAs_EDF, right_IAs_EDF

def create_ycoors_ias(hS, padding, start_y_coordinate):

    top = start_y_coordinate + hS + padding
    bottom = start_y_coordinate - hS - padding

    # transform into EDF coordinates

    top_EDF = translate_coordinates(top, scr_width=scr_width, scr_height=scr_height, axis = 'y')
    bottom_EDF = translate_coordinates(bottom, scr_width=scr_width, scr_height=scr_height, axis = 'y')
    print(top_EDF, bottom_EDF)
    return top_EDF, bottom_EDF

def create_msg_ias(nr_ias, left_edf, top_edf, right_edf, bottom_edf):

    msg_list = []
    for ia in range(nr_ias):
         msg = f'!V IAREA RECTANGLE {ia + 1} {left_edf[ia]} {top_edf} {right_edf[ia]} {bottom_edf} IA{ia + 1}'
         msg_list.append(msg)

    return msg_list

def message(message_text = "", response_key = "space", duration = 0, height = None, pos = (0.0, 0.0), color = colorText, font = fontStim, size = sizeStim, languageStyle = languageStyleStim):
    message_on_screen = visual.TextStim(win, text = "OK", languageStyle = languageStyle)
    message_on_screen.text    = message_text
    message_on_screen.height  = height
    message_on_screen.pos     = pos
    message_on_screen.color   = color
    message_on_screen.size    = size
    message_on_screen.font    = font
    
    message_on_screen.draw()
    win.flip()
    if duration == 0: # for the welcome and goodbye
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration) # for the feedback

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

#######################
## EXPERIMENT STARTS ##
#######################

# import modules

from psychopy import gui, visual, event, logging, data, sound, clock, core, hardware
import time, os, numpy

# eye-tracking libraries
import pylink
#from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy # remember to put this script in your folder & sounds

# display GUI

wk_dir = os.getcwd()

ppt_number_taken = True
while ppt_number_taken:
    infoDlg = gui.DlgFromDict(dictionary = info, title = 'Participant information')
    ppt_number = str(info['Participant number'])
    edf_name = ppt_number # to obtain EDF file name, you could alternatively use ppt_number
    behavioural_file = 'behavioural/pp_' + ppt_number 
    edf_file = edf_name + '.EDF' # remember to add the .edf extension
    if not infoDlg.OK: #Quit the experiment if 'Cancel' is selected
        core.quit()
    if not os.path.isfile(behavioural_file + '.csv'):
        ppt_number_taken = False
    else:
        infoDlg2 = gui.Dlg(title = 'Error') #If the participant number is not unique, present an error msg
        infoDlg2.addText('This participant number is in use already, please select another')
        infoDlg2.show() #For this dlg method we need the .show() for presenting

# Set up the folder to save .edf files in the STIM PC
# There is one general folder for eye-tracking data (et_results) and within that folder, one per participant
# This is because we are also taking screenshots of each trial for later data pre-processing

results_folder = 'et_results/pp_' + str(info['Participant number'])
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
local_edf = os.path.join(results_folder, edf_file) # we call this at the end to transfer .EDF from ET PC to STIM PC

# load in stimuli

trial_list = data.importConditions(excel_conditions) 
trials = data.TrialHandler(trial_list, nReps = 1, method = 'random')
ThisExp = data.ExperimentHandler(dataFileName = behavioural_file, extraInfo = info)
ThisExp.addLoop(trials)

# create screen

win = visual.Window(fullscr = True, checkTiming=False, color = (1, 1, 1), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that

scr_width = win.size[0]
scr_height = win.size[1]

# create clock

my_clock = core.Clock()

# start the eye-tracking components

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

et_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# 3. Configure the tracker

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    
    et_tracker.sendCommand("sample_rate %d" % sampling_frequency) 
    et_tracker.sendCommand("recording_parse_type = GAZE")
    et_tracker.sendCommand("select_parser_configuration 0")
    et_tracker.sendCommand("calibration_type = %s" %  calibration_type)
    et_tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (scr_width-1, scr_height-1)) # this needs to be modified to the Display PC screen size you are using
    et_tracker.sendMessage("DISPLAY_COORDS 0 0 %d %d" % (scr_width-1, scr_height-1)) # this needs to be modified to the Display PC screen size you are using
    
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

# welcome participant

message(welcome_text)

# instructions eye-tracking

message(explanation_eyetracking)

# calibration and validation

if not dummy_mode:
    genv = EyeLinkCoreGraphicsPsychoPy(et_tracker, win) # we are using openGraphicsEx(), cf. manual openGraphics versus this.
    foreground_color = (-1, -1, -1)
    background_color = win.color
    genv.setCalibrationColors(foreground_color, background_color)
    pylink.openGraphicsEx(genv)
    try:
        et_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        et_tracker.exitCalibration()

# instructions experiment

message(instructions_text)

# optional: practice session

if practice:
    practice_list = data.importConditions(excel_practice) 
    ptrials = data.TrialHandler(practice_list, nReps = 1, method = 'random')
    ThisExp.addLoop(ptrials)
    message(practice_text)
    for p_trial in ptrials:
        run_trial(p_trial, nr_images)
        ThisExp.nextEntry()

ThisExp.addLoop(trials)
for trial in trials:
    run_trial(trial, nr_images)
    ThisExp.nextEntry()

# We need to close the data file, transfer it from ET PC to STIM PC and then close the connection between both PCs (plus exist PsychoPy)

if not dummy_mode:
    et_tracker.setOfflineMode()
    pylink.pumpDelay(100)
    et_tracker.closeDataFile() # close the file
    pylink.pumpDelay(500)
    et_tracker.receiveDataFile(edf_file, local_edf) # transfer the file
    et_tracker.close() # close the link

# goodbye screen

message(goodbye_text)

win.close()
core.quit()
sys.exit()