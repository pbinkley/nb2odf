#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs, sys, getopt, inspect

from odf.opendocument import load
from odf.style import Style, ParagraphProperties, TextProperties
from odf.text import P, Span, Note, NoteCitation, NoteBody

# global variables
currentP = None
oldP = None
currentS = ""
input = None
output = None

# from http://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
	global input, output, currentP, oldP, currentS, currentStyle, notecounter
	notecounter = 1
	inputfile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'test.py -i <inputfile> -o <outputfile>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
		print 'Input file is "', inputfile
		print 'Output file is "', outputfile

	# NB tags begin 174 and end 175
	# input = codecs.open(inputfile, encoding="cp437")
        input = open(inputfile, 'rb')
	#output = OpenDocumentText()
	output = load("template.odt")
	
        state = "start"
	tag = ""
	fonts = []
	blocks = []
	infootnote = False
	# set to true when encounter line break; if not followed by end of para, insert <br/>
	possiblebreak = False
	
	""" 
	Our strategy is to accumulate strings in s, and to stack blocks in the blocks array
	
	We assume paragraphs begin with USIX, USBX or USNX and end with USSX.
	Footnotes begin with <FN1 and end with >
	"""
	#for line in input.readlines():
	try:
                o = unicode(input.read(1), 'latin-1')
                while o != '':
                        #print o
                	if ord(o) == 174: 
                		""" start of tag """
                                handletag()
                        elif ord(o) == 175:
                                """ end of footnote: it's already attached, so just point currentP at context P """

                                #print inspect.getmembers(currentP)
                                if currentP and oldP:
                                        currentP.addText(currentS)
                                        currentS = ''
                                        currentP = oldP
                        elif ord(o) > 31 and ord(o) < 128:
                                currentS += o
                        else:
                                currentS += handlechar(ord(o))
                                
                        o = unicode(input.read(1), 'latin-1')
	finally:
         	input.close()
                output.save(outputfile)

def handlechar(o):
	# special characters
	if o == 250:
		return u'\u00A0'
	elif o == 9:
		return u'\t'
	elif o == 10:
		return u'\n'
	elif o == 13:
		return u'\r'
	elif o == 21:
		return  u'§'
	elif o == 129:
		return  u'ü'
	elif o == 130:
		return  u'é'
	elif o == 132:
		return  u'ä'
	elif o == 133:
		return  u"à"
	elif o == 148:
		return  u'ö'
	elif o == 179:
		return  u'|'
	elif o == 183:
		return u'\u00A0'
	elif o == 187:
		return ' '
	elif o == 224:
		return u'à'
	elif o == 228:
		return u'ä'
	elif o == 233:
		return u'é'
	elif o == 246:
		return u'ö'
	elif o == 252:
		return u'ü'
	else:
		return  "[unknown:" + str(o) + "]"
	
def handletag():
	global input, output, currentP, oldP, currentS, currentStyle, notecounter
	""" read tag """
	tag = ""
	tagc = input.read(1)
	while ord(tagc) != 175 and ord(tagc) != 187:
		#print tagc
		tag += unicode(tagc, 'latin-1')
		if tag == u"FN1" or tag == u'X6':
                        break
		tagc = input.read(1)
	print "Tag: " + tag
	if tag == u"USIX":
		""" indented paragraph """
		currentP = P(stylename="First_20_line_20_indent")
	elif tag == u"USBX":
		""" block quote """
		currentP = P(stylename="Text_20_body_20_indent")
	elif tag == u"USNX":
		""" unindented paragraph """
		currentP = P(stylename="Text_20_body")
	elif tag == u"USSX":
		""" paragraph separator """
		print "Para done: " + currentS
		currentP.addText(currentS)
		currentS = ""
		output.text.addElement(currentP)
	elif tag == u'MDIT':
                currentP.addText(currentS)
                currentS = ''
                currentStyle = 'T2'
	elif tag == u'MDBO':
                currentP.addText(currentS)
                currentS = ''
                currentStyle = 'T3'
        elif tag == u'MDNM':
                currentP.addElement(Span(stylename=currentStyle, text=currentS))
                currentS = ''
	elif tag == u'FN1':
                """ we have a footnote, which will end with a loose 175 """
                oldP = currentP
                currentP.addText(currentS)
                currentS = ''
                """ currentP becomes the footnote """
                note = Note(id="ftn" + str(notecounter-1), noteclass="footnote")
                currentP.addElement(note)
                note.addElement(NoteCitation(text=str(notecounter)))
                notecounter += 1
                notebody = NoteBody()
                note.addElement(notebody)
                currentP = P(stylename="Footnote", text=u"")
                notebody.addElement(currentP)
                """ so the structure is now: context P - note - notebody - currentP """
        elif tag == u"RP" or tag==u'X6':                 
            tag = ""
                        
	else:
                currentS += u"[" + tag + u"]"
                
	
if __name__ == "__main__":
	main(sys.argv[1:])

