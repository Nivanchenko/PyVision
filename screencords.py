import screeninfo
import time
import subprocess as sp
import numpy
import cv2
from pynput.mouse import Listener

down_x = down_y = up_x = up_y = -1

def on_click(x, y, button, pressed):
    global down_x
    global down_y
    global up_x
    global up_y
    if pressed:
        (down_x, down_y) = (x, y)
    else:
        (up_x, up_y) = (x, y)
        return False

def get_cords():
    global down_x
    global down_y
    global up_x
    global up_y
    print('u have about 3 seconds, press q and draw rectangle')
    time.sleep(1)
    mon = screeninfo.get_monitors()[0]
    print(mon.height)
    print(mon.width)
    command = [ 'ffmpeg',
                '-video_size', '{}x{}'.format(mon.width, mon.height), '-framerate', '15',
                '-f', 'x11grab', '-i', ':0.0',
                '-f', 'image2pipe',
                '-pix_fmt', 'rgb24',
                '-vcodec', 'rawvideo', '-']

    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

    raw_image = pipe.stdout.read(mon.width * mon.height * 3)
    # transform the byte read into a numpy array
    image =  numpy.fromstring(raw_image, dtype='uint8')
    image = image.reshape((mon.height, mon.width, 3))
    cv2.namedWindow ('screen', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty ('screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('screen', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #pipe.stdout.flush()
    while True:
        if cv2.waitKey(25) & 0xFF == ord('q'):
            with Listener(on_click=on_click) as listener:
                listener.join()
            cv2.destroyAllWindows()
            break
    return down_x, down_y, up_x, up_y

if __name__ == '__main__':
    crd = get_cords()
    print(crd)
