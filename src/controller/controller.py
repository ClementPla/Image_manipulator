import wx
from src.model import model
from src.view import view
import constants as cst
import wx.aui


class Controller(wx.Frame):
    def __init__(self, *args, **kwargs):
        """
        This is the main and mother class. There should be only one instance of this class.
        :param args:
        :param kwargs:
        """

        wx.Frame.__init__(self, parent=None, title="Image manipulator", *args, **kwargs)
        self.create_menubar()

        # Initializing instance of framework
        self.model = model.Model(self)

        # Creating canvas
        self.list_canvas = []
        self.notebook = NotebookCanvas(self, self)
        # Creating tool window
        self.tool = ToolWindow(self)

        self.Layout()
        self.Maximize()
        self.Show(True)

    def create_menubar(self):

        filemenu = wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "About", "Information about this program")
        filemenu.AppendSeparator()

        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU)
        menuOpen = wx.MenuItem(parentMenu=filemenu, id=wx.ID_OPEN, text="Open image...", kind=wx.ITEM_NORMAL)
        menuOpen.SetBitmap(open_bmp)
        filemenu.AppendItem(menuOpen)

        filemenu.AppendSeparator()

        exit_bmp = wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU)
        menuExit = wx.MenuItem(parentMenu=filemenu, id=wx.ID_EXIT)
        menuExit.SetBitmap(exit_bmp)
        filemenu.AppendItem(menuExit)

        # Setting up the edit menu.
        editmenu = wx.Menu()

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "File")  # Adding the "filemenu" to the MenuBar
        menuBar.Append(editmenu, "Edit")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Bind on event
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)
        self.Bind(wx.EVT_MENU, self.on_open, menuOpen)
        self.Bind(wx.EVT_MENU, self.on_exit, menuExit)

    @staticmethod
    def call_warning(warning_attribute):
        """
        This function is called every time a warning or error message is triggered
        Each warning is defined by its signature. Each signature will call a specific function.
        :param warning_attribute: The signature of the warning message; integer. The harsh table is defined in constants.py
        :return:
        """

        def existing_image():
            print "Warning ID: ", warning_attribute
            print 'Existing image will be erased'
            # Todo Implement a correct warning dialog and offer choice (erase or build a new window

        options = {0: existing_image,
                   }

        options[warning_attribute]()

    def on_about(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.

        dlg = wx.MessageDialog(self, "Started on a cold night, 11/16/2016", "About GraphSound", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def on_exit(self, e):
        self.Close(True)  # Close the frame.

    def on_open(self, e=None):
        """
            Open an image
        """
        if self.model.current_file['image'] is None:
            dlg = wx.FileDialog(self, "Choose a file", self.model.default_source, "", "*.*")
            if dlg.ShowModal() == wx.ID_OK:
                self.model.current_file['filename'] = dlg.GetFilename()
                self.model.current_file['dirname'] = dlg.GetDirectory()
                self.model.openNewFile()
                self.construct_new_canvas(self.model.current_file)
            dlg.Destroy()
        else:
            self.model.openNewFile()

    def construct_new_canvas(self, image_prop):
        """
        This function creates a new canvas, shown as a new tab in the notebook panel.
        :param image_prop: dictionary containing image's properties and model information (defined by the model)
        :param name:
        :return:
        .. todo: rename  the function in order to respect PEP-8
        """

        new_canvas = view.CanvasPanel(self.notebook, controller=self)
        self.list_canvas.append(new_canvas)
        new_canvas.scrollable_panel.constructImageScrollable(image_prop)
        self.notebook.AddPage(new_canvas, image_prop['filename'], select=True)
        # Construct the image icon visible on the tab
        idx1 = self.notebook.il.Add(new_canvas.scrollable_panel.icon_image)
        self.notebook.SetPageImage(len(self.list_canvas) - 1, idx1)
        self.tool.Show(True)
        self.Layout()


class NotebookCanvas(wx.aui.AuiNotebook):
    """
    todo surcharger la suppression d'un onglet
    """

    def __init__(self, parent, controller, *args, **kwargs):
        self.c = controller

        screen_size = wx.GetDisplaySize()
        wx.aui.AuiNotebook.__init__(self, parent, id=wx.ID_ANY,
                                    size=tuple((i * cst.MAIN_PANEL_RATIO for i in screen_size)),
                                    style=wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB,
                                    *args, **kwargs)

        self.il = wx.ImageList(16, 16)
        self.AssignImageList(self.il)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.on_page_changing)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.close)

    def on_page_changed(self, event):
        sel = self.GetSelection()
        self.c.activeCanvas = self.c.list_canvas[sel]
        chan_dict = self.c.activeCanvas.scrollable_panel.chan_image
        self.c.tool.build_chanel_selector(chan_dict)
        self.c.model.current_file = self.c.list_canvas[sel].scrollable_panel.image_prop

        event.Skip()

    def on_page_changing(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def close(self, event):
        """right-click event handler"""
        index = event.GetSelection()
        del self.c.list_canvas[index]
        self.DeletePage(index)


class ToolWindow(wx.Frame):
    def __init__(self, parent, *args, **kwargs):
        """
        A lateral window, which contains most of the quick access to tools.
        By default, the size of this window is defined as a fraction of the main window. This fraction is precised in
        the constants.py package.
        The default behaviour is to put this window always on top of the parent.


        The frame contains a notebook panel, each tab corresponding to a particular option.
        :param parent:
        :param args:
        :param kwargs:
        .. todo:: There should be the possibility to close and re-open this window

        """
        width, height = wx.GetDisplaySize()
        wx.Frame.__init__(self, parent=parent,
                          size=(width * cst.TOOL_WINDOW__WIDTH_RATIO, height * cst.TOOL_WINDOW__HEIGHT_RATIO),
                          title='Tools',
                          style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE & ~(
                          wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
                          *args, **kwargs)

        self.SetPosition((width - 4 * (width * cst.TOOL_WINDOW__WIDTH_RATIO), height / 8))
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
            self.show_button = wx.ToggleButton(self, label=title, size=(30, 30))
            self.bmp = wx.BitmapFromBuffer(img.shape[1], img.shape[0], img)
            self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, self.bmp)
            self.sizer.Add(self.show_button, 1, wx.ALL, 5)
            self.sizer.Add(self.imageBitmap, 0, wx.ALL, 5)
            self.SetSizer(self.sizer)
            self.Show(True)
