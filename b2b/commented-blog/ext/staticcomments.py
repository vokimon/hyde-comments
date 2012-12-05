from hyde.plugin import Plugin
import re
import hashlib
import urllib


"""
This plugin enables the rendering of static comments,
by making available, as metadata, comment info
stored as independent source files for each comment.
"""


# TOTEST:
# - If inreplyto and thread defined, takes inreplyto as replyto
# - Neither inreplyto nor thread available -> AttributeError
# - Just inreplyto -> thread = inreplyto
# - Just thead -> inreplyto = thread
# - inreplyto and thead -> no change
# - Repeated comment id
# - nested comments
# - ncomments in nested comments
# - meta.comments = True enables them
# - avatar when
#   - valid email
#   - invalid email
#   - explicit image provided
#   - changing default via meta
# - Sorting comments by date
# - Threads
# - Counting despite the threads


class CommentsPlugin(Plugin) :
	def __init__(self, site) :
		super(CommentsPlugin, self).__init__(site)
		self._stripMetaRE = re.compile(
			r"^\s*(?:---|===)\s*\n((?:.|\n)+?)\n\s*(?:---|===)\s*\n*",
			re.MULTILINE)

	def begin_site(self) :

		def contentWithoutMeta(r) :
			text = r.source_file.read_all()
			match = re.match(self._stripMetaRE, text)
			return text[match.end():]

		def commentAvatar(c) :
			if hasattr(c.meta, 'avataruri') and c.meta.avataruri :
				return c.meta.avataruri
			if hasattr(c.meta, 'image') and c.meta.image :
				return c.meta.image
			gravatar_default = c.node.meta.gravatar_default if 'gravatar_default' in c.node.meta else 'mm'
			return gravatarFromEmail(c.meta.authoremail, gravatar_default) or None

		def gravatarFromEmail(email, default='mm', size=32) :
			"""Given an email address composes the gravatar image uri.
			default says which strategy use when not found.
			https://en.gravatar.com/site/implement/images/
			"""
			md5 = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
			return ( "http://www.gravatar.com/avatar/" + md5 + "?"
				+ urllib.urlencode({
					'd':default,
					's':str(32)
					}))

		# compile dicts of posts and comments by id
		comments = {}
		posts = {}
		for r in self.site.content.walk_resources() :
			if r.source_file.kind == 'comment' :
				if 'id' not in r.meta.to_dict() :
					self.logger.debug("Not id for comment %s"%r)
				id = str(r.meta.id)
				if id in comments :
					raise ValueError(
						"Repeated comment id '%s' in comments %s and %s" %(
							id, r, comments[id]))
				comments[id] = r
			else :
				if 'id' not in r.meta.to_dict() : continue
				id = str(r.meta.id)
				if id in posts :
					raise ValueError(
						"Repeated post id '%s' in comments %s and %s" %(
							id, r, posts[id]))
				posts[id] = r

		# Initialize comment related fields on posts
		for post in posts.values() :
			post.ncomments = 0
			post.comments = []

		# Setting computed fields on comments
		for comment in comments.values() :
			comment.thread_children = []
			comment.is_processable = False
			comment.meta.listable=False
			comment.uses_template=False
			comment.text = contentWithoutMeta(comment)
			comment.meta.avataruri = commentAvatar(comment)

		def connectComment(comment, inreplyto) :
			self.logger.debug("Comment found: %s replying %s"%(r,inreplyto))
			if inreplyto in comments :
				comments[inreplyto].thread_children.append(comment)
			elif inreplyto in posts :
				posts[inreplyto].comments.append(comment)
			else:
				raise ValueError(
					"Comment %s refering to an invalid resource '%s'" %(
						r, inreplyto))

		# Build the thread tree
		for comment in comments.values() :
			if 'inreplyto' in comment.meta.to_dict() :
				inreplyto = str(comment.meta.inreplyto)
				connectComment(comment, inreplyto)
			elif 'thread' in comment.meta.to_dict() :
				thread = str(comment.meta.thread)
				connectComment(comment, thread)
				comment.meta.inreplyto = thread
			else :
				raise ValueError(
					"Comment %s is missing either a 'thread' or 'inreplyto' meta attribute to be related"%(
						comment))

		# Sort by date and count comments
		def recursiveSort(comments) :
			for comment in comments :
				recursiveSort(comment.thread_children)
				comments.sort(key=lambda x : x.meta.published)
		def recursiveCount(comments) :
			return sum((recursiveCount(c.thread_children) for c in comments), len(comments))

		def recursiveDepend(post, comments) :
			post.depends.extend( (
				comment.relative_path
				for comment in comments
				if comment.relative_path not in post.depends
				))
			for comment in comments :
				recursiveDepend(post, comment.thread_children)

		for post in posts.values() :
			recursiveSort(post.comments)
			post.ncomments = recursiveCount(post.comments)
			if not hasattr(post, 'depends'):
				post.depends = []
			recursiveDepend(post, post.comments)




