#!/bin/env python
# Python script to convert Xwiki syntax to Wordpress syntax (mostly HTML)
################################################################################

import sys, getopt, re

def usage():
  print"""
Usage: """ + sys.argv[0] + """ -i /input/file/path [-o /output/file/path]

-i, --input=
  Specifies file path for input (xwiki syntax)
-o, --output=
  Specifies file path for output (wordpress syntax)
-h, --help
  Displays this
"""

def read_file(input):
  input_f = open(input, 'r')
  data = []
  for line in input_f:
    data.append(line)
  #add an empty line in the end
  data.append("")
  return data

def convert_standard(data):
  newdata = []
  current_ul = False
  current_code = False
  for line in data:
    #Check for xwiki macros
    match = re.search("{{/code}}", line)
    if match:
      line=re.sub("{{/code}}", "[/code]", line)
      current_code = False
    match = re.search("{{code}}", line)
    if match:
      line=re.sub("{{code}}", "[code]", line)
      current_code = True
    if current_code:
      #text inside code is plain text
      #No changes must be done on plain text
      newdata.append(line)
      continue
    line = re.sub("{{info}}", "<blockquote>", line)
    line = re.sub("{{/info}}", "</blockquote>", line)
    line = re.sub("{{warning}}", '!!', line)
    line = re.sub("{{/warning}}", '!!', line)
    line = re.sub("{{toc/}}", "", line)
    #Check for images
    line = re.sub("\[\[image:(\w+)(||)*.*\]\]", r"!!!DON'T FORGET TO ADD IMAGE: \1", line)
    #Check for HTML links
    line = re.sub("\[\[(\w+)>>url:(.*)\]\]", r'<a href="\2">\1</a>', line)  
    #Check for unordered lists
    match = re.search("^\* ", line)
    if match:
      line = re.sub("^\* ", "<li>", line, 1)
      line += "</li>"
      if current_ul == False:
        current_ul = True
        line = "<ul>"+line
    elif current_ul:
      current_ul = False
      line += "</ul>"
    #Check for bold and italic caracters
    newline = ""
    even = True
    for splitted in line.split("**"):
      if even:
        even = False
        newline += splitted
      else:
        even = True
        newline += "<b>" + splitted + "</b>"
    line = newline
    newline = ""
    outside_italic = True
    #This is not working well at all
    #URL are getting caught
    #Should use a real parser
    for splitted in line.split("//"):
      if outside_italic :
        newline += splitted
        outside_italic = False
      elif newline[-1:] == ":":
        newline += "//"+splitted
        outside_italic = False
      else:
        newline += "<i>" + splitted + "</i>"
        outside_italic = True
    line = newline
    line = re.sub("\*\*(.*)\*\*", r"<b>\1</b>", line)
    #Check for titles
    line = re.sub("^==== ", "<h5>", line, 1)
    line = re.sub(" ====$", "</h5>", line, 1)
    line = re.sub("^=== ", "<h4>", line, 1)
    line = re.sub(" ===$", "</h4>", line, 1)
    line = re.sub("^== ", "<h3>", line, 1)
    line = re.sub(" ==$", "</h3>", line, 1)
    line = re.sub("^= ", "<h2>", line, 1)
    line = re.sub(" =$", "</h2>", line, 1)
    newdata.append(line)
  return newdata

def convert_user_specific(data):
  newdata = []
  for line in data:
    #line = re.sub("sensitive_information", "clean", line)
    #line = re.sub("same_with_no_case", "clean", line, flags=re.I)
    newdata.append(line)
  return newdata

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:h', ['input=', 'output=', 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for o, a in opts:
    if o == "-v":
      verbose = True
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-i", "--input"):
      input = a
    elif o in ("-o", "--output"):
      output = a
    else:
      assert False, "unhandled option"

  if input == None:
    usage()
    sys.exit(2)
  data = read_file(input)

  standard_data = convert_standard(data)
  user_specific_data = convert_user_specific(standard_data)

  output_data = ""
  for line in user_specific_data:
    #print line
    output_data += line
  print output_data

if __name__ == "__main__":
  main()
