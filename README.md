uiautomatorplug
===============

enhancement for the python implement of android uiautomator JSON RPC client. and provide image comparision feature.


#### Installation
     sudo pip install uiautomatorplug
    
#### Dependency
    1: sudo pip install uiautomator (https://github.com/xiaocong/uiautomator/blob/master/uiautomator.py).
    2: sudo apt-get install python-opencv
    3: sudo apt-get install python-numpy
    4: target android device: sdk_version>=16

#### Usage
    >>> from uiautomatorplug.android import device as d
    >>> d.info
    >>> d.orientation
    >>> d.orientation = 'l'
    >>> d.wakeup()
    >>> d.start_activity(action='android.intent.action.DIAL', data='tel:xxxx', flags=0x04000000)
    >>> d.find('path/phone_launch_success.png')
    >>> d.click(100, 200)
    >>> d.click('path/DPAD_NUMBER_1.png')
    >>> d.click('path/DPAD_NUMBER_1.png', rotation=90)
    >>> d.exists(text='string_value_of_screen_layout_component_text_attribute')
    >>> d.expect('path/phone_launch_success.png')
    >>> d(text='Settings').click()
    
#### tips
    the screenshot of android device will be captured into device's '/sdcard/' folder as default.
    to change the screenshot saving path on device to be your device real storage path:
    
    from uiautomatorplug.android import device as d
    d.set_internal_storage_dir('/storage/sdcard1/')
     
