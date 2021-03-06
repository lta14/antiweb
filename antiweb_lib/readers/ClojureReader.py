__author__ = "Michael Reithinger, Philipp Rathmanner, Lukas Tanner, Philipp Grandits, and Christian Eitner"
__copyright__ = "Copyright 2017, antiweb team"
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "antiweb team"
__email__ = "antiweb@freelists.org"

from pygments.token import Token

from antiweb_lib.readers.Reader import Reader

#@cstart(ClojureReader)
class ClojureReader(Reader):
    #@start(ClojureReader doc)
    #ClojureReader
    #=============
    """
    .. py:class:: ClojureReader

       A reader for Clojure code. This class inherits :py:class:`Reader`.
    """
    #@indent 3
    #@include(ClojureReader)
    #@(ClojureReader doc)

    def __init__(self, lexer,  single_comment_markers,  block_comment_markers):
        super(ClojureReader, self).__init__(lexer,  single_comment_markers,  block_comment_markers)
        self.single_comment_marker = single_comment_markers[0]

    def _accept_token(self, token):
        return token in Token.Comment
    
    def _cut_comment(self, index, token, text):
        if text.startswith(self.single_comment_marker):
            text = text[1:]
        return text
		
    def filter_output(self, lines):
        """
        .. py:method:: filter_output(lines)

           See :py:meth:`Reader.filter_output`.
        """
        for l in lines:
            if l.type == "d":
                #remove comment chars in document lines
                stext = l.text.lstrip()
		
                if stext.startswith(self.single_comment_marker):
                    #remove comments but not chapters
                    l.text = l.indented(stext[1:])

            yield l
    #@edoc
    #@(ClojureReader)
