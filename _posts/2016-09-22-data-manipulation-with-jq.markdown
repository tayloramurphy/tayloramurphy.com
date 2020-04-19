---
title: Data Manipulation with jq
date: 2016-09-22T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /datajq/
---
I had a data maniuplation challenge the other data that I was able to easily solve with the wonderful command line tool `jq`. As described on the [homepage](https://stedolan.github.io/jq/) for jq:

> jq is like `sed` for JSON data

Which basically means that you can do some very powerful transformations all without having to open the file.

#### My Problem
I had JSON data of the form:

{% highlight javascript %}
[{
	"value": "GENE:d",
	"other": "Data1"
},{
	"value": "GENE2:d",
	"other": "Data2"
},{
	"value": "GENE:d",
	"other": "Data3"
}]
{% endhighlight %}

and I needed to get it into the form of:

{% highlight javascript %}
[{
	"term": "GENE:d",
	"synonym": "GENE"
},{
	"term": "GENE2:d",
	"synonym": "GENE2"
}]
{% endhighlight %}

You'll notice some key points here. First, I needed to ensure uniqueness of all terms (in this case they happen to be genes). Second, I needed to remove the `:d` from each of the terms and store it with the synonym key.

It's possible to do this in a one-liner with `jq`, but it took me a lot of trial and error (at least 30 attempts based on my bash history). My first successful attempt actually had an intermediate step in Sublime Text where I permuted the data to determine the unique values. I then used `jq` to carry it the rest of the way. After playing with it a bit more when the task at hand was no longer urgent, I was able to solve it all in one step and build a better mental model of how the tool works. What really tripped me up was a basic lack of understanding about how the data flows from one `jq` filter to another.

`jq` works on a stream of JSON data. If you have a properly formatted JSON file, the easiest way to make it a stream is to call `cat` on the file and then pipe it (`|`) to `jq`. It would look like this:

{% highlight bash %}
cat your_json_file.json | jq '.[]'
{% endhighlight %}

For all subsequent examples, assume the `cat` command is present and is piping the data to `jq`.

#### The Steps
The first thing to do is call `unique_by` on each object. This is easily done via:

{% highlight bash %}
jq 'unique_by(.value)'
{% endhighlight %}

With uniqueness guaranteed across the dataset, we're now able to focus on a single  object for all subsequent steps. You'll notice above that all of my data is in a single array with each item being a JSON object. To "unpack" the array, the next command is simply `.[]`. All together this looks like:

{% highlight bash %}
jq 'unique_by(.value) | .[]'
{% endhighlight %}

With that, we're now able to process each object in isolation. The next part I had to do was to take the string from the "value" key and store it into a variable. I figured this out after a lot of trial and error. In my earlier attempts I was unable to access the value I needed after the following steps. Saving it to a variable worked, so I'm going with it. It looks like this:

{% highlight bash %}
jq 'unique_by(.value) | .[] | .value as $term'
{% endhighlight %}

`.value` is accessing the string at the key "value" and it's storing it to the variable `$term`. The next step is to parse our string to remove the `:d` from each term. I used the `match` function but in theory I could have used the sub function to remove the `:d`. Matching was more useful because I wanted to store the match in my final object. To access the "value" term we have to filter our inidiviual object by doing this:

{% highlight bash %}
jq 'unique_by(.value) | .[] | .value as $term | .value'
{% endhighlight %}

So that now we're working with a string. Each string can then be passed to the match function like so:

{% highlight bash %}
jq 'unique_by(.value) | .[] | .value as $term | .value | match("[A-Z0-9orf\\-]{1,}") as $synonym'
{% endhighlight %}

That regular expression should match all the genes I have in my dataset. The above code won't work though because you're not doing anything with the match. The match object looks like this:

{% highlight javascript %}
{
  "offset": 0,
  "length": 6,
  "string": "OR14I1",
  "captures": []
}
{% endhighlight %}

So the value I need is stored in the "string" key. Now, with both values I need accessible via variables, I'm able to generate the final object:

{% highlight bash %}
jq 'unique_by(.value) | .[] | .value as $term | .value | match("[A-Z0-9orf\\-]{1,}") as $synonym | {term:$value, synonym:$synonym.string}'
{% endhighlight %}

Running the above will output each object in the proper format. The only problem is that because I started with an array I need to end with an array. This is done trivially by wrapping the entire `jq` expression with brackets:

{% highlight bash %}
jq '[unique_by(.value) | .[] | .value as $term | .value | match("[A-Z0-9orf\\-]{1,}") as $synonym | {term:$value, synonym:$synonym.string}]'
{% endhighlight %}

With all of that in place, we're then able to write to a file by simply adding `> your_output_file.json` to the end of the above command.

And that's that! Hopefully that helps explain the workings of `jq` a bit. It's certainly helped me have a better mental model of how data is passed to each filter.
