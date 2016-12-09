# -*- coding: utf-8 -*-
"""
This class handles all the I/O operation (reading and writing).
"""
import os
import cv2

from src.controller import constants as cst


class Model():
    def __init__(self, controller):

        self.c = controller
        self.currentFile = dict(filename='', dirname='', extension='', image=None)
        # This is an error. This dictionary should not be an attribute of the model,
        # but an attribute of the opened image. Indeed, there can be many images opened at once. So this attributes should be moved.

        self.default_source = os.path.dirname(os.path.realpath(__file__))  # Give the current directory
        # Todo Should lead to the image directory

    def openNewFile(self):
        """Open file based on the self.currentfile dictionary
        If an image is already opened, then the dictinary pointing to the image is updated.
        """

        if self.currentFile['image'] is None:
            path = os.path.join(self.currentFile['dirname'], self.currentFile['filename'])
            try:
                assert (os.path.isfile(path))
            except AssertionError:
                print 'This is not a valid file path'
            self.currentFile['filename'], self.currentFile['extension'] = os.path.splitext(path)

            try:
                assert (self.currentFile['extension'].upper() in cst.FORMAT_HANDLE)
            except AssertionError:
                print 'This is not a recognized file extension'
                #Todo call the warning method in the controller
            print path
            self.currentFile['image'] = cv2.imread(
                path.decode('latin1'))  # Todo: problem with accent in path (encoding into utf-8?) URGENT
            self.c.constructNewCanvas(self.currentFile['image'], self.currentFile['filename'])

        else:
            self.c.call_warning(cst.EXISTING_IMAGE_LOADED) #Todo Correct the error message (implement an user choice: "destroy the present canvas or construct new one?")
            self.currentFile = dict(filename='', dirname='', extension='', image=None)
            self.c.OnOpen()
