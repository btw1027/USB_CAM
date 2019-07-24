#!/usr/bin/env python

""" GUI for setting up stereo cameras with PySpin library """

# NOTE: As of May-15-2018, It appears basically nothing in matplotlib and
# PySpin is thread safe.

# pylint: disable=global-statement,line-too-long

import sys
import queue
import functools
import math
from datetime import datetime
from tkinter import messagebox

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.widgets import Slider

from PIL import Image

import usb_cam

# These are min/max values for FLIR Blackfly S BFS-U3-200S6C camera

__FPS_MIN = 1.33
__FPS_MAX = 20              # Depends on USB port speed and Image Size
__GAIN_MIN = 0              # Units are dB
__GAIN_MAX = 27            # Units are dB
__EXPOSURE_MIN = 10000         # units must be micro seconds
__EXPOSURE_MAX = 30000   # units must be micro seconds

# Set up GUI params
__QUEUE = queue.Queue()
__STREAM = False
__IMSHOW_PRIMARY_DICT = {'imshow': None, 'imshow_size': None, 'max_val': None}
__HIST_PRIMARY_DICT = {'bar': None, 'max_val': None}
__GUI_DICT = None

# -------------- #
# Wrappers       #
# -------------- #

def __queue_wrapper(func):
    """ wraps function such that it gets inserted into the queue when called """

    @functools.wraps(func)
    def __wrapped_func(*args, **kwargs):
        """ wrapped function """

        __QUEUE.put((func, args, kwargs))
    return __wrapped_func

def __message_box_wrapper(func):
    """ wraps function in try/except and pops up message box with exception """

    @functools.wraps(func)
    def __wrapped_func(*args, **kwargs):
        """ wrapped function """

        try:
            func(*args, **kwargs)
        except Exception as e: # pylint: disable=broad-except,invalid-name
            messagebox.showerror("Error", str(e))
    return __wrapped_func

# -------------- #
# Callbacks      #
# -------------- #

@__queue_wrapper
@__message_box_wrapper
def __find_and_init_primary(_=None):
    """ Finds and initializes primary camera """

    find_and_init_text = __GUI_DICT['cam_plot_primary_dict']['find_and_init_text'].text

    print('Finding primary camera...')
    usb_cam.find_primary(find_and_init_text)

    print('Initializing primary camera...')
    usb_cam.init_primary(find_and_init_text)

@__queue_wrapper
@__message_box_wrapper
def __start_stream(_=None):
    """ Starts stream of cameras """
    global __STREAM

    # Make sure they aren't already streaming
    if not __STREAM:
        print('Starting stream...')

        # Set buffer to newest only
        usb_cam.primary_node_cmd('TLStream.StreamBufferHandlingMode',
                                       'SetValue',
                                       'RW',
                                       'PySpin.StreamBufferHandlingMode_NewestOnly')

        # Set acquisition mode to continuous
        usb_cam.primary_node_cmd('AcquisitionMode',
                                       'SetValue',
                                       'RW',
                                       'PySpin.AcquisitionMode_Continuous')

        # Start acquisition - Must start secondary acquisition first in case there
        # is a hardware trigger!
        usb_cam.start_acquisition_primary()

        # Enable stream
        __STREAM = True

@__queue_wrapper
@__message_box_wrapper
def __stop_stream(_=None):
    """ Stops stream of cameras """
    global __STREAM

    # Make sure they're streaming
    if __STREAM:
        print('Stopping stream...')

        # Stop acquisition - Order shouldn't matter here
        usb_cam.end_acquisition_primary()

        # End stream
        __STREAM = False

        
@__queue_wrapper
@__message_box_wrapper
def __drawtool(_=None):
    """ Draw tool """
    """ Stops stream of cameras """
    global __STREAM

    # Make sure they're streaming
    if __STREAM:
        print('Stopping stream...')

        # Stop acquisition - Order shouldn't matter here
        usb_cam.end_acquisition_primary()
         # End stream
        __STREAM = False
    
    
    #ax = plt.gca()
    xy = plt.ginput(2)
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    #line, = ax.plot(x,y, 'r')
    distance = math.sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2)
    distance_s = '%4.3f' % distance
    distance_micron = distance*11.85318
    distance_micron_s = '%4.3f' % distance_micron
    
    __GUI_DICT['distancetext'].eventson = False
    __GUI_DICT['distancetext'].set_val('The Distance is '+distance_s+' px, '+distance_micron_s+' um')
    __GUI_DICT['distancetext'].eventson = True
        
    
@__queue_wrapper
@__message_box_wrapper
def __gain_slider_primary(_=None):
    """ primary gain slider callback """

    gain = __GUI_DICT['gain_slider_primary'].val

    # Update text to match slider
    __GUI_DICT['gain_text_primary'].eventson = False
    __GUI_DICT['gain_text_primary'].set_val(gain)
    __GUI_DICT['gain_text_primary'].eventson = True

    # Set gain for primary camera
    usb_cam.set_gain_primary(gain)

@__queue_wrapper
@__message_box_wrapper
def __gain_text_primary(_=None):
    """ primary gain text callback """

    gain_text = __GUI_DICT['gain_text_primary'].text
    if not gain_text:
        return

    gain = float(gain_text)

    # Update slider to match text
    __GUI_DICT['gain_slider_primary'].eventson = False
    __GUI_DICT['gain_slider_primary'].set_val(gain)
    __GUI_DICT['gain_slider_primary'].eventson = True

    # Set gain for cameras
    usb_cam.set_gain_primary(gain)

@__queue_wrapper
@__message_box_wrapper
def __exposure_slider(_=None):
    """ Exposure slider callback """

    exposure = __GUI_DICT['exposure_slider'].val

    # Update text to match slider
    __GUI_DICT['exposure_text'].eventson = False
    __GUI_DICT['exposure_text'].set_val(exposure)
    __GUI_DICT['exposure_text'].eventson = True

    # Set exposure for camera
    usb_cam.set_exposure(exposure)

@__queue_wrapper
@__message_box_wrapper
def __exposure_text(_=None):
    """ Exposure text callback """

    exposure_text = __GUI_DICT['exposure_text'].text
    if not exposure_text:
        return

    exposure = float(exposure_text)

    # Update slider to match text
    __GUI_DICT['exposure_slider'].eventson = False
    __GUI_DICT['exposure_slider'].set_val(exposure)
    __GUI_DICT['exposure_slider'].eventson = True

    # Set exposure for cameras
    usb_cam.set_exposure(exposure)

@__queue_wrapper
@__message_box_wrapper
def __fps_slider(_=None):
    """ FPS slider callback """

    fps = __GUI_DICT['fps_slider'].val

    # Update text to match slider
    __GUI_DICT['fps_text'].eventson = False
    __GUI_DICT['fps_text'].set_val(fps)
    __GUI_DICT['fps_text'].eventson = True

    # Set frame rate for cameras
    usb_cam.set_frame_rate(fps)

@__queue_wrapper
@__message_box_wrapper
def __fps_text(_=None):
    """ FPS text callback """

    fps_text = __GUI_DICT['fps_text'].text
    if not fps_text:
        return

    fps = float(fps_text)

    # Update slider to match text
    __GUI_DICT['fps_slider'].eventson = False
    __GUI_DICT['fps_slider'].set_val(fps)
    __GUI_DICT['fps_slider'].eventson = True

    # Set frame rate for cameras
    usb_cam.set_frame_rate(fps)

# Helper function; do not call this directly!
def __save_images(save_type):
    """ Care is taken here to ensure images are taken close to each other in time """

    if not __STREAM:
        raise RuntimeError('Stream has not been started yet! Please start it first.')

    # Get name format, counter, and number of images
    name_format = __GUI_DICT['name_format_text'].text
    counter = int(__GUI_DICT['counter_text'].text)
    num_images = int(__GUI_DICT['num_images_text'].text)

    # Grab images
    for i in range(num_images):
        # Get image dicts - must acquire primary image first in case there is a hardware trigger!
        image_primary_dict = usb_cam.get_image_primary()

        # Make sure images are complete
        if 'data' in image_primary_dict:
            if save_type == 'primary':
                # Save primary image
                primary_name = name_format.format(serial=usb_cam.get_serial_primary(),
                                                  datetime=str(datetime.fromtimestamp(image_primary_dict['timestamp'])),
                                                  counter=counter+i)

                # Remove spaces and dots; 
                primary_name = primary_name.replace(' ', '_').replace('.', '_') + '.tif'

                # Save primary image
                print('Acquired: ' + primary_name)
                Image.fromarray(image_primary_dict['data'].astype(np.uint32)).save(primary_name,
                                                                                   optimize=False,
                                                                                   compress_level=0,
                                                                                   bits=image_primary_dict['bitsperpixel'])

# Update counter
    __GUI_DICT['counter_text'].set_val(str(counter+num_images))

@__queue_wrapper
@__message_box_wrapper
def __save_primary_images(_=None):
    """ Save primary image(s) """

    __save_images('primary')

# -------------- #
# GUI            #
# -------------- #

def __slider_with_text(fig, pos, slider_str, val_min, val_max, val_default, padding): # pylint: disable=too-many-arguments
    """ Creates a slider with text box given a position """

    # Set position params
    slider_padding = 0.1
    slider_text_width = (0.5-3*padding)/3

    # Slider
    slider_pos = [pos[0]+slider_padding+padding,
                  pos[1],
                  pos[2]-slider_padding-3*padding-slider_text_width,
                  pos[3]]
    slider_axes = fig.add_axes(slider_pos)
    slider = Slider(slider_axes,
                    slider_str,
                    val_min,
                    val_max,
                    valinit=val_default,
                    valfmt="%3.3f",
                    dragging=False, )
    slider.label.set_fontsize(20)
    slider.valtext.set_visible(False)

    # Text
    text_pos = [slider_pos[0]+slider_pos[2]+padding,
                slider_pos[1],
                slider_text_width,
                pos[3]]
    text_axes = fig.add_axes(text_pos)
    text = TextBox(text_axes, '')

    return (slider, text)

def __cam_plot(fig, pos, cam_str, options_height, padding): # pylint: disable=too-many-locals
    """ Creates 'camera' plot; make one of these per camera """

    # Set position params
    num_options = 1
    residual_height = pos[3]-(3+num_options)*padding-num_options*options_height
    image_height = residual_height
    image_width = pos[2]-2*padding
    hist_height = residual_height-image_height

    # Set axes
    image_pos = [pos[0]+padding, pos[1]+pos[3]-image_height-padding, image_width, image_height]
    image_axes = fig.add_axes(image_pos)
    image_axes.set_xticklabels([])
    image_axes.set_yticklabels([])
    image_axes.set_xticks([])
    image_axes.set_yticks([])

    #hist_pos = [image_pos[0], image_pos[1]-hist_height-padding, image_width, hist_height]
    #hist_axes = fig.add_axes(hist_pos)
    #hist_axes.set_xticklabels([])
    #hist_axes.set_yticklabels([])
    #hist_axes.set_xticks([])
   # hist_axes.set_yticks([])

    find_and_init_button_pos = [image_pos[0],
                                image_pos[1]-hist_height-6*padding,
                                (image_width-padding)*0.5,
                                options_height]
    find_and_init_button_axes = fig.add_axes(find_and_init_button_pos)

    find_and_init_text_pos = [find_and_init_button_pos[0]+find_and_init_button_pos[2]+padding,
                              find_and_init_button_pos[1],
                              (image_width-padding)*0.5,
                              options_height]
    find_and_init_text_axes = fig.add_axes(find_and_init_text_pos)

    # Set widgets
    find_and_init_button = Button(find_and_init_button_axes, 'Find and Initialize Camera')
    find_and_init_button.label.set_fontsize(20)
    find_and_init_text = TextBox(find_and_init_text_axes, '')
    # find_and_init_text.label.set_fontsize(18)
    
    

    return {'image_axes': image_axes,
            'find_and_init_button': find_and_init_button,
            'find_and_init_text': find_and_init_text}

def __stereo_gui(): # pylint: disable=too-many-locals,too-many-statements
    """ Main function for GUI for setting up stereo cameras with PySpin library """

    # Get figure
    fig = plt.figure()
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    # Set position params
    padding = 0.01
    options_height = 0.05
    num_options = 0
    cam_plot_height_offset = num_options*options_height+num_options*padding
    cam_plot_width = 0.70
    cam_plot_height = 1-cam_plot_height_offset
    fontsize = 20
    #POS = [LEFT, BUTTOM, WIDTH, HEIGHT]
    # Primary camera plot
    cam_primary_pos = [0,
                       cam_plot_height_offset,
                       cam_plot_width,
                       cam_plot_height]
    cam_plot_primary_dict = __cam_plot(fig,
                                       cam_primary_pos,
                                       'Primary',
                                       options_height,
                                       padding)
    # Set initial values
    cam_plot_primary_dict['find_and_init_text'].set_val('primary.yaml')
    # Set callbacks
    cam_plot_primary_dict['find_and_init_button'].on_clicked(__find_and_init_primary)

    # Start stream
    start_stream_button_pos = [0.70+padding,
                               1-options_height-padding,
                               0.15-2*padding,
                               options_height]
    start_stream_button_axes = fig.add_axes(start_stream_button_pos)
    start_stream_button = Button(start_stream_button_axes, 'Start Stream')
    start_stream_button.label.set_fontsize(fontsize)
    # Set callback
    start_stream_button.on_clicked(__start_stream)

    # Stop stream
    stop_stream_button_pos = [0.85+padding,
                              1-options_height-padding,
                              0.15-2*padding,
                              options_height]
    stop_stream_button_axes = fig.add_axes(stop_stream_button_pos)
    stop_stream_button = Button(stop_stream_button_axes, 'Stop Stream')
    stop_stream_button.label.set_fontsize(fontsize)
    # Set callback
    stop_stream_button.on_clicked(__stop_stream)

    # Primary gain
    gain_primary_pos = [0.70+padding, start_stream_button_pos[1]-options_height-padding, 0.3-padding, options_height]
    (gain_slider_primary, gain_text_primary) = __slider_with_text(fig,
                                                                  gain_primary_pos,
                                                                  'Gain',
                                                                  __GAIN_MIN,
                                                                  __GAIN_MAX,
                                                                  __GAIN_MIN,
                                                                  padding)
    # Set callbacks
    gain_slider_primary.on_changed(__gain_slider_primary)
    gain_text_primary.on_submit(__gain_text_primary)

    # Exposure
    exposure_pos = [0.70+padding, gain_primary_pos[1]-options_height-padding, 0.3-padding, options_height]
    (exposure_slider, exposure_text) = __slider_with_text(fig,
                                                          exposure_pos,
                                                          'Exposure',
                                                          __EXPOSURE_MIN,
                                                          __EXPOSURE_MAX,
                                                          __EXPOSURE_MIN,
                                                          padding)
    # Set callbacks
    exposure_slider.on_changed(__exposure_slider)
    exposure_text.on_submit(__exposure_text)
    
    # FPS
    fps_pos = [0.70+padding, exposure_pos[1]-options_height-padding, 0.3-padding, options_height]
    (fps_slider, fps_text) = __slider_with_text(fig,
                                                fps_pos,
                                                'FPS',
                                                __FPS_MIN,
                                                __FPS_MAX,
                                                __FPS_MIN,
                                                padding)
    # Set callbacks
    fps_slider.on_changed(__fps_slider)
    fps_text.on_submit(__fps_text)
    
    # drawtool button
    drawtool_button_pos = [0.70+padding, fps_pos[1]-options_height-padding, 0.1, options_height]
    drawtool_button_axes = fig.add_axes(drawtool_button_pos)
    drawtool_button = Button(drawtool_button_axes, 'Draw Tool')
    drawtool_button.label.set_fontsize(fontsize)
    # Set callback
    drawtool_button.on_clicked(__drawtool)
    
    distancetext_pos = [0.85+padding, fps_pos[1]-options_height-padding, 0.25, options_height]
    distancetext_axes = fig.add_axes(distancetext_pos)
    distancetext = TextBox(distancetext_axes, 'Distance', initial='')
    distancetext.label.set_fontsize(fontsize)
    # Set callback



    # Set name format
    name_format_pos = [0.70+padding,
                       drawtool_button_pos[1]-options_height-padding,
                       0.3-padding,
                       options_height]
    name_format_axes = fig.add_axes(name_format_pos)
    name_format_text = TextBox(name_format_axes, 'Name format')
    name_format_text.label.set_fontsize(fontsize)
    name_format_text.set_val('{serial}_{datetime}_{counter}')

    # Set counter
    counter_pos = [0.70+padding,
                   name_format_pos[1]-options_height-padding,
                   0.3-padding,
                   options_height]
    counter_axes = fig.add_axes(counter_pos)
    counter_text = TextBox(counter_axes, 'Counter')
    counter_text.label.set_fontsize(fontsize)
    counter_text.set_val(1)

    # Set save primary button
    save_primary_button_pos = [0.70+padding,
                               counter_pos[1]-options_height-padding,
                               0.3-padding,
                               options_height]
    save_primary_button_axes = fig.add_axes(save_primary_button_pos)
    save_primary_button = Button(save_primary_button_axes, 'Save Primary Image(s)')
    save_primary_button.label.set_fontsize(fontsize)
    # Set callback
    save_primary_button.on_clicked(__save_primary_images)

    # Set num images text
    num_images_text_pos = [save_primary_button_pos[0]+save_primary_button_pos[2]+padding+(0.5-2*padding)*0.1875+2*padding,
                           name_format_pos[1]-options_height-padding,
                           (0.5-2*padding)*0.8125-padding,
                           options_height]
    num_images_text_axes = fig.add_axes(num_images_text_pos)
    num_images_text = TextBox(num_images_text_axes, '#')
    num_images_text.label.set_fontsize(fontsize)
    num_images_text.set_val(1)

    return {'fig': fig,
            'cam_plot_primary_dict': cam_plot_primary_dict,
            'start_stream_button': start_stream_button,
            'stop_stream_button': stop_stream_button,
            'gain_slider_primary': gain_slider_primary,
            'exposure_slider': exposure_slider,
            'exposure_text': exposure_text,
            'drawtool_button': drawtool_button,
            'distancetext': distancetext,
            'fps_slider': fps_slider,
            'fps_text': fps_text,
            'name_format_text': name_format_text,
            'counter_text': counter_text,
            'save_primary_button': save_primary_button,
            'num_images_text': num_images_text}

# -------------- #
# Set up stream  #
# -------------- #

def __plot_image(image, max_val, image_axes, imshow_dict):
    """ plots image somewhat fast """

    # If image size changes or max val changes, then we must replot imshow
    if image.shape != imshow_dict['imshow_size'] or max_val != imshow_dict['max_val']:
        # Must reset axes and re-imshow()
        image_axes.cla()
        imshow_dict['imshow'] = image_axes.imshow(image, cmap='gray', vmin=0, vmax=max_val)
        imshow_dict['imshow_size'] = image.shape
        imshow_dict['max_val'] = max_val
        image_axes.set_xticklabels([])
        image_axes.set_yticklabels([])
        image_axes.set_xticks([])
        image_axes.set_yticks([])
    else:
        # Can just "set_data" since data is the same size and has the same max val
        imshow_dict['imshow'].set_data(image)

    return imshow_dict

@__queue_wrapper
@__message_box_wrapper
def __stream_images():
    """ stream update of images """
    global __IMSHOW_PRIMARY_DICT

    try:
        # Get image dicts - Must acquire primary image first in case there is a hardware trigger!
        image_primary_dict = usb_cam.get_image_primary()

        # Make sure images are complete
        if 'data' in image_primary_dict:
            # Plot primary image and histogram
            __IMSHOW_PRIMARY_DICT = __plot_image(image_primary_dict['data'],
                                                 2**image_primary_dict['bitsperpixel']-1,
                                                 __GUI_DICT['cam_plot_primary_dict']['image_axes'],
                                                 __IMSHOW_PRIMARY_DICT)

    except: # pylint: disable=bare-except
        if __STREAM:
            # Only re-raise error if stream is still enabled
            raise

# -------------- #
# Start gui      #
# -------------- #

def main():
    """ Main program """
    global __QUEUE
    global __STREAM
    global __IMSHOW_PRIMARY_DICT
    global __GUI_DICT

    # Set GUI
    __GUI_DICT = __stereo_gui()

    # Update plot while figure exists
    while plt.fignum_exists(__GUI_DICT['fig'].number): # pylint: disable=unsubscriptable-object
        try:
            # Handle streams
            if __STREAM:
                __stream_images()

            # Handle queue
            while not __QUEUE.empty():
                func, args, kwargs = __QUEUE.get()
                func(*args, **kwargs)

            # Update plot
            plt.pause(sys.float_info.min)
        except: # pylint: disable=bare-except
            if plt.fignum_exists(__GUI_DICT['fig'].number):
                # Only re-raise error if figure is still open
                raise

    # Clean up
    __QUEUE = queue.Queue()
    __STREAM = False
    __IMSHOW_PRIMARY_DICT = {'imshow': None, 'imshow_size': None}
    __GUI_DICT = None

    print('Exiting...')

    return 0

if __name__ == '__main__':
    sys.exit(main())
