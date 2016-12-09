import wx
from src.model import model
from src.view import view
import constants as cst
import numpy as np


class Controller(wx.Frame):
    def __init__(self, *args, **kwargs):
        """
        This is the main and mother class. There should be only one instance of this class.
        :param args:
        :param kwargs:
        """

        wx.Frame.__init__(self, parent=None, title="Image manipulator", *args, **kwargs)
        filemenu = wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "About", "Information about this program")
        filemenu.AppendSeparator()
        menuOpen = filemenu.Append(wx.ID_ABOUT, "Open image...", "")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "Exit", "Terminate the program")

        # Setting up the edit menu.
        editmenu = wx.Menu()

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "File")  # Adding the "filemenu" to the MenuBar
        menuBar.Append(editmenu, "Edit")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Initializing instance of framework
        self.model = model.Model(self)
        self.view = view.View(self)

        # Creating canvas
        self.list_canvas = []
        self.notebook = NotebookCanvas(self, self)
        self.activeCanvas = 0

        # Creating tool window

        self.tool = ToolWindow(self)
        self.Layout()

        # Bind on event
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Maximize()
        self.Show(True)

    def call_warning(self, warning_attribute):
        """
        This function is called every time a warning or error message is triggered
        :param warning_attribute: The signature of the warning message. It should be an integer. The harsh table is defined in constants.py
        :return:
        """
        def existing_image():
            print 'Existing image will be erased'
            # Todo Implement a correct warning dialog and offer choice (erase or build a new window

        def foo():
            print "Not implemented"

        def bar():
            print "Not implemented"

        options = {0: existing_image,
                   1: foo,
                   2: bar
                   }

        options[warning_attribute]()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.

        dlg = wx.MessageDialog(self, "Started on a cold night, 11/16/2016", "About GraphSound", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

    def OnOpen(self, e=None):
        """
            Open an image
        """
        if self.model.currentFile['image'] is None:
            dlg = wx.FileDialog(self, "Choose a file", self.model.default_source, "", "*.*")
            if dlg.ShowModal() == wx.ID_OK:
                self.model.currentFile['filename'] = dlg.GetFilename()
                self.model.currentFile['dirname'] = dlg.GetDirectory()
                self.model.openNewFile()
            dlg.Destroy()
        else:
            self.model.openNewFile()

    def constructNewCanvas(self, image, name):
        """
        This function creates a new canvas, shown as a new tab in the notebook panel.
        :param image:
        :param name:
        :return:
        .. todo: rename  the function in order to respect PEP-8
        """

        new_canvas = CanvasPanel(self.notebook, controller=self)
        self.list_canvas.append(new_canvas)

        new_canvas.scrollable_panel.constructImageScrollable(image=image)

        self.notebook.AddPage(new_canvas, name, select=True)

        # Construct the image icon visible on the tab
        idx1 = self.notebook.il.Add(new_canvas.scrollable_panel.icon_image)
        self.notebook.SetPageImage(len(self.list_canvas) - 1, idx1)
        self.tool.Show(True)
        self.Layout()


class CanvasPanel(wx.Panel):
    def __init__(self, parent, controller, *args, **kwargs):
        """
        This is by default the center panel, located in the center of the main frame. This panel contains a notebook panel,
        each tab corresponding to a new image opened.
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
        self.scrollable_panel = view.ScrollableImage(self, size=tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)))
        self.scrollable_panel.SetBackgroundColour('white')
        self.scrollable_panel.SetMinSize(tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)))
        self.scrollable_panel.SetScrollbars(1, 1, 1, 1)
        self.scrollable_panel.EnableScrolling(True, True)
        sizer.Add(self.scrollable_panel, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        self.scrollable_panel.Show(True)


class NotebookCanvas(wx.Notebook):
    def __init__(self, parent, controller, *args, **kwargs):
        self.c = controller

        screen_size = wx.GetDisplaySize()
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, size=tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)),
                             style=
                             wx.BK_DEFAULT,
                             # wx.BK_TOP
                             # wx.BK_BOTTOM
                             # wx.BK_LEFT
                             # wx.BK_RIGHT)
                             *args, **kwargs)

        self.il = wx.ImageList(16, 16)
        self.AssignImageList(self.il)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onpagechanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onpagechanging)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMClick)

    def onpagechanged(self, event):
        sel = self.GetSelection()
        self.c.activeCanvas = self.c.list_canvas[sel]
        chan_dict = self.c.activeCanvas.scrollable_panel.chan_image
        self.c.tool.build_chanel_selector(chan_dict)
        event.Skip()

    def onpagechanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnMClick(self, event):
        """right-click event handler"""

        mousePos = event.GetPosition()
        pageIdx, other = self.HitTest(mousePos)
        del self.c.list_canvas[pageIdx]
        self.DeletePage(pageIdx)


class ToolWindow(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        """
        A lateral window, which containes most of the quick access to tools.
        By default, the size of this window is defined as a fraction of the main window. This fraction is precised in
        the constants.py package.

        The default behaviour is to put this window always on top.


        The frame contains a notebook panel, each tab corresponding to a particular option.
        :param parent:
        :param args:
        :param kwargs:

        .. todo:: Correct the window behaviour: it should be on top of the main window, but only of the current app.
        .. todo:: There should be the possibility to close and re-open this window

        """
        width, height = wx.GetDisplaySize()
        wx.Frame.__init__(self, parent=parent,
                          size=(width * cst.TOOL_WINDOW__WIDTH_RATIO, height * cst.TOOL_WINDOW__HEIGHT_RATIO),
                          title='Tools',
                          style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
                          *args, **kwargs)

        self.SetPosition((width - 2 * (width * cst.TOOL_WINDOW__WIDTH_RATIO), height / 8))

        self.notebookMenu = wx.Notebook(self, style=wx.BK_DEFAULT)
        self.notebookMenu.SetBackgroundColour('white')
        self.panelChanel = wx.Panel(self.notebookMenu)
        self.panelChanel.SetBackgroundColour('white')
        self.notebookMenu.AddPage(self.panelChanel, 'Channels')
        self.panelChanel.Show(True)
        self.notebookMenu.Show(True)
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.Show(False)

    def build_chanel_selector(self, chan_dict):
        """
        This function updates the panel displaying the different chanels.
        Notes that this function includes a class definition.
        :param chan_dict:
        :return:
        """
        children = self.topsizer.GetChildren()
        for child in children:
            widget = child.GetWindow()
            widget.Destroy()

        r = self.ChanPanel(self.panelChanel, img=chan_dict['r_chan'], title='Red')
        g = self.ChanPanel(self.panelChanel, img=chan_dict['g_chan'], title='Green')
        b = self.ChanPanel(self.panelChanel, img=chan_dict['b_chan'], title='Blue')
        self.topsizer.Add(r, 0, wx.ALL | wx.EXPAND, 5)
        self.topsizer.Add(g, 0, wx.ALL | wx.EXPAND, 5)
        self.topsizer.Add(b, 0, wx.ALL | wx.EXPAND, 5)
        self.panelChanel.SetSizer(self.topsizer)
        self.panelChanel.Layout()

    class ChanPanel(wx.Panel):
        def __init__(self, parent, img, title):
            wx.Panel.__init__(self, parent)
            self.SetBackgroundColour('white')
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.show_button = wx.Button(self, label=title, size=(30, 30))
            self.bmp = wx.BitmapFromBuffer(img.shape[1], img.shape[0], img)
            self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, self.bmp)
            self.sizer.Add(self.show_button, 1, wx.ALL, 5)
            self.sizer.Add(self.imageBitmap, 0, wx.ALL, 5)

            self.SetSizer(self.sizer)
            self.Show(True)
