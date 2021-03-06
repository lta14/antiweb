__author__ = "Michael Reithinger, Philipp Rathmanner, Lukas Tanner, Philipp Grandits, and Christian Eitner"
__copyright__ = "Copyright 2017, antiweb team"
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "antiweb team"
__email__ = "antiweb@freelists.org"

import operator
from bs4 import BeautifulSoup,  Tag,  NavigableString

from antiweb_lib.readers.Line import Line
from antiweb_lib.readers.CReader import CReader

#@cstart(CSharpReader)

class CSharpReader(CReader):
    #@start(CSharpReader doc)
    #CSharpReader
    #=============
    """
    .. py:class:: CSharpReader

       A reader for C# code. This class inherits :py:class:`CReader`.
       The CSharpReader is needed because C# specific output filtering is applied.
       Compared to C, C# uses XML comments starting with *///* which are reused
       for the final documentation. Here you can see an overview of the CSharpReader class
       and its methods.

    """

    #@indent 3
    #@include(CSharpReader)
    #@include(CSharpReader.strip_tags doc)
    #@include(CSharpReader.get_attribute_text doc)
    #@include(CSharpReader.get_stripped_xml_lines doc)
    #@include(CSharpReader.create_new_lines doc)
    #@include(CSharpReader.init_xml_block doc)
    #@include(CSharpReader.filter_output doc)
    #@(CSharpReader doc)

    default_xml_block_index = -1

    def __init__(self, lexer, single_comment_markers, block_comment_markers):
        #the call to the base class CReader is needed for initialising the comment markers
        super(CSharpReader, self).__init__(lexer,  single_comment_markers,  block_comment_markers)

    #@cstart(CSharpReader.strip_tags)
    def strip_tags(self, tags):
        """
        .. py:method:: strip_tags(tags)

           Removes all C# XML tags. The tags are replaced by their attributes and contents.
           This method is called recursively. This is needed for nested tags.

           Examples:

            * ``<param name="arg1">value</param>`` will be stripped to : *"arg1 value"*
            * ``<para>Start <see cref="(String)"/> end</para>`` will be stripped to : *"Start (String) end"*

           :param Tag tags: the parsed xml tags
           :return: a string containing the stripped version of the tags
        """

        text = ""

        if isinstance(tags, Tag):
            text = self.get_attribute_text(tags)

            for content in tags.contents:
                if not isinstance(content, NavigableString):
                    content = self.strip_tags(content)
                text += content

        return text
    #@edoc

    #@cstart(CSharpReader.get_attribute_text)
    def get_attribute_text(self, tag):
        """
        .. py:method:: get_attribute_text(tag)

           Returns the values of all XML tag attributes seperated by whitespace.

           Examples:

            * ``<param name="arg1">parameterValue</param>`` returns : *"arg1 "*
            * ``<include file='file1' path='[@name="test"]' />`` returns: *"file1 [@name="test"] "*

           :param Tag tag: a BeautifulSoup Tag
           :return: the values of all attributes concatenated
        """
        #collect all values of xml tag attributes
        attributes = tag.attrs
        attribute_text = ""
        for attribute, value in attributes.items():
            attribute_text = value + " "
        return attribute_text
    #@edoc

    #@cstart(CSharpReader.get_stripped_xml_lines)
    def get_stripped_xml_lines(self, xml_lines_block):
        """
        .. py:method:: get_stripped_xml_lines(xml_lines_block)

           Removes all XML comment tags from the lines in the xml_lines_block.

           :param Line[] xml_lines_block: A list containing all Line object which belong to an XML comment block.
           :return: A list of all stripped XML lines.
        """
        #the xml_lines_block contains Line objects. As the xml parser expects a string
        #the Line obects have to be converted to a string.
        xml_text = "\n".join(map(operator.attrgetter("text"), xml_lines_block))

        #the xml lines will be parsed and then all xml tags will be removed
        xml_tags = BeautifulSoup(xml_text, "html.parser")

        stripped_xml_lines = self.strip_tags(xml_tags)

        return stripped_xml_lines.splitlines()
    #@edoc

    #@cstart(CSharpReader.create_new_lines)
    def create_new_lines(self, stripped_xml_lines, index, fname):
        """
        .. py:method:: create_new_lines(stripped_xml_lines, index, fname)

           This method is called after all XML comment tags of a comment block are stripped. For each new
           line in the stripped_xml_lines a new Line object is created.

           Note that leading spaces and tabs are stripped, which means that lines
           do not have any indentation. Use a C# comment block if indentations should be kept.

           :param string[] stripped_xml_lines: The comment lines were the XML tags have been stripped.
           :param int index: The starting index for the new line object.
           :param string fname: The file name of the currently processed file.
           :return: A generator containing the lines which have been created out of the stripped_xml_lines.
        """

        for line in stripped_xml_lines:
            #only removing spaces and tabs --> newlines should be kept
            new_line = Line(fname, index, line.lstrip(' \t'))
            index += 1
            yield new_line
    #@edoc

    #@cstart(CSharpReader.init_xml_block)
    def init_xml_block(self):
        """
        .. py:method:: init_xml_block()

           Inits the variables which are needed for collecting an XML comment block.
        """
        xml_lines_block = []
        xml_start_index = self.default_xml_block_index
        return xml_lines_block, xml_start_index
    #@edoc

    #@cstart(CSharpReader.filter_output)
    def filter_output(self, lines):
        """
        .. py:method:: filter_output(lines)

           Applies C# specific filtering for the final output.
           XML comment tags are replaced by their attributes and contents.

           See :py:meth:`Reader.filter_output`

           We have to handle four cases:
            1. The current line is a code line: The line is added to result.
            2. The current line is a block comment: The line can be skipped.
            3. The current line is an XML comment: The line is added to the xml_lines_block.
            4. The current line is a single comment line: Add the line to result. If the current line is the first
               line after an xml comment block, the comment block is processed and its lines are added to result.

           :param Line[] lines: All lines of a file. The directives have already been replaced.
           :return: A generator containing all lines for the final output.
        """
        #first the CReader filters the output
        #afterwards the CSharpReader does some C# specific filtering
        lines = super(CSharpReader, self).filter_output(lines)

        #the xml_lines_block collects xml comment lines
        #if the end of an xml comment block is identified, the collected xml lines are processed
        xml_lines_block, xml_start_index  = self.init_xml_block()

        for l in lines:
            if l.type == "d":

                text = l.text.lstrip()

                if text == self.block_comment_marker_start or text == self.block_comment_marker_end:
                    #remove /* and */ from documentation lines. see the l.text.lstrip()!
                    #if the lines ends with a white space the quotes will be kept!
                    #This is feature, to force the quotes in the output
                    continue

                if text.startswith("/") and not text.startswith(self.block_comment_marker_start):
                    l.text = l.indented(text[1:])

                    if xml_start_index == self.default_xml_block_index:
                        #indicates that a new xml_block has started
                        xml_start_index = l.index

                    xml_lines_block.append(l)
                    continue
                elif not xml_start_index == self.default_xml_block_index:
                    #an xml comment block has ended, now the block is processed
                    #at first the xml tags are stripped, afterwards a new line object is created for each
                    #stripped line and added to the final result generator
                    stripped_xml_lines = self.get_stripped_xml_lines(xml_lines_block)

                    new_lines = self.create_new_lines(stripped_xml_lines, xml_start_index, l.fname)
                    for line in new_lines:
                        yield line

                    #reset the xml variables for the next block
                    xml_lines_block, xml_start_index  = self.init_xml_block()

            yield l
    #@edoc
