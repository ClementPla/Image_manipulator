# -*- coding: utf-8 -*-

import wx
from src.controller import controller

if __name__ == "__main__":
    app = wx.App(False)
    controller = controller.Controller()
    app.MainLoop()