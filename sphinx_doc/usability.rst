
# DJANGO-BLAST DASHBOARD DESIGN

What follows are the key-points of my guide to usability when 
creating a Web site.  It underlies and influences almost every 
design decision that involves layout, navigation, structure, 
look and feel.  

Please feel free to critique it so I can amend it and we can 
share a common set of guidelines on which to base our new 
dashboard.  

Usability is just common sense, so much of what follows may sound
obvious.  

## Usability

### The Average User.  

Even if the actual audience is composed of highly educated people, it 
pays to assume that the audience is: the average user (AU). 

The actual Average User is kept in a hermetically sealed vault at the 
International Bureau of Standards in Geneva. 
It's a person of average intelligence, or even a tad below.  

The AU's motto is:  ***DON'T MAKE ME THINK***

AUs don't read they scan.  

AUs don't look for correct choices, they muddle through (let's make muddling through easy)

A bit like the dog-owner admonishing Spot to leave the garbage can alone; 
the dog only hears: blah, blah, blah, Spot, blah, blah, blah, Spot, blah.  

The Web developer sees in his web pages a product brochure, The AU
sees billboards at 60 mph (let's give them billboards).  

AU gets it, life is good.  

From here on I will call the AU simply, 'user' or 'users.'


 
People, including Web developers, want to innovate. Nobody gets an award for 
following conventions. However, refrain! And follow established conventions.
(Like nav bars on top or left, 

Follow established conventions 



#### Creating a visual hierarchy


##### Keep visual noise down: 

- Too many elements clamoring for attention. Bright colors, exclamation points, animation, etc.
- Disorganization.  Does your page look like a ransacked room?  
- Clutter.  Think Google 

##### Format test for easy scanning  

- Use plenty of headings and put time into writing them
- No floting headers and if using header levels make them easy to distinguish.
- Keep paragraphs short
- Anything that can be put into a bullet list, probably should be (with extra space between items).  
- Don't highlight too many thing, but higlight key words and phrases.


#### Clicking 

Make clickables obvious and consistent, same color or shape.  

How many clicks to a page seems like a useful metric, but in fact 
what matters more is how hard each click is: the amount of thought required 
and the amount of uncertainty about whether I am making the right choice.  

Rule of thumb:
```
Three mindless unambiguous clicks equal one click that requires thought. 
```

After clicking...  "Am I in the right place?"  


Don't present all clickable options at once if each requires more than just a click. 


When theire is a complicated decision provide unavoidable help in the right place and the right time

London streets provide a good example of good help (for tourists unfamiliar with British quirks):

Brief, timely, unavoidable:

![alt text](http://static.panoramio.com/photos/large/52105275.jpg "Good help")


### Omit ~~Needless~~ Words 

Krug's Third Law of Usability:

> Get rid of half the words in a page, and then get rid of half of what's left

Do be ruthless.  


### Happy talk must die.  

No happy talk (you know... "Welcome to..." and a voice inside goes "blah, blal, blah).  


### Instructions  must die.  

Users don't read, they muddle through, remember?  


## Navigation and Home Page: Things you must get right

And you may find yourself in a beautiful house, with a beautiful wife...
And you may ask yourself, How did I get here?  

Cater for two kinds of users, search-dominant, and link-dominant  

At Sears, search dominant ask the first clerk they see... "Where are the power tools?" 
link-dominant look at the signs above the isles.  

According to their frame of mind or level of urgency users will look for a search box or will 
click on a section. 

Unlike traveling physical spaces, in a web site it's hard to accumulate a sense of 
orientation. Hence, there is no department store navigation, but we have web navigation.  

The Home Page is like the North Star.  Being able to get back to it gives you a fresh start.  

The obvious goal of navigation is to find what we are looking for and tell us where we are. 
But navigation can and should do more.  

By making the hierarchy visible it tells us what the sit contains. Navigation reveals content. 

Done correctly, navigation gives us implicitly all the instructions we need (which is good because 
users will ignore other instructions, anyway) 

Persistent Navigation says: "Navigation is over here, it may vary depending where you are 
but it will always be here and work he same way."  

Navigation in avery page (almost) gives confirmation that you are still in the same site, which is
more important than one might think.  And you only have to figure out how it works once. 

Navigation can be reduced or omitted in the presence of forms to fill in, like registration, feedback, 
profile preferences, etc., though, it is still useful to have a home link and to utilities to help fill 
the form.  

Persisten Navigation elements: 

- Site Id (clickable logo) 
- Sections (content hierarchy top level: i.e., home, products, Support, About) 
- Utilities (not part of content hierarchy: i.e., Sign in/Register, Account, Contact, Help) 
- Search (text box and button with 'Search' or magnifying glass)

Site Id logo, on every page (upper left corner), no exceptions.  Users expect the Site Id logo to 
be a link to the home page. 

Include navigation on pages at all levels, not only the first two or three levels.  

Utilities slightly less prominent that Sections and only about 4 or 5 most often used.  
Leftovers belong in the small text links of the footer.  

Have sample pages for all navigation levels before any concerns about color scheme. 

Every page needs a name, in the right place of the visual hierarchy. It should appear to be framing
the content. The name must be prominent (size, color, typeface) as the heading for the page. The 
name must match the words clicked to get there.  If the link of button reads "Sushi Rolls" it 
should take me to a page named "Sushi Rolls."  It's a tacit contract with the visitor, and violations
lead to loss of trust.  

Have the equivalent of "You are here" in a national park, by highlighting (i.e., different color AND
         
bold text) the current location in navigation bars, lists, or menus tha appear on the page.  

Don't make these indicators too subtle.  Subtlety is the mark of sophistication, but not in Web design; 
users in a hurry miss subtle indicators.  

Use breadcrumbs, that is, show the the path from the home page to where you are and make it easy to move
up to higher levels in the hierarchy.  They are self-explanatory and don't take much room. 

Breadcrumbs: 

- Put them at the top.
- Use '>' between the levels.
- Boldface the last item (name of the current page). 

Tabs: One of the few physical metaphors that actually works in a user interface. 

- They are self-evident
- Hard to miss.
- Slick and efficient. 

Do them right. 

The active tab must pop out at you. Give a different color or contrast and it has to physically connect 
with the space below.  


The Blindfold Test.  

You are blindfolded and when you can see again you see a page anywhere in the site:

You should be able to answer these questions without hesitation: 

- What site is this? (Site Id)
- What page am I on? (Page name)  
- What are the major sections of this site? (Sections) 
- What are my options at this level? (Local navigation)
- How can I search?

How to do the test.  

1. Choose a page and print it. 
2. Hold it at arms length so you can't really study it closely. 
3. As quickly as possible, try to find and circle each of this items.

   - Site Id.
   - Page Name.
   - Sections. 
   - "You are here" indicator. 
   - Search

Ask others to do other pages.  


Home Page has to accomodate. 

- Site identity and mission. 
- Site hierarchy (content: What can I find here? and features: What can I do here?) 
- Search
- Teases (entice with hints of the good stuff inside) 
- Feature promos (invite to explore additional sections or try new features).
- Timely content (frequently updated content. Signs of life).  
- Shorcuts (to most frequently requested pieces).
- Registration
- Show me what I am looking for. 
- And what I am not looking for (but may be interested in) 
- Show me where to start. 
- Establish credibility and trust (No second chance to make a good first impression) 

Constrain: Everybody wants a piece of it... like waterfront property.   

Beware of: Design by stakeholders - then your home page may well include:

- Letter from the president
- Headquarters photo
- Mission/Philosophy statement
- Press releases
- Virtual tour. 

Remember The Sixth Sense?  ("I see dead people...")  

In some home pages:  "I see stakeholders..."  

Stakeholders need to be educated about the danger of overgrazing the home page and 
offered other methods of driving traffic. 

Beware of: Too Many Cooks -  Everybody, even the CEO, has an opinion about it.  

One Size Fits All: The home page has to appeal to all who visit the site.

The home page can't do it all: It involves compromise.  

Don't lose this: Conveying the Big Picture. (It has to make clear what the site is) 

Needs to answer four questions: 

- What is this? 
- What do they have here? 
- What can I do here? 
- Why should I be here--and not somewhere else?  

At a glance, with little effort. 

Like the Big Bang, the first few seconds are critical.  

Not everybody enters the site through the home page. A user clicks a link in an email 
to a page deep in a site, and...  

...that is what persistent navigation is for.  They can always jump to the home page 
get their bearings.

How to get the message across:

- The Tagline (visually connected to the Site Id - Nothing beats a good tagline [No one else could use it but you]) 
    - Zipcar - wheels when you need them
    - Opentable - Restaurant Reservations * Free * Instant * Confirmed
    - www.fueleconomy.gov - the official US government source for fuel economy information
- The Welcome Blurb (No mission statement, but a terse,  prominent description of the site that catches the eye) 
- The "Learn more." (when it requires a fair amount of explanation)

A tagline is not a motto ("To Protect and Serve" - a guiding principle) a tagline conveys a value proposition.  
Use as much space as necessary to get the message across. Fight excuses, like:

- You can't imagine that anybody doesn't kow what this site is.
- Others clamor to use the home page for other purposes.  (Good luck) 

But keep it SHORT.  

Additonally, a home page should say with confidence: 

- Here is where to start if I want to search. 
- Here is where to start if I want to browse 
- Here is where to start if I want to sample their best stuff. 

Home page design may involve religious debates where nobody is going to change their mind, 
and the perennial struggle between art and commerce (farmers and cowmen vs.  the railroad barons?)  
Endorphins are involved.  

Then it turns to what "most users like" in the belief users are like *anything*. 

I must come clean: There is no Average User. 

All Web users are unique and all web use is basically idiosyncratic.  

What works is good, integrated design that fills a need, carefully thought out, well executed and tested. 

Testing answers the important question of whether we created a good experience for most people who are likely 
to use *this* site. There is no substitutei for it.    


## Usability Testing 
