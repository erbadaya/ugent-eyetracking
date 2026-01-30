"""
Basic script for a Visual World Paradigm eye-tracking experiment
Author: Esperanza Badaya
Course: Eye-tracking in Language Research
15/01/2026

This is a template script for a VWP experiment. At the top of the script, you can find the customisable parts. You can also edit the script further to adapt it to your needs, but ideally the script covers all the possible experiments following what is discussed in the course.
The code relies on a series of functions to ease communication with participants and drawing areas of interest.

The assumed structure of this template is as follows:

- Welcome participant screen
- Eye-tracking instructions screen
- Calibration and validation
- Instructions experiment screen
- Experiment starts (no breaks, random presentation of stimuli) (Optional: Practice session)
- Goodbye

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
explanation_eyetracking = u'ET explanation'
instructions_text = u'What the task is about'
goodbye_text = u'Bye'
# optional: if you have practice/breaks in your experiment
practice_text = u''
break_text = u''

# text parameters

fontStim = 'Courier New'
sizeStim = 14
anchorHorizStim = 'left'
alignTextStim = 'left'
languageStyleStim = 'LTR'
colorText = 'black'

# file names

excel_conditions = 'template_vwp.xlsx' # write the filename of the excel with the experiment information
excel_practice = ''  # write the filename of the excel that has information about the practice session, if there is

# information for the GUI

info = {"Participant number": ""} # You can add more if you want

# eye-tracker configuration

preamble_text = ''
sampling_frequency = 1000
calibration_type = "HV5"

# visual world paradigm components

task_look = 'task' # define whether participants have to do something (mouse) or is a look-and-listen task, options task or look
nr_images = 4 # write the number of images that are shown on the screen, 2 or 4. if you want 3 or 5, you will need to think how to display them! 
preview_length = 1.5 # write the time of the preview window
img_width = 198
img_height = 198

# optional: timeout parameters (Note: timeout is only applicable to task VWP)
timeout = True
timeout_time = 1 # time for continuing to the next trial

##################################
## END COSTUMISATION PARAMETERS ##
##################################

##################################
##### CUSTOMISATION RUN_TRIAL ####
##################################

# open the run_trial function to customise the trial as needed (i.e., save conditions of interest, add triggers where necessary)

def run_trial(trial, nr_images):
    
    # load images

    if nr_images == 2:
        positions, image_1, image_2 = create_positions(nr_images, trial)
        image_1.draw()
        image_2.draw()
    elif nr_images == 4:
        positions, image_1, image_2, image_3, image_4 = create_positions(nr_images, trial)
        image_1.draw()
        image_2.draw()
        image_3.draw()
        image_4.draw()

    # create msg for ias
    msg_IAs = create_ias(nr_images, trial, positions)

    # load sound
    # TO COSTUMISE
    # this assumes two recordings

    carrier_sound = sound.Sound(trial['audio1'])
    target_sound = sound.Sound(trial['audio2'])
    
    carrier_sound.setVolume(1.0)
    target_sound.setVolume(1.0)


    # if you want to pilot the areas of interest

    if pilot_IAs:
        for ia in range(nr_images):
            rectIA = pilot_IARect(ia, positions, img_width, img_height)
            rectIA.draw()


    # mark the beginning of the trial
    # # Send message to the .EDF file (for later data segmentation) and to the ET PC for us
    
    et_tracker.sendMessage('TRIALID %d' % trials.thisN)

    # record_status_message : show some info on the ET PC
    # here we show how many trial has been tested
    # you could put condition, stimuli, etc. whatever is informative for you
    status_msg = 'TRIAL number %d' % trials.thisN
    et_tracker.sendCommand("record_status_message '%s'" % status_msg)

    # Perform drift correction (drift check)
    while not dummy_mode:
        if (not et_tracker.isConnected()) or et_tracker.breakPressed():
            abort_exp()
        try:
            error = et_tracker.doDriftCorrect(int(scr_width/2.0),
                                              int(scr_height/2.0), 1, 1)
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
    
    mouse.setVisible(visible = False)  # hide the mouse during preview window + audio

    win.flip()
    et_tracker.sendMessage('preview_onset')
    preview_onset = core.getTime()

    # tracking mouse clicks
    mouseIsDown = False
    instructionPlayed = False 
    targetPlayed = False
    audioFinished = False
    trialSkipped = False

    while True:
        # catch the error during the preview window
        error = et_tracker.isRecording()
        if error is not pylink.TRIAL_OK:
            et_tracker.sendMessage('tracker_disconnected')
            skip_trial()
            trialSkipped = True
            break
        for keycode, modifier in event.getKeys(modifiers=True):
            if keycode == 'escape': # for skipping a trial
                et_tracker.sendMessage('trial_skipped')
                skip_trial()
                trialSkipped = True
                break
            if keycode == "c" and (modifier['ctrl'] is True): # for terminating experiment
                et_tracker.sendMessage('experiment_aborted')
                abort_exp()
        if trialSkipped == False:
            # if we haven't skipped the trial or aborted the experiment after the preview window
            if core.getTime() - preview_onset >= preview_length:
                if instructionPlayed == False and trialSkipped == False:
                    carrier_sound.play()
                    # send trigger audio onset
                    et_tracker.sendMessage('audio_onset')
                    print("audio onset")
                    clock.wait(carrier_sound.getDuration() )
                    carrier_sound.stop()
                    instructionPlayed = True
                if instructionPlayed == True and targetPlayed == False and trialSkipped == False:
                    target_sound.play()
                    # send trigger target onset
                    et_tracker.sendMessage('target_onset')
                    print("target onset")
                    clock.wait(target_sound.getDuration())
                    target_sound.stop()
                    # send trigger target offset
                    et_tracker.sendMessage('target_offset')
                    my_clock.reset()
                    targetPlayed = True
                    mouse.setPos(newPos=(0, 0))
                if targetPlayed == True and audioFinished == False and trialSkipped == False:
                    mouse.setVisible(visible = True)
                    if timeout:
                        if sum(mouse.getPressed()) == 1 and mouseIsDown == False:
                            RT = round(my_clock.getTime() * 1000)
                            mouseIsDown = True
                            x_pos, y_pos = mouse.getPos()
                            object_clicked = calculate_object_clicked(x_pos, y_pos, nr_images, trial, positions)
                            break
                        if my_clock.getTime() >= timeout_time:
                            RT = 'timeout'
                            object_clicked = 'timeout'
                            break
                    else:
                        if sum(mouse.getPressed()) == 1 and mouseIsDown == False:
                            RT = round(my_clock.getTime() * 1000)
                            mouseIsDown = True
                            x_pos, y_pos = mouse.getPos()
                            object_clicked = calculate_object_clicked(x_pos, y_pos, nr_images, trial, positions)
                            break
                error = et_tracker.isRecording()
            if error is not pylink.TRIAL_OK:
                et_tracker.sendMessage('tracker_disconnected')
                skip_trial()
                trialSkipped = True
                mouse.setVisible(visible = False, newPos = (0,0)) 
                break
            for keycode, modifier in event.getKeys(modifiers=True):
                if keycode == 'escape': # for skipping a trial
                    et_tracker.sendMessage('trial_skipped')
                    skip_trial()
                    trialSkipped = True
                    mouse.setVisible(visible = False, newPos = (0,0)) 
                    break
                if keycode == "c" and (modifier['ctrl'] is True): # for terminating experiment
                    et_tracker.sendMessage('experiment_aborted')
                    abort_exp()
        else:
            break
                    
    # log information about areas of interest
    # in DataViewer, coordinates start at the top, left corner (i.e., 0,0)
    # RECTANGLE <id> <left> <top> <right> <bottom> [label]
    # we need to know the size of the images and the size of the screen

    for ia in range(nr_images):
        et_tracker.sendMessage(msg_IAs[ia])

    # stop recording, save information about the trial & mark trial end in the .EDF file
    
    # clear the screen
    # send a message to clear the Data Viewer screen as well
    et_tracker.sendMessage('!V CLEAR 128 128 128')

    # stop recording; add 100 msec to catch final events before stopping
    pylink.pumpDelay(100)
    et_tracker.stopRecording()

    # log information about this trial in the EDF file
    ### COSTUMISE WITH WHATEVER INFORMATION YOU WANT TO STORE IN THE EDF FILE
        
    et_tracker.sendMessage('!V TRIAL_VAR trial_type %s' % trial["trialtype"])
    et_tracker.sendMessage('!V TRIAL_VAR fluency %s' % trial["fluency"])
    pylink.pumpDelay(50) # adding a break to the et so we don't lose messages
    et_tracker.sendMessage('!V TRIAL_VAR honesty %s' % trial["honesty"])
    et_tracker.sendMessage('!V TRIAL_VAR RT %d' % RT)
    et_tracker.sendMessage('!V TRIAL_VAR object_clicked %s' % object_clicked)
    
    ### COSTUMISE WITH WHATEVER INFORMATION YOU WANT TO STORE IN THE BEHAVIOURAL FILE
    
    trials.addData('RT', RT)
    trials.addData('object_clicked', object_clicked)
        
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
            new_val =(coor_val + 1) * 0.5 * scr_width
        else:
            new_val = (1 - (coor_val + 1) * 0.5) * scr_height
    else:
        if axis == 'x':
            new_val = (2 * coor_val) / scr_width - 1
        else:
            new_val = 1 - (2 * coor_val) / scr_height
    return new_val

def calculate_edges_image(image, positions, img_width, img_height):
    
    # In PIXELS, center-origin
    x, y = positions[image][0], positions[image][1]
    half_w = img_width / 2.0
    half_h = img_height / 2.0
    left_pix   = x - half_w
    right_pix  = x + half_w
    top_pix    = y - half_h
    bottom_pix = y + half_h
    return left_pix, right_pix, top_pix, bottom_pix

def pilot_IARect(image, positions, img_width, img_height):

    left_pix, right_pix, top_pix, bottom_pix = calculate_edges_image(image, positions, img_width, img_height)
    
    center_x = (left_pix + right_pix)/2
    center_y = (top_pix + bottom_pix)/2

    width = abs(right_pix - left_pix)
    height = abs(bottom_pix - top_pix)

    rectIA = visual.Rect(win, width=width, height=height, pos=(center_x, center_y), fillColor = 'None', lineColor = 'red', units = 'pix')
    return rectIA

def calculate_object_clicked(x_coor, y_coor, nr_images, trial, positions):
    # y increases upwards in PsychoPy 'pix'
    for image in range(nr_images):
        left_pix, right_pix, top_pix, bottom_pix = calculate_edges_image(image, positions, img_width, img_height)
        if (left_pix <= x_coor <= right_pix) and (top_pix <= y_coor <= bottom_pix):
            # Fix the key name: 'image_{i}_label' (not 'image_f{...}')
            return trial[f'image_{image+1}_label']
    return 'none'  # if no hit

def create_ias(nr_images, trial, positions):

    # log information about areas of interest
    # in DataViewer, coordinates start at the top, left corner (i.e., 0,0)
    # RECTANGLE <id> <left> <top> <right> <bottom> [label]
    # we need to know the size of the images and the size of the screen
    
    msg_list = []
    for i in range(nr_images):
        x, y = positions[i][0], positions[i][1]
        # Convert center-origin (PsychoPy) to top-left origin (DataViewer/EDF)
        left   = int(scr_width / 2 + (x - img_width/2))
        right  = int(scr_width / 2 + (x + img_width/2))
        # For Y, invert because DataViewer Y grows downward
        top    = int(scr_height / 2 - (y + img_height/2))
        bottom = int(scr_height / 2 - (y - img_height/2))

        label = trial[f'image_{i+1}_label']
        msg = f'!V IAREA RECTANGLE {i+1} {left} {top} {right} {bottom} IA{i+1}_{label}'
        msg_list.append(msg)
    return msg_list

def create_positions(nr_images, trial):
    # Place images at the four quadrants in PIXELS (center-origin)
    # x: left/right offsets ~ quarter of screen width
    # y: up/down offsets ~ quarter of screen height
    if nr_images == 2:
        offset_x = scr_width // 4
        positions = [(-offset_x, 0), (offset_x, 0)]
    elif nr_images == 4:
        offset_x = scr_width // 4
        offset_y = scr_height // 4
        positions = [(-offset_x, offset_y),    # top-left
                     (-offset_x, -offset_y),   # bottom-left
                     (offset_x, -offset_y),    # bottom-right
                     (offset_x, offset_y)]     # top-right
    else:
        raise ValueError("nr_images must be 2 or 4 for this template.")

    numpy.random.shuffle(positions)

    # Always set size explicitly
    if nr_images == 2:
        image_1 = visual.ImageStim(win, image=trial["image_1_ID"],
                                   pos=positions[0], size=(img_width, img_height), units='pix')
        image_2 = visual.ImageStim(win, image=trial["image_2_ID"],
                                   pos=positions[1], size=(img_width, img_height), units='pix')
        return positions, image_1, image_2

    elif nr_images == 4:
        image_1 = visual.ImageStim(win, image=trial["image_1_ID"],
                                   pos=positions[0], size=(img_width, img_height), units='pix')
        image_2 = visual.ImageStim(win, image=trial["image_2_ID"],
                                   pos=positions[1], size=(img_width, img_height), units='pix')
        image_3 = visual.ImageStim(win, image=trial["image_3_ID"],
                                   pos=positions[2], size=(img_width, img_height), units='pix')
        image_4 = visual.ImageStim(win, image=trial["image_4_ID"],
                                   pos=positions[3], size=(img_width, img_height), units='pix')
        return positions, image_1, image_2, image_3, image_4
    
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

from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']  # force PTB first

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


# create screen

win = visual.Window(fullscr = True, checkTiming=False, color = (1, 1, 1), units = 'pix') # checkTiming is due to PsychoPy's latest release where measuring screen rate is shown to participants, in my case it gets stuck, so adding this parameter to prevent that

scr_width = win.size[0]
scr_height = win.size[1]

# create clock

my_clock = core.Clock()

# create mouse

mouse = event.Mouse(visible = False)

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