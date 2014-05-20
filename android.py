#!/usr/bin/python
# -*- coding:utf-8 -*- 

import os, sys, time, types, shutil
from os.path import join, exists
from commands import getoutput as shell
from comparison import isMatch, getMatchedCenterOffset
from uiautomator import Device
import inspect

__all__ = ['device', 'ExpectException']

ANDROID_SERIAL = 'ANDROID_SERIAL'
DEFAULT_RIGHT_DIR_NAME = 'pics'
DEFAULT_REPORT_DIR_NAME = 'tmp'
WORKING_DIR_PATH = os.getcwd()
REPORT_DIR_PATH = join(WORKING_DIR_PATH, DEFAULT_REPORT_DIR_NAME)
#RIGHT_DIR_PATH = join(WORKING_DIR_PATH, DEFAULT_RIGHT_DIR_NAME)

class AndroidDevice(object):
    '''
    wrapper for android uiautomator-server binding(pip install uiautomator).
    provide android device event inject, ui object inspect and image comparison.
    '''

    def __init__(self, seral=None):
        '''
        create device instance.
        '''
        self.serial = os.environ[ANDROID_SERIAL] if os.environ.has_key(ANDROID_SERIAL) else None
        self.working_dir_path = WORKING_DIR_PATH
        self.report_dir_path = REPORT_DIR_PATH
        self.right_dir_path = WORKING_DIR_PATH
        self.d = Device(self.serial)
        #try:
        #    if int(self.d.info['sdkInt']) <= 17:
        #        self.d.screenshot = self.screenshot_common
        #except:
        #    pass

    def __getattr__(self, attr):
        '''
        forward method/attrbuite to uiautomator device if method support by uiautomator.
        '''
        if hasattr(self.d, attr):
            if attr == 'screenshot':
                return self.screenshot_common
            m =  getattr(self.d, attr)
            if inspect.ismethod(m):
                def wrapper(*args, **kwargs):
                    return m(*args, **kwargs)
                return wrapper
            else:
                return m
        raise AttributeError(attr)

    def __call__(self, *args, **kwargs):
        '''
        selector support:
        d(text="Settings").click()
        '''
        return self.d(*args, **kwargs)

    @property
    def orientation(self):
        return self.d.orientation

    @orientation.setter
    def orientation(self, v):
        self.d.orientation = v

    def serial(self):
        '''
        device serial number from $ANDROID_SERIAL
        '''
        return self.serial

    def sleep(self, sec):
        time.sleep(sec)

    #device event inject
    def start_activity(self, **intent_params):
        '''
        Starts an Activity on the device by sending an Intent which constructed from the specified parameters.     
        The params of Intent supported from adb docs:
        <INTENT> specifications include these flags:
            [-a <ACTION>] [-d <DATA_URI>] [-t <MIME_TYPE>]
            [-c <CATEGORY> [-c <CATEGORY>] ...]
            [-e|--es <EXTRA_KEY> <EXTRA_STRING_VALUE> ...]
            [--esn <EXTRA_KEY> ...]
            [--ez <EXTRA_KEY> <EXTRA_BOOLEAN_VALUE> ...]
            [-e|--ei <EXTRA_KEY> <EXTRA_INT_VALUE> ...]
            [-n <COMPONENT>] [-f <FLAGS>]
            [<URI>]
        @type intent_params: dictionary 
        @param intent_params: the properties of an Intent. 
                              property support: component/action/data/mimetype/categories/extras/flags/uri
        @rtype: AndroidDevice
        @return: a instance of AndroidDevice.
        '''
        
        #d.server.adb.cmd('shell','am', 'start', '-a', 'android.intent.action.DIAL','tel:13581739891').communicate()
        #sys.stderr.write(str(intent_params))
        keys = intent_params.keys()
        shellcmd = ['shell', 'am', 'start']
        if 'component' in keys:
            shellcmd.append('-n')
            shellcmd.append(intent_params['component'])

        if 'action' in keys:  
            shellcmd.append('-a')
            shellcmd.append(intent_params['action'])

        if 'data' in keys:
            shellcmd.append('-d')
            shellcmd.append(intent_params['data'])

        if 'mimetype' in keys:
            shellcmd.append('-t')
            shellcmd.append(intent_params['mimetype'])

        if 'categories' in keys:
            for category in intent_params['categories']:
                shellcmd.append('-c')
                shellcmd.append(category)
        
        if 'extras' in keys:
            for extra_key, extra_value in intent_params['extras'].items():
                str_value = ''
                arg = ''
                if isinstance(extra_value, types.IntType):
                    str_value = str(extra_value)
                    arg = '--ei'
                elif isinstance(extra_value, types.BooleanType):
                    str_value = str(extra_value)
                    arg = '--ez'
                else:
                    str_value = str(extra_value)
                    arg = '--es'
                shellcmd.append(arg)
                shellcmd.append(extra_key)
                shellcmd.append(str_value)
                
        if 'flags' in keys:
            shellcmd.append('-f')
            shellcmd.append(str(intent_params['flags']))

        if 'uri' in keys:
            shellcmd.append(intent_params['uri'])

        if 'package' in keys:
            shellcmd.append(intent_params['package'])
        #sys.stderr.write(str(shellcmd))            
        self.d.server.adb.cmd(*shellcmd).communicate()
        return self

    def instrument(self, **kwargs):
        '''
        Run the specified package with instrumentation and return the output it generates. 
        Use this to run a test package using InstrumentationTestRunner.
        Typically this target <COMPONENT> is the form <TEST_PACKAGE>/<RUNNER_CLASS>. 
        Options are:
        -w: wait for instrumentation to finish before returning. Required for test runners.
        -r: print raw results (otherwise decode REPORT_KEY_STREAMRESULT).
            Use with [-e perf true] to generate raw output for performance measurements.
        -e <NAME> <VALUE>: set argument <NAME> to <VALUE>.
            For test runners a common form is [-e <testrunner_flag> <value>[,<value>...]].
        -p <FILE>: write profiling data to <FILE>
        --user <USER_ID> | current: Specify user instrumentation runs in; current user if not specified.
        --no-window-animation: turn off window animations will running.

        @type intent_params: dictionary 
        @param intent_params: the properties of an instrumentation testing. 
                              property support: packagename, <NAME> to <VALUE>.
        @rtype: AndroidDevice
        @return: a instance of AndroidDevice.
        '''
        keys = kwargs.keys()
        shellcmd = ['shell', 'am', 'instrument', '-w', '-r']
        pkgname = kwargs.pop('packagename')
        for k, v in kwargs.items():
            if k and v:
                shellcmd.append('-e')
                shellcmd.append(k)
                shellcmd.append(str(v))
        shellcmd.append(pkgname)
        result = self.d.server.adb.cmd(*shellcmd).communicate()
        return result

    def click(self, *args, **kwargs):
        '''
        example:
         click(x,y)
         Click the screen location specified by x and y.
         Format: (x,y) the screen location specified by x and y.
         x   The horizontal position of the touch in actual device pixels, starting from the left of the screen in its current orientation.
         y   The vertical position of the touch in actual device pixels, starting from the top of the screen in its current orientation.
        
        click('phone_app.png', rotation=90)
        
        Perform a click event on the center point on the expected screen region.
        If the screen region want to click not found in the current screen snapshot will do nothing
        rotation: 0, 90, 180, 270
        '''
        if args:
            if isinstance(args[0], types.IntType):
                self.__click_point(*args, **kwargs)
                return self
            if isinstance(args[0], types.StringType):
                self.__click_image(*args, **kwargs)
                return self

    def __click_point(self, x, y, waittime=1):
        '''
        click x,y
        '''
        self.d.click(x, y)
        time.sleep(waittime)

    def __click_image(self, imagename, waittime=1, threshold=0.01, rotation=0):
        '''
        if the wanted image found on current screen click it.
        if the wanted image not found raise exception and set test to be failure.
        '''
        expect_image_path = None
        current_image_path = None
        if os.path.isabs(imagename):
            expect_image_path = imagename
            current_image_path = join(self.report_dir_path, os.path.basenme(imagename))
        else:
            expect_image_path = join(self.right_dir_path, imagename)
            current_image_path = join(self.report_dir_path, imagename)       

        assert os.path.exists(expect_image_path), 'the local expected image %s not found!' % expect_image_path

        self.d.screenshot(current_image_path)
        assert os.path.exists(current_image_path), 'fetch current screen shot image %s failed!' % imagename
        pos = getMatchedCenterOffset(subPath=expect_image_path, srcPath=current_image_path, threshold=0.01, rotation=rotation)
        if not pos:
            reason = 'Fail Reason: The wanted image \'%s\' not found on screen!' % imagename
            raise ExpectException(expect_image_path, current_image_path, reason)
        self.d.click(pos[0], pos[1])
        time.sleep(waittime)

    def screenshot_common(self, filename):
        '''
        if SK version <= 16
        Capture the screenshot via adb and store it in the specified location.
        '''
        png = os.path.basename(filename)
        if self.serial:
            shell('adb -s %s shell screencap /sdcard/%s' % (self.serial, png))
            shell('adb -s %s pull /sdcard/%s %s' % (self.serial, png, filename))
        else:
            shell('adb shell screencap /sdcard/%s' % png)
            shell('adb pull /sdcard/%s %s' % (png, filename))
        return True

    #inspect
    def exists(self, **kwargs):
        '''
        if the expected component exists on current screen layout return true else return false.
        '''
        return self.d.exists(**kwargs)

    def expect(self, imagename, interval=2, timeout=4, threshold=0.01, msg=''):
        '''
        if the expected image found on current screen return self 
        else raise exception. set test to be failure.
        '''
        expect_image_path = None
        current_image_path = None
        if os.path.isabs(imagename):
            expect_image_path = imagename
            current_image_path = join(self.report_dir_path, os.path.basenme(imagename))
        else:
            expect_image_path = join(self.right_dir_path, imagename)
            current_image_path = join(self.report_dir_path, imagename)       

        assert os.path.exists(expect_image_path), 'the local expected image %s not found!' % expect_image_path
        begin = time.time()
        while (time.time() - begin < timeout):
            self.d.screenshot(current_image_path)
            if isMatch(expect_image_path , current_image_path , threshold):
                return self
            time.sleep(interval)
        reason = msg if msg else 'Fail Reason: Image \'%s\' not found on screen!' % imagename
        raise ExpectException(expect_image_path, current_image_path, reason)

    def find(self, imagename, interval=2, timeout=4, threshold=0.01):
        '''
        if the expected image found on current screen return true else return false
        '''
        expect_image_path = None
        current_image_path = None
        if os.path.isabs(imagename):
            expect_image_path = imagename
            current_image_path = join(self.report_dir_path, os.path.basenme(imagename))
        else:
            expect_image_path = join(self.right_dir_path, imagename)
            current_image_path = join(self.report_dir_path, imagename)       

        assert os.path.exists(expect_image_path), 'the local expected image %s not found!' % expect_image_path

        begin = time.time()
        isExists = False
        while (time.time() - begin < timeout):
            time.sleep(interval)
            self.d.screenshot(current_image_path)
            isExists = isMatch(expect_image_path , current_image_path , threshold)
            if not isExists:
                time.sleep(interval)
                continue
        return isExists

    def TODOinstallPackage(self, **kwargs):
        pass

    def TODOremovePackage(self, **kwargs):
        pass

class ExpectException(AssertionError):
    '''A custom exception will be raised by AndroidDevice.'''
    def __init__(self, expect, current, msg):
        AssertionError.__init__(self)
        self.expect = expect
        self.current = current
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

device = AndroidDevice()





































