---
title: Python in Memory
date: 2015-11-08T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /python-in-memory/
---
This following is a simple concept that I was struggling with last week but managed to figure out with the help of some pair programming.

Here's the setup. I have a few tables in RethinkDB that were ~100 MB each. RethinkDB is a NoSQL database and it stores data in JSON. The bits I specifically needed were nested inside an array. So something like this

{% highlight javascript %}
[
  "id": "32-characer GUID",
  "something": "some string"
  "other": [
    {
       "bit_I_care_about": "string"
    },
    {
       "bit_I_care_about": "string"
    }
  ]
]
{% endhighlight %}

To get at the bits I care about, I'd have to iterate through each top level object, get the `other` key, then iterate through each element of the array in `other`. My initial thought was to do this procedurally.

Read the data without modifications to a variable. Then iterate through each element of the array in the key `other`. Then get the bits I need. 

Doing this on one table was fine. But I needed to compare the bits_I_need between multiple tables. It consistently was bombing out whenever I tried to do this due to memory constraints. Even when I tried to use iPython's magic commands to clear memory each time, it kept bombing out. 

The solution was, of course, to get the bits_I_need as I'm reading the data into memory. Instead of doing something like this:

{% highlight python %}
things_i_need = []
data = r.db('my_db').table('my_table').run(conn)
in_memory = [flatten(thing) for thing in data]
# flatten() is a custom function that brings everything in `other` to the top level
for thing in in_memory:
    things_i_need.append(stuff['bit_I_care_about'])
{% endhighlight %}

which is way too memory intensive and has much more than I need, I could do something like this:

{% highlight python %}
things_i_need = []
data = r.db('my_db').table('my_table').run(conn)
for thing in data:
   for stuff in thing['other']:
        things_i_need.append(stuff['bit_I_care_about'])
{% endhighlight %}

Which runs like a breeze. Even better, since I was comparing between tables, I could wrap this in a function to get exactly what I want:

{% highlight python %}
def my_function(table_1, table_2):
	things_i_need = []
	data = r.db('my_db').table(table_1).run(conn)
	for thing in data:
	   for stuff in thing['other']:
	        things_i_need.append(stuff['bit_I_care_about'])

	things_i_need2 = []
	data2 = r.db('my_db').table('table_2').run(conn)
	for thing in data2:
	   for stuff in thing['other']:
	        things_i_need2.append(stuff['bit_I_care_about'])

    return list(set(things_i_need2)-set(things_i_need))
{% endhighlight %}

Then I can just iterate through all the tables I need to compare, call this function with the appropriate tables, and be on my merry way.

Of course, this could be optimized further, but it can also be extended. If I needed to only add to my list after satisfying a certain condition, I could do so. I should also probably use `thing.get('other', [])` instead of `thing['other']` because it allows the program to continue even if that key doesn't exist. 

This was a fun little challenge that was solved with the help of a second set of eyes and some insight into what I was actually trying to get accomplish. Instead of getting all the data in case I needed, we took a look at the goal I was trying to achieve and coded it in that manner.
