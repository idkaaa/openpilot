import av
import cv2 as cv
import time
import threading
import queue

# bufferless VideoCapture: https://stackoverflow.com/a/69141497
# https://spin.atomicobject.com/frame-buffering-opencv/

class Camera:
  def __init__(self, cam_type_state, stream_type, camera_id):
    self.camera_id = camera_id
    try:
      self.camera_id = int(camera_id)
    except ValueError: # allow strings, ex: /dev/video0
      pass


    self.cam_type_state = cam_type_state
    self.stream_type = stream_type
    self.cur_frame_id = 0

    print(f"Opening {cam_type_state} at {camera_id}")

    self.cap = cv.VideoCapture(camera_id)

    self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920.0)
    self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080.0)
    # self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280.0)
    # self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720.0)
    self.cap.set(cv.CAP_PROP_FPS, 30.0)
    self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))


    self.W = self.cap.get(cv.CAP_PROP_FRAME_WIDTH)
    self.H = self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)

    #Starting camera thread
    self.q = queue.Queue()
    self.t = threading.Thread(target=self._reader)
    self.t.daemon = True
    self.t.start()


  @classmethod
  def bgr2nv12(self, bgr):
    frame = av.VideoFrame.from_ndarray(bgr, format='bgr24')
    return frame.reformat(format='nv12').to_ndarray()

  # grab frames as soon as they are available
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        raise Exception("Could not read frame.")
      if not self.q.empty():
        try:
          self.q.get_nowait()  # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  # retrieve latest frame
  def read(self):
      return self.q.get()

  def read_frames(self):

    # Number of frames to capture
    # num_frames = 240
    # start = time.time()
    # print("Camera[{0}]:".format(self.camera_id))
    # fps = self.cap.get(cv.CAP_PROP_FPS)
    # print("Frames per second using video.get(cv.CAP_PROP_FPS) : {0}".format(fps))
    # print("Capturing {0} frames".format(num_frames))
    while True:
      frame = self.read()
      if frame is None:
        print("unable to retrieve frame")
        break

      # if self.cur_frame_id == num_frames-1:
      #   print("end time")
      #   # End time
      #   end = time.time()
      #   print("Camera[{0}]:".format(self.camera_id))
      #   # Time elapsed
      #   seconds = end - start
      #   print ("Time taken : {0} seconds".format(seconds))

      #   # Calculate frames per second
      #   fps  = num_frames / seconds
      #   print("Estimated frames per second : {0}".format(fps))


      # Rotate the frame 180 degrees (flip both axes)
      #frame = cv.flip(frame, -1)
      #cv.resize(frame, (1280, 720), dst=frame, interpolation=cv.INTER_LINEAR)
      yuv = Camera.bgr2nv12(frame)
      yield yuv.data.tobytes()
    self.cap.release()
    print("finished camera thread")









