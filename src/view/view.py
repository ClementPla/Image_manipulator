"""
This is the view package. The view should handle all the operation made on the image, including the displaying of this one.
Nonetheless, this task is shared with the controller package. This last one is globally in control of the view package.
"""
import wx
import cv2
import numpy as np
from src.controller import constants as cst

import wx.lib.statbmp


class ScrollableImage(wx.ScrolledWindow):
    def __init__(self, parent, size, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, parent=parent, size=size, style=wx.BORDER_RAISED | wx.BG_STYLE_PAINT, *args,
                                   **kwargs)

        self.parent = parent
        self.bmp = None
        self.imageBitmap = None
        self.icon_image = None
        self.chan_image = dict()
        self.image_prop = dict()
        self.user_scale = 1
        self.img_size = tuple()

    def constructImageScrollable(self, image_prop):
        """
        :param image_prop: dictionary containing image's properties and model information (defined by the model)
        :return:
        """

        self.image_prop = image_prop
        image = self.image_prop['image']
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]
        self.img_size = (height, width)
        self.bmp = wx.BitmapFromBuffer(width, height, image)
        # self.imageBitmap = wx.lib.statbmp.GenStaticBitmap(self, wx.ID_ANY, self.bmp)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetScrollbars(20, 20, height / 20, width / 20)
        self.construct_miniature_chan()

        self.Bind(wx.EVT_KEY_DOWN, self.zoom_scale)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        """set up the device context (DC) for painting"""
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_VIRTUAL_AREA)
        dc.DestroyClippingRegion()

        #  Calculate visible region
        size_region = self.GetSize()
        view_start = self.CalcUnscrolledPosition(wx.Point(0, 0))
        dc.SetClippingRegion(view_start[0], view_start[1], size_region[0],
                             size_region[1])  # Clipping only the visible region
        self.OnSize(dc) #  Adjust size based on the user scale factor

    def Draw(self, dc):
        pass

    def OnSize(self, dc):
        dc.Clear()
        dc.SetUserScale(self.user_scale, self.user_scale)
        dc.DrawBitmap(self.bmp, 0, 0)

    def UpdateDrawing(self):
        """
        This would get called if the drawing needed to change, for whatever reason.

        The idea here is that the drawing is based on some data generated
        elsewhere in the system. If that data changes, the drawing needs to
        be updated.

        This code re-draws the buffer, then calls Update, which forces a paint event.
        """
        dc = wx.MemoryDC()
        dc.SelectObject(self.bmp)
        self.Draw(dc)
        del dc  # need to get rid of the MemoryDC before Update() is called.
        self.Refresh()
        self.Update()

    def zoom_scale(self, event):
        if event.GetKeyCode() == 388: #  Corresponds to the '+' on an alpha-numeric keyboard
            self.user_scale *= 1.5
            self.SetScrollbars(20, 20, self.img_size[0] * self.user_scale / 20, self.img_size[1] * self.user_scale / 20)
            self.UpdateDrawing()

        if event.GetKeyCode() == 390: #  Corresponds to the '-' on an alpha-numeric keyboard
            self.user_scale /= 1.5
            self.SetScrollbars(20, 20, self.img_size[0] * self.user_scale / 20, self.img_size[1] * self.user_scale / 20)
            self.UpdateDrawing()
        event.Skip()

    def scale_bitmap(self, bitmap, width, height):
        """
        Do rescale of an image
        :param bitmap:
        :param width:
        :param height:
        :return:
        """
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        return wx.BitmapFromImage(image)

    def construct_miniature_chan(self):
        """
        Builds a dictionary containing resized chanel (icon format) in form of a matrix.
        :return:
        """
        img = self.image_prop['image']
        if img.shape[2] == 3:
            size = cst.ICON_SIZE
            img = cv2.resize(img, (size, size))
            r_chan = np.zeros((size, size, 3), dtype=np.uint8)
            r_chan[:, :, 0] = img[:, :, 0]
            g_chan = np.zeros((size, size, 3), dtype=np.uint8)
            g_chan[:, :, 1] = img[:, :, 1]
            b_chan = np.zeros((size, size, 3), dtype=np.uint8)
            b_chan[:, :, 2] = img[:, :, 2]
            self.chan_image['r_chan'] = r_chan
            self.chan_image['b_chan'] = b_chan
            self.chan_image['g_chan'] = g_chan

        self.icon_image = self.scale_bitmap((self.bmp), 20, 20)


class CanvasPanel(wx.Panel):
    def __init__(self, parent, controller, *args, **kwargs):
        """
        This is by default the center panel, located in the center of the main frame.
        This one containes a scrollable panel, which contains the image displayed.
        The definition of the scrollable panel class is given in the view package, as it concerned the displaying of the image
        :param parent:
        :param controller:
        :param args:
        :param kwargs:

        It should be surely interesting to have an attribute indicating which canvas is the active one
        """
        wx.Panel.__init__(self, parent, *args, **kwargs)

        # Setting up the file menu.
        self.c = controller

        # Creating the scrollable panel
        screen_size = wx.GetDisplaySize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrollable_panel = ScrollableImage(self,
                                                size=tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)))
        self.scrollable_panel.SetBackgroundColour('white')
        # self.scrollable_panel.SetMinSize(tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)))
        self.scrollable_panel.SetScrollbars(1, 1, 1, 1)
        self.scrollable_panel.EnableScrolling(True, True)
        sizer.Add(self.scrollable_panel, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        self.scrollable_panel.Show(True)
