__author__ = "Michael Reithinger, Philipp Rathmanner, Lukas Tanner, Philipp Grandits, and Christian Eitner"
__copyright__ = "Copyright 2017, antiweb team"
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "antiweb team"
__email__ = "antiweb@freelists.org"

from watchdog.events import FileSystemEventHandler
from antiweb_lib.write import write
from antiweb_lib.write import create_write_string
from antiweb_lib.readers.config import is_file_supported
import time

#@start()
"""
.. _label-filechangehandler:

###################
FileChangeHandler
###################

#@include(FileChangeHandler doc)

#@include(process_event doc)

-   events 'created', 'modified', 'moved' and 'deleted' are handled by the process_event method
-   event 'moved' is triggered when a subdirectory of the monitored source directory
    contains monitored files and the subdirectory is renamed
-   note that when a file is modified/created watchdog may get multiple events

#@include(file_events)

"""

#@cstart(FileChangeHandler)
class FileChangeHandler(FileSystemEventHandler):
    #@start(FileChangeHandler doc)
    """
    .. py:class:: FileChangeHandler(directory, extensions, options)

       This handler is responsible for handling changed file events in antiweb's daemon mode.

       :param string directory: absolute path to the monitored source directory
       :param options: antiweb commandline options
       :param created_files: a set which contains the absolute paths of all previously created documentation files

    """
    #@include(FileChangeHandler)

    #@(FileChangeHandler doc)

    def __init__(self, directory, options, created_files):
        self._directory = directory
        #antiweb commandline options
        self._options = options
        self._event_counter = 0
        self._created_files = set()
        self._created_files.update(created_files)

#@cstart(process_event)

    def process_event(self, event):
#@start(process_event doc)
        """
.. py:method:: process_event(self, event)

   Handles the file events: 'modified' | 'created' | 'moved' | 'deleted'.

   The events trigger an update of the corresponding documentation file.
   Ignored events are: deleted files, changed directories, files without a handled extension and changes of
   antiweb's created documentation files.

   :param event: The file event that should be handled. Possible event types: 'modified' | 'created' | 'moved' | 'deleted'
        """

#@include(process_event)
#@(process_event doc)

        self._event_counter += 1
        time_stamp = "[" + time.strftime('%H:%M:%S') + " " + str(self._event_counter).zfill(5) + "] "

        changed_file = event.src_path

        if event.event_type == "moved":
            #moved event has to be handled differently:
            #the file has been moved so it is now located in event.dest_path
            changed_file = event.dest_path

        ignore_change = changed_file in self._created_files or not is_file_supported(changed_file) or \
                  event.is_directory or event.event_type == "deleted"

        if not ignore_change:
            #process change
            created_file = write(self._directory, changed_file, self._options, False)

            if created_file:
                self._created_files.add(created_file)

            event_string = create_write_string(changed_file, created_file)
        else:
            #ignore change
            event_string = "Ignored change: " + changed_file + " [" + event.event_type + "]"

        #using autoflush to immediately print the output
        print(time_stamp + event_string, flush=True)

#@(process_event)


#@cstart(file_events)

    def on_modified(self, event):
        self.process_event(event)

    def on_created(self, event):
        self.process_event(event)

    def on_moved(self, event):
        #this event is triggered when a src directory contains a subdirectory with some files
        #and the subdirectory is renamed. the event is then triggered for all files within
        #the subdirectory and the subdirectory itself
        self.process_event(event)

    def on_deleted(self, event):
        self.process_event(event)

#@(file_events)

#@
