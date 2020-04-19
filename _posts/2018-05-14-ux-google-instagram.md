---
title: The UX of Sharing Photos with Google Photos and Instagram
date: 2018-05-14T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /ux-google-instagram/
---
I had one of the most frustrating technology related moments of my life on Mother’s Day. My aim was simple: share a few old and new photos of my mother and me on Instagram. All of the photos are already in Google Photos so this should be a relatively simple task, right? With the pieces all set, let’s see what actually happened.

Google Photos actually made it quite easy to find photos of my mom. I simply typed her name in the search bar and many years worth of photos popped up. I selected a few and created a new album called “Mother’s Day 2018”. This held 7 photos that I thought would be fun to share.

Popping over to Instagram, I hit the `+` symbol at the bottom of the app and am greeted with a grid of options on the bottom third of the screen with the currently selected photo taking up ~55%. None of the photos I selected in Google Photos are visible. At the top I notice a dropdown that says “Gallery”. I tap it and am greeted with a long list of items including Videos, Instagram, IMG_20180120_162026, Hangouts, FaceApp, Download Camera, 100APPLE, Other…, Photos, Twitter, Other Photos, Allo Images, and a few more options. Some of these I can guess what they are, others are less obvious. The option “Other Photos” appear to be a weird mix of screenshots, gifs, and scans. “Photos” appears to match what’s in “Gallery”. The APPLE ones seem to be a mix of photos from my old iPhone. None of them, from what I can tell, have any ability to give me the 7 photos I selected in Google Photos.

I hop back over to Google Photos and attempt to share from the app. Selecting a single photo will allow me to share with Instagram as a post, but as soon as I select multiple photos, the option disappears and is instead replaced with a DM link instead. Presumably that would send a link to a user of my choice to the Google Photos album.

This is the first major roadblock I hit. I’m not going to scroll through the entire gallery to find the correct 7 photos I want to post. Even if I did do that, the UX would be miserable as well because selecting multiple photos on Instagram is generally an annoying experience. 

My new goal becomes figuring out how to get these 7 photos as the first ones that appear when you open Instagram. To do this, I download the album to my PC. I unzip the photos and then upload them right back to Google Photos. I’m greeted with an option to add to album or to share. I add them to a new album called “delete”. Back in the main view of the app, the photos I just uploaded aren’t present. They’re in the album, but they’ve been sorted based on the date they were taken. 

I remember that photos have EXIF data stored with them, so I attempt to remove the EXIF data. First I copy the files to new ones. This does not remove the data. After some googling, I learn you can go to the properties of a photo, navigate to details, and click “Remove Properties and Personal Information”. There’s an option to make a copy of the photo and remove as much information as possible. I do that and now I have copies of the 7 photos in the same folder. These copies are then uploaded to Google Photos. 

I’m expecting these photos to be the first 7 that appear in the “Photos” tab within Google Photos. Contrary to expectations, only three appear. This is deeply frustrating. I immediately want to see what’s different about those photos that would cause Google Photos to organize them in an unexpected order. The mission then becomes how do I find my most recently uploaded photos. Nothing in the main UI indicates how I might do that. The hamburger menu is unhelpful. I search for “recent” and get no results. “Recently added” returns no results. “Latest” gives me two photos that don’t appear to be connected to that word in any way whatsoever. I happen to click to the “X” button on my search and realize that some options pop up when there is no text in the search bar. This wasn’t obvious to me because I typed my initial query and hit enter rather quick.

In the third modal-esque box I see Videos, Selfies, Movies, Animations, and Show More. Clicking “Show More” drops down a bunch more options and at the bottom I see “Recently Added”. Clicking this shows all of the photos I was hoping to find. The url has the word “\_tra\_” after `/search/`, but searching for “\_tra\_” returns no results as does searching for “tra”.

Clicking on a photo that showed up in the past in the timeline reveals that Google Photos still has the original date the photo was taken. When I look at the properties of the photo on windows I see that the Created, Modified, and Accessed dates are all today’s date. It’s unclear to me why there is this discrepancy. I’m guessing there’s something in the EXIF data that I’m not aware of, but I don’t know how to fix it. Even more frustrated, I proceed to manually change the date on the photos that retained the original date. Now within the web version of Google Photos, I see all of the photos at the top of the page under “Today”. My assumptions here are that these will now sync to Google Photos on my phone and then I will be able to upload them to Instagram. 

On my phone (Pixel 2XL), these photos don’t appear. As a user, I want to force a sync to occur. On my PC I do a hard refresh (Control + Shift + R) and confirm that the photos are there. On my phone, I close all apps, restart my phone, and even turn sync on and off and the photos don’t appear. Going into Instagram, I don’t see these photos on any of the options. 

At this point I’m becoming frustrated and angry. I almost stop trying to make this happen but I want to keep going because the photos are meaningful to me and I legitimately want to share them. My sisters probably don’t remember some of these photos and I think they’d like it. My wife notices I’m upset and after telling her my frustrations, she suggests I just text them to myself. To me that’s a ridiculous way of doing it because, after all, there must be a better way. But unfortunately, I know it will work. So I do it anyways. 

I open Google Inbox and use hangouts to type in my phone number and open a new chat window. I copy the photos from my PC into the chat and text them to myself. 

> Sidebar: Trying to recreate the chain of events for this post leads me to another quirk. Evidently, my phone number is different in Google’s eyes when I include the country code (+1) or not. With it included I’m now in a pending state on my PC where it’s saying the invite is pending. On my phone, I see the chat with my number and the country code at the top and a message displaying “+1<my number> hasn’t accepted your invitation”. Digging a little deeper, I find that I have a separate hangout for my phone number without the country code. This is correctly associated with my name and Project Fi account. I don’t know what to even make of this.

Now that the photos are on my phone, I proceed to manually download each photo under the triple dot option at the top and “Save Media”. Evidently, these go directly to my Google Photos library, which, after all of this, is surprising to me. I do this for each of the seven photos and they all successfully appear at the top of my Google Photos library and at the top of the options list when I’m in Instagram. I then am able to proceed to crafting a multi-photo post.

---
This entire process is insane and I feel like it should not be happening in 2018. It seems crazy to me that a simple task like “choose multiple photos from the primary photo app on a flagship phone and share them on Instagram” is such a complicated process. I get it, Google and Facebook are two big competing companies with different goals. But the difficulty and lack of interoperability between them make me hate them both. This process has left me with so many questions.

Why was this so difficult to do?

Is this really such an uncommon thing to want to do?

Why can’t I directly share motion photos on Instagram? This seems like a perfect thing to share!

Why did my PC not properly strip out all data on the photo on some photos but it did on others? Or is this really Google’s fault?

Why are my photos not syncing? (As of this writing, I have a photo I uploaded to Google Photos on my PC that is not on my phone and a photo that I saved to my phone that is not synced to Google Photos on my PC.)

Why don’t products want to give users a “Sync Now” button? (1Password does not want to do this either as it should “just work”).

Why does a modern web app like Google Photos eschew easily accessible and common photo app features like “latest upload”?

What are all of these photo folder options in Instagram? Where can I access those? What does “Gallery” actually mean?

Most of all, why does it feel like these frustrating UX experiences are becoming more common and not less? 

Perhaps I don’t have great data but it certainly _feels_ like the bad experiences are trumping the good ones lately. I do notice good UI and UX when they happen, but the bad UX experiences have stood out so much more to me lately. This isn’t the first bad experience I’ve had but it’s the first one I’ve taken the time to write at length about. There are other experiences I’ve had recently that I’m tempted to write about (Nest’s billing vs home address, student loan refinancing docs, and a billing payment error that requires me to _call them to finish paying_). 

I’m not a UX, design, or even product expert. But I am a tech-savvy consumer and I know that it’s possible to make these experiences better. The technical challenges are solvable, it’s the people and process around these features that have failed. But that’s fixable too, I think. My hope in writing about these is to release some of my own tension about the process and to highlight areas for improvement. Also, I hope to encourage and inspire more people to care about the little things more. A little love goes a long way. 
