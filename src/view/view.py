"""
This is the view package. The view should handle all the operation made on the image, including the displaying of this one.
Nonetheless, this task is shared with the controller package. This last one is globally in control of the view package.
"""
import wx
import cv2
import numpy as np
from src.controller import constants as cst


class View:
    def __init__(self, controller):
        self.c = controller

    def constructImageScrollable(self, frame):
        # cv2.cvtColor(image, image, cv2.COLOR_BGR2RGB)
        scrollpanel = self.c.mainCanvas.central_panel

        height, width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        bmp = wx.BitmapFromBuffer(width, height, frame)
        imageBitmap = wx.StaticBitmap(scrollpanel, wx.ID_ANY, bmp)

        self.sc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sc_sizer.AddStretchSpacer()
        self.sc_sizer.Add(imageBitmap, 0, wx.CENTER)
        self.sc_sizer.AddStretchSpacer()

        scrollpanel.SetSizer(self.sc_sizer)
        scrollpanel.SetScrollbars(20, 20, height / 20, width / 20)
        scrollpanel.Refresh()

    def clearImage(self):
        if self.sc_sizer.GetChildren():
            self.sc_sizer.Hide(1)
            self.sc_sizer.Remove(1)


class ScrollableImage(wx.ScrolledWindow):
    def __init__(self, parent, size, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, parent=parent, size=size,style=wx.BORDER_RAISED, *args, **kwargs)

        self.parent = parent
        self.bmp = None
        self.imageBitmap = None
        self.icon_image = None
        self.numpyImage = None
        self.chan_image = dict()

    def constructImageScrollable(self, image):

        self.numpyImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width = image.shape[:2]

        self.bmp = wx.BitmapFromBuffer(width, height, self.numpyImage)
        self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, self.bmp)
        self.sc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sc_sizer.AddStretchSpacer()
        self.sc_sizer.Add(self.imageBitmap, 0, wx.CENTER)
        self.sc_sizer.AddStretchSpacer()



        self.SetSizer(self.sc_sizer)
        self.SetScrollbars(20, 20, height / 20, width / 20)
        self.constructMiniatureChan()
        self.Refresh()

    def updateView(self):
        frame = cv2.cvtColor(self.numpyImage, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]

    def scale_bitmap(self, bitmap, width, height):


        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def constructMiniatureChan(self):
        if self.numpyImage.shape[2] == 3:
            size = cst.ICON_SIZE
            img = cv2.resize(self.numpyImage, (size,size))

            r_chan = np.zeros((size,size,3), dtype=np.uint8)
            r_chan[:,:,0] = img[:,:,0]
            g_chan = np.zeros((size, size, 3), dtype=np.uint8)
            g_chan[:, :, 1] = img[:, :, 1]
            b_chan = np.zeros((size,size,3), dtype=np.uint8)
            b_chan[:,:,2] = img[:,:,2]
            self.chan_image['r_chan'] = r_chan
            self.chan_image['b_chan'] = b_chan
            self.chan_image['g_chan'] = g_chan

        self.icon_image = self.scale_bitmap((self.bmp), 20, 20)

