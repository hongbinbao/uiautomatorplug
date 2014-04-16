uiautomatorplug
===============

enhancement for the python implement of android uiautomator. provide image comparision


#### Installation
     sudo pip install uiautomatorplug
    
#### Dependency
    1: sudo apt-get install python-opencv
    2: sudo apt-get install python-numpy
    3: target android device: sdk_version>=16

#### Usage
    >>> from uiautomatorplug.android import device as d
    >>> d.info
    >>> d.orientation
    >>> d.orientation = 'l'
    >>> d.wakeup()
    >>> d.start_activity(action='android.intent.action.DIAL', data='tel:xxxx', flags=0x04000000)
    >>> d.find('phone_launch_success.png')
    >>> d.click(100, 200)
    >>> d.click('DPAD_NUMBER_1.png')
    >>> d.click('DPAD_NUMBER_1.png', rotation=90)
    >>> d.exists(text='string_value_of_screen_layout_component_text_attribute')
    >>> d.expect('phone_launch_success.png')
    >>> d(text='Settings').click()
