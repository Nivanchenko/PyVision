import subprocess as sp
import numpy
import cv2
import screencords as sc

def draw_lines(img,lines):
    for line in lines:
        coords = line[0]
        cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)

def process_img(image):
    original_image = image
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edge detection
    processed_img =  cv2.Canny(processed_img, threshold1 = 200, threshold2=300)
    # more info: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    #                          edges       rho   theta   thresh         # min length, max gap:        
#    lines = cv2.HoughLinesP(processed_img, 1, numpy.pi/180, 180,      20,         15)
#    print('{} {}'.format(lines, type(lines)))
#    draw_lines(processed_img,lines)
    return processed_img

def main():
    down_x, down_y, up_x, up_y = sc.get_cords()
    x = min(down_x, up_x)
    y = min(down_y, up_y)
    x2 = max(down_x, up_x)
    y2 = max(down_y, up_y)
    width = x2-x
    heigh = y2-y

    command = [ 'ffmpeg',
                '-video_size', '{}x{}'.format(width, heigh), '-framerate', '15',
                '-f', 'x11grab', '-i', ':0.0+{},{}'.format(down_x, down_y),
                '-f', 'image2pipe',
                '-pix_fmt', 'rgb24',
                '-vcodec', 'rawvideo', '-']

    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

    #for i in range(1000):
    while True:
        raw_image = pipe.stdout.read(width * heigh * 3)
        # transform the byte read into a numpy array
        image =  numpy.fromstring(raw_image, dtype='uint8')
        image = image.reshape((heigh, width, 3))

        raw_image = pipe.stdout.read(width * heigh * 3)
        # transform the byte read into a numpy array
        image2 =  numpy.fromstring(raw_image, dtype='uint8')
        image2 = image2.reshape((heigh, width, 3))
        diff = cv2.absdiff(image, image2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        denoised = cv2.fastNlMeansDenoisingColored(diff,None,10,10,7,21)
        #denoised = thresh
        #dilated = cv2.dilate(denoised, None, iterations=4)
        #dilated = thresh
       # contours, hirarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
       # for contour in contours:
       #     (x, y, w, h) = cv2.boundingRect(contour)
       #     if cv2.contourArea(contour) < 700:
       #         continue
       #     cv2.rectangle(image2, (x, y), (x+w, y+h), (0, 255, 255), 2)



        cv2.imshow('window', cv2.cvtColor(image2, cv2.COLOR_BGR2RGB))
        cv2.imshow('windowdiff', cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
        pipe.stdout.flush()
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

main()
