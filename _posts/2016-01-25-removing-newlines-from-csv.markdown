---
title: Removing newlines from CSV
date: 2016-01-25T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /removing-newlines-csv/
---
A small csv annoyance at work necessitated me writing a script to automate the fix for said annoyance.

The problem:

I had CSV files that were generated from the PDF reading app Tabula. When these files were opened in Sublime Text 2 or Excel, the newline characters in between double quotes were rendered and data that was supposed to be on a single line would end up on multiple lines. This was annoying and I wanted remove this so that it could be displayed and manipulated properly in Excel. (Yes, I know, Excel is rough but we do what we must when the business demands it).

My desired end result is that I would be able to use an Alfred script to make it simple to execute this. At first I thought I would copy in the text I needed fixed and then I could put the corrected data back into my clipboard. This worked quite well for my JSONify Alfred script which converts a single line of JSON into human-readable JSON. But I'm generally always working with actual CSV files, so I decided to have it read from a file and write to a new one.

In Alfred, the workflow is quite simple: 

1. Create a File Filter --- In my case, the files are always on my desktop. My file filter is triggered with "cn" and it searches my desktop for .csv files. 

1. Pass file to Run Script --- This file is then passed to a Python script that I wrote. The actual Alfred script runs `python csvnewlineremove.py {query}` in bash.

Here's the Python script:

{% highlight python %}
# -*- coding: utf-8 -*-
import csv, os, sys
import StringIO


input_file = sys.argv[1]

with open(input_file, "rb") as csv_file:
    csv_data = StringIO.StringIO(csv_file.read())

final_location = os.path.expanduser("~/Desktop/alfredfixed.csv")

with open(final_location, "wb") as output:
    mywriter = csv.writer(output)
    filtered = (line.replace('\r', '') for line in csv_data)

    for record in csv.reader(filtered):
        mywriter.writerow(tuple(record))
{% endhighlight %}

`sys.argv[1]` parses the input file directory which is then read as a string by StringIO. I did this after a bunch of googling as a way to pull in the contents of a file as a string. I'm not 100% sure this is necessary but it works. I need to look into this more.

`final_location` is a way for me to output the file to the desktop of whoever happens to be using the workflow.

The final `with`  sets up a csv writer instance in `mywriter`. The magic happens in `filtered`. Originally I thought I needed to remove excess new lines (`\n`). But when I opened up the file in a hex editor (I recommend [Hex Fiend](http://ridiculousfish.com/hexfiend/)) I discovered that it was actually character returns (`0D` in hex) that were causing the problem. So by switching in the `replace` field `\n` with `\r`, it worked. 

The Stack Overflow question I referenced most closely was [this one](http://stackoverflow.com/questions/8219502/how-could-i-remove-newlines-from-all-quoted-pieces-of-text-in-a-file). As you'll notice, the accepted answer had the final record wrapped in a tuple call. I'm not sure why they did that except to make the data immutable. I've left in it as it seems safer. 

All in all, this was a fun little project that I've now automated and it won't slow me up anymore.
