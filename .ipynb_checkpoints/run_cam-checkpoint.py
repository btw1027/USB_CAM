import matplotlib
matplotlib.use('TkAgg') #crashes when using %matplotlib qt
import numpy
from matplotlib import pyplot as plt
import PySpin
from datetime import datetime
import os
import math

def list_object_parameters(obj):
    import inspect
    return [a[0] for a in inspect.getmembers(obj)]

def is_param_in_object(param, obj):
    import inspect
    params = [a[0] for a in inspect.getmembers(obj)]
    return param in params

def set_custom_cam_settings(cam, **kwargs):
    params = list_object_parameters(cam)
    try:
        result = True
        for k, v in kwargs.items():
            if (k in params) and (getattr(cam,k).GetAccessMode() == PySpin.RW):
                if k == 'Width':
                    getattr(cam, k).SetValue(v)
                    print('Setting', k, '=', v)
                    cam.OffsetX.SetValue(int((5472-v)/2))
                    print('Setting OffsetX =', (5472-v)/2)
                elif k == 'Height':
                    getattr(cam, k).SetValue(v)
                    print('Setting', k, '=', v)
                    cam.OffsetY.SetValue(int((3648-v)/2))
                    print('Setting OffsetY =', (3648-v)/2)
                else: 
                    getattr(cam, k).SetValue(v)
                    print('Setting', k, '=', v)
            else:
                print(k, 'is not a parameter of this object or not accessible')
                result = False
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
    return result

def acquire_images(cam, num_images):
    try:
        result = True
        # Set acquisition mode to continuous
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print('Unable to set acquisition mode to continuous. Aborting...')
            return False
        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        # Begin acquiring images
        cam.BeginAcquisition()
        print('Acquiring images...')
        
        for i in range(num_images):
            try:
                # Retrieve next received image and ensure image completion
                image_result = cam.GetNextImage()
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d...' % image_result.GetImageStatus())
                else:
                    image = image_result.GetNDArray()
                    fig, current_ax = plt.subplots(figsize=(10,10))                
                    plt.imshow(image, cmap='gray')
                    plt.show()
                    ld = LineDrawer()
                    ld.draw_line() # here you click on the plot
                    

                # Release image
                image_result.Release()
            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                result = False
        # End acquisition
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def run_cam(params, num_images=1):
    result = True
    # Get system
    system = PySpin.System.GetInstance()
    # Get camera list
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()
    print('Number of cameras detected: %d' % num_cameras)
    # Finish if there are no cameras
    if num_cameras == 0:
        # Clear camera list before releasing system
        cam_list.Clear()
        # Release system instance
        system.ReleaseInstance()
        print('Not enough cameras!')
        return False
    
    cam = cam_list.GetByIndex(0)
    try: 
        # Initialize camera
        cam.Init()
        # Configure camera settings
        set_custom_cam_settings(cam, **params)
        # Acquire images
        result &= acquire_images(cam, num_images)
        
        set_custom_cam_settings(cam, ExposureAuto=True, GainAuto=True)
        # Deinitialize camera
        cam.DeInit()
        return result

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False
    
    del cam
    cam_list.Clear()
    system.ReleaseInstance()
    return result

class LineDrawer(object):
    lines = []
    def draw_line(self):
        ax = plt.gca()
        xy = plt.ginput(2)        
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = plt.plot(x,y)
        ax.figure.canvas.draw()
        self.lines.append(line)
        distance = math.sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2)
        distance_s = '%4.3f' % distance
        bbox_props = dict(boxstyle="round,pad=0.3", ec="b", lw=2)
        t = ax.text(0, 0, 'The distance is '+distance_s+' px', ha="center", va="center", size=15,bbox=bbox_props)
#         ax.annotate('The distance is '+distance_s+' px', (0,0), horizontalalignment='right', verticalalignment='top')
        print('The distance in pixels is %4.3f' % distance)
        
#max width = 5472
#max height = 3648

params = {
    'Width': 912,
    'Height': 1824,
    'AcquisitionFrameRateEnable': True,
    'AcquisitionFrameRate': 3,
    'ExposureAuto': False,
    'ExposureTime': 15000,
    'GainAuto': False,
    'Gain': 6.29
}

run_cam(params, 1)