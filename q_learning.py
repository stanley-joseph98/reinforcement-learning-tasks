from pyvirtualdisplay import Display
from easyprocess import EasyProcess

# Start the virtual display
with EasyProcess(['C:\\Users\\USER\Desktop\\ALL MY TASKS\\TSI DATA SCIENCE\\Machine Learning\\reinforcementLearning\\.venv\Lib\site-packages\\xvfbwrapper-0.2.9.dist-info']):
    virtual_display = Display(visible=0, size=(1400, 900))
    virtual_display.start()
