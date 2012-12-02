hyde-comments: Static comments for Hyde static web generator
============================================================

What?
-----

This is an extension of [Hyde] static web generator to incorporate
comments into your blog post while retaining both data and
simple server requirements.

The idea is that comments are stored as plain text files along
with your post text files and they are combined either on
generation time or in rendering time using JavaScript.

This extension is in early stage and many things are to be defined.
You can participate on the decisions by contributing.

Why?
----

Most people using static blog generators either don't have comments
or they have to rely on external services such as [Disqus].
Such services allow hosting comments and display them by
adding an static javascript code to your template.

So, why that approach is not enough?
You should read the following [post][JeckyllStaticCommentsPost] by Matt Palmer
the author of an equivalent extension for [Jeckyll] (Ruby based alter ego of Hyde).

In summary:

* I want to have control over my data. I don't want to rely on an external service.
* I want my blogging tools be free software (as in freedom, not gratis)

Documentation
-------------

Currently, the behaviour of the extension is not yet well-defined.
Please, meanwhile rely on the examples which are pretty explanatory and on (glups!) the code.

Status
------

What works:

- Generation of content from comment files
	- Takes comment files (.comment) with metadata for each comment in content folders.
	- Comment count as post metadata 'ncomments'
	- Comments as post metadata 'comments'
	- Nested comments based on 'inreplyto' metadata.
- Author avatars
	- Gravatar based on 'authoremail'
	- Explicit avatar from 'image' or 'avataruri'
- Stylable classes
- Disabling or enabling comments via meta.comment = True/False

What is to be implemented:

- Static generation (pending matter):
	- Generate dependencies on comments
	- Configurable default gravatar mode
	- Configurable message for unable to send more messages
- Comment submission form
	- Submission form with hidden inreplyto and thread
	- Server script (php?) to build the comment file and submit it by email
	- Closing comments (visible but no further submissions accepted)
- Spam tools
	- Moderation by accepting a checksum
	- Pre-moderation with akismet
- Unassisted automatic generation
- On browser rendering
	- Generation of json data for comments
	- Regeneration of comment index json files when moderated
	- Dynamically building comments with javascript
	- Combine it with existing comments
	- JSON data tolerance (don't destroy existing comments when JSON data is missing)

Want to help? [Fork it in GitHub][GitHupHydeComments].

Design forces
-------------

### Comment rendering

How/when to render the comments within a post?

* During blog generation
* On browser via JavaScript

The first option can be implemented by adding special files to the site content,
that can be detected by extension or metadata.
Building the comments as part of the site structure
and rendering them by a template

The second option could be implemented
by placing static [JSON] files for comments on a given URL
and querying them from the post page.
There could be an index JSON file for each post with the URL's of the related comments which could be independent files.

The first option has the drawback that it has to be generated each time a comment is added.
The second option has the drawback that it requires JavaScript and that the crawlers (Google) cannot index comments content.

Also, the JavaScript option can add a feature to auto-reload the comments for updates.
This feature indeed opens a third hybrid option:

* Statically generating comments which are available on generation time and updating them on browser.

This way if there is no JavaScript you still have the comments
crawlers have the static content available for rendering
and users can see the comments without waiting for the site to be regenerated.

### Comment submission

This is the part of the web that requires to be dynamic.
Thus, it should be an small lightweight script if we want to keep in the static generation category.

To my understanding, there are three levels of things that can be done.
Each can be convenient for some users.

1. **Sending an email with the comment file to the author** so that he can moderate it, save it and regenerate the site.
2. **Storing the comment file and noticing the author**.
3. **Storing the comment file, regenerating the site and warn the author**.



[Hyde]: http://ringce.com/hyde
[Disqus]: http://disqus
[JeckyllStaticCommentsPost]: http://hezmatt.org/~mpalmer/blog/2011/07/19/static-comments-in-jekyll.html
[Jeckyll]: http://jekyllrb.com/
[JSON]: http://json.org
[GitHupHydeComments]: https://github.com/vokimon/hyde-comments



