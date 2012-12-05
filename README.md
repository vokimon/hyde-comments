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
the author of an equivalent extension for [Jeckyll][Jeckyll] (Ruby based alter ego of Hyde).

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

- Posts include comments information provided as separate comment files
	- Comment files (.comment) can be placed anywhere in the content folder.
	- They are related to their post assigning 'comment.meta.thread' to 'post.meta.id'
	- Templates can acces the list of post comments by accessing 'post.comments'
- Nested comments:
	- Comments are nested assigning 'child.meta.inreplyto' to 'parent.meta.id'
	- Top level comments just set 'child.meta.inreplyto' to the post id.
	- Children comments are available as 'parent.meta.children'
- Comment template with stylable classes
- Disabling or enabling comments in a post via meta.comment = True/False
- Author avatars
	- Gravatar based on 'authoremail' if available.
	- Configurable [fallback gravatar](http://en.gravatar.com/site/implement/images/)
	- Explicit avatar from either 'image' or 'avataruri' metas.
- Comment submission form (a web 1.0 one :-( )
- Comment submission backend in php, that sends the comment file back to the author.
	- The author has to save it and regenerate the web site.
	- You can place the backend in a different hosting if you want. Just change the submission URI in 'meta.comment_handler_uri':.
	- Light-coupled: It is easily reimplementable in whatever language/framework your hosting allows.
	- If you want to automate more things, like regeneration or comment storage, all futs under the same API.
- Post generation depends on its comments.
- Fixed: Links are not generated when no author website is provided.


What is to be implemented (TO-DO's):

- AJAX based comment submission form
- Generation can be threaded but there is no means yet to submit threaded comments by replying a given comment
- Adding optional avatar field (upload or uri?)
- Disabling comments submission via 'meta.commentsclosed' = True
- Security concerns on comment content
	- Strip html tags
	- Spam links
	- Email addresses
- Spam tools
	- Moderation by accepting a checksum
	- Pre-moderation with akismet
- Unassisted automatic generation
- Client side rendering
	- Generation of json data for comments
	- Regeneration of comment index json files when moderated
	- Dynamically building comments with javascript
	- Combine it with existing comments
	- JSON data tolerance (don't destroy existing comments when JSON data is missing)
- Pingback
- Likes

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

This part of the comment system requires server side scripting at least to receive the comments.
But the use of static web generators is often motivated by reasons such as:

* Reducing the server load.
* Being able to place the web whatever the languages provided by a given hosting.

The first motivation discourages the use of heavy duty server scripts.
The second one discourages from attaching the user to a given language and framework setup.

Nevertheless many users that are happy with that if some tasks are being conveniently automated.

We are not that constrained if we realize that:

- Adding a comment is an infrequent task compared to page views, so the load is less than the one of a dynamic website if you want to compare with that.
- We can place the submission script in a different host than the static website. Hosting restrictions and load can be reduced that way.
- If they are simple enough, we can provide, with the same API, different back-ends that do different things using different technologies.

So what kind of things could do a back-end:

- Sending an attached comment file by mail to the author so that she can store it and regenerate the website by hand.
- Storing the comment on the site and notifying the author so that she can regenerate the blog.
- Storing and regenerating the blog (convenient but dangerous)
- Validating the author email (sending an email to the author so she can confirm the comment via a confirmation url)
- Filtering for spam with Akismet or similar
- Log-in, account management...



[Hyde]: http://ringce.com/hyde
[Disqus]: http://disqus
[JeckyllStaticCommentsPost]: http://hezmatt.org/~mpalmer/blog/2011/07/19/static-comments-in-jekyll.html
[Jeckyll]: http://jekyllrb.com/
[JSON]: http://json.org
[GitHupHydeComments]: https://github.com/vokimon/hyde-comments



