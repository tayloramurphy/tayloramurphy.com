---
title: Creating an Alexa Skill
date: 2017-02-14T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /alexagene/
---
One of the many great talks I went to at PyTennessee 2017 was [Jason Bynum's](https://twitter.com/jasonbynum) ["Alexa Doesn't Even Have Any Skillz"](https://www.pytennessee.org/schedule/presentation/151/). I opted to go to his talk instead of some potentially more relevant ones (sorry Elasticsearch!) but I'm glad I made that choice.

Jason walked us through the basics of setting up an Alexa skill using Python. He then teased us with the promotion Amazon is currently offering, which is a hoodie if you publish a skill before the end of February.

### The Start
Amazon is trying to convince as many people as possible to develop skills for the Alexa device. To encourage everyone to publish something, they've created a simple guide to create your own [Fact Skill](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/content/fact-skill-1). As I am highly motivated by hoodies, I started from this Fact Skill and decided to tweak it as needed.

The first thing you need to do is create an account on developer.amazon.com. I linked my personal Amazon account because it was easier. Within the portal, you then select "Alexa" and then "Add a New Skill".

Here's where the first decision has to be made. You need to create a name for the skill and create an invocation name. This is the phrase that users will say to launch your skill. I knew I wanted to make my skill specifically for querying the HUGO Gene Nomenclature Committee website, so I called it "Gene Facts".

### Defining the Interaction
Because we're working off a template, you don't have to do much work to define the interaction model. But you could if you really wanted to. The awesome thing about what Amazon has done with Alexa is the way they're defining the interaction model for humans and machines. The simplified version is you have intents and slots.

Intents are user-defined and represents the requests the skill can handle. Slots are user-provided arguments that are passed to the intent. The Fact skill is set up with the basic ones we need. We have `GetNewFactIntent`, which is our primary trigger for the skill, and we have 3 built-ins for Help, Stop, and Cancel. The cool thing about these is that you can add intent-specific data to them. For example, in the docs, they discuss a Horoscope example which has the primary intent `GetHoroscope` which then has two slots for sign and date. The date slot is referencing an Amazon built-in dataset of available dates while the "sign" slot is built from a list of developer specified words.

A decent analogy to the intent/slot idea is that of a function to which you pass specific arguments. The intent is the function definition and the slots are the data that you are passing to the function. Our fact skill doesn't have any slots, or function arguments if you will, because we're not making a request with specific data. It picks a random number and selects a fact from a subset of available data.

There is a lot you could do with the intents and slots model definition. Certainly more than the basic fact skill is showing. I'm excited for what people will come up with in the future, but I wanted to keep my own skill simple for now.

Once you've defined the intent schema and any custom slot types you can specify sample utterances that people would use to interact with your skill. The utterances provided by the fact example all all pretty obvious. I simply changed the words "space" to "gene" and went with what they had.

### AWS Lambda
The next step of the tutorial has you setting up a Lambda function. Lambda functions are quite cool because you don't have to constantly run an EC2 instance to be watching and waiting for a trigger. The lambda function will get triggered and a box is spun up to quickly execute your code.

The tutorial is quite explicit about what you need to do to set up a Lambda function so I won't go into detail about that. The problems weren't with setting up the Lambda function, it was when I started messing with the code.

### Node.js
I'm not a Node developer. Technically, I'm not really a Python developer either since I play with data mostly. But I have a much better intuitive grasp of Python than JavaScript and, in particular, Node. I wasn't content with just replacing the space facts in the example skill with some crappy gene facts. I wanted to actually query an API and do something interesting.

The HGNC API is open and doesn't require any authentication, so it's a quick and easy way to dynamically pull data from the internet. Because I didn't want to deal with user requested data (slots) I stuck with the randomized model of picking data. My initial attempt at the skill would pick a random number between 1 and 20000 and attempt to use that as the HGNC ID. If that wasn't a valid ID, then it returned the information for _BRAF_. This turned out to be an unsatisfying solution because every third request was for _BRAF_.

I then decided to just download the entire protein-coding gene dataset from HGNC and get all the actual IDs. Then at least I wouldn't always be returning _BRAF_. I saved this into an array and adjusted the gene selector to pick a random number from 0 to the length of the gene_ids array minus 1. This at least was a more valid way of randomly selecting a gene.

My next struggle was with making an HTTP request in Node. The cool thing about Node is that it's asynchronous by nature. The frustrating thing with Node is that it's asynchronous by nature. I initially had the speech results returning outside the request function because that was the basic format of the initial code. But by doing this I was constantly returning an incomplete sentence that had no data. The final emit statement wasn't waiting for data to be returned from the request.

Of course the solution to this is to use callbacks, but I still don't have a great understanding of how that really works, so I just shoved the emit statement into the request to make my life easier. Ugly? Yes. Does it work? Sure!

### Testing and Running
With my code mostly working, I now had to test that I was returning what I expected from the program. The "quickest" way to do this was to zip everything up, upload it to AWS Lambda, and test it within the skill development portal. I'm sure I could've tested this locally better, but going through this circuitous route was faster in the moment. I selected the folder with all of my code and node modules in it and compressed it using the Mac's built in zipping feature.

I selected my zip file and uploaded and tested it in Lambda. Immediately I was getting errors. Unfortunately, to figure out exactly what the errors were I needed to go to Cloudwatch to actually see them. There I saw the error was: `Unable to import module 'index': Error`. Everything seemed like it should be working fine based on what I could tell, so I turned to my handy-dandy reference guides known as Google and StackOverflow. Thankfully, I quickly found the issue via [this thread](http://stackoverflow.com/questions/41750026/aws-lambda-error-cannot-find-module-var-task-index). Basically, compressing the files via the built-in was causing some weird problems. Using `zip -r` on the command line fixed it. Though now that brings up even more questions about why the initial compression wouldn't work.

With everything seemingly squared away, I was able to test that Alexa could speak the responses. But now I had new problems: she was trying to say the gene abbreviations, which was hilarious, and she spoke way too damn fast.

### Slow Down Alexa!
My goal then became making Alexa easier to understand. I wanted her to spell out the gene abbreviation and to do it slowly. Google again was my friend and it quickly become obvious that you could use Speech Synthesis Markup Language to get her to say words in a particular manner. In this case, it's as easy as adding the markup `<say-as interpret-as="spell-out">YOUR PHRASE</say-as>` around the word you want spelled out.

I added this to the code, zipped it, uploaded it, and tested it (again, not the quickest method of testing these things...) and Alexa dutifully spelled out the gene name. But she did it damn quick and there wasn't an obvious method of slowing her down using the `say-as` markup. StackOverflow was my friend again and I found [this thread](http://stackoverflow.com/questions/37885565/alexa-skill-ssml-talking-speed#) which basically says to insert breaks between every letter.

With this new-found knowledge, I adjusted the code for the gene abbreviation like so:

`the_gene.split('').join('<break time="100ms"/>') + '<break time="100ms"/></say-as>`

This worked surprisingly well and I decided that was enough fiddling with the skill.

### Finishing Touches
With everything how I liked it, I then moved on to the rest of the tutorial which is all about the user-facing experience: writing out the long and short descriptions, selecting some icons, and figuring out example phrases for the skill. This was all pretty trivial but I should've spent a little more time with it because this step is what kicked back my skill initially. The review team had concerns about my use of HGNC in the name and they didn't like my example phrases. Evidently the initial phrase is supposed to be the full one and then the other two examples are just the final "action" words. (e.g. Alexa ask Gene Facts to tell me a fact is the first example and the other two are 'tell me trivia' and 'give me a fact')

With that fix in place, my skill was accepted and officially published! It's available on the [Alexa Skills Store](https://www.amazon.com/Taylor-Murphy-Unofficial-HGNC-Facts/dp/B01N806ZT6/ref=sr_1_1?s=digital-skills&ie=UTF8&qid=1487711634&sr=1-1&keywords=gene+facts) for free and it already has a review for 4/5 stars. Not too shabby.

Give a try and tell me what you think. Or better yet, publish your own! Definitely use the [Amazon tutorial](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/content/fact-skill-1) as a starting point, but here's [my own code](https://github.com/tayloramurphy/gene-facts/blob/master/index.js) if you're interesetd.
