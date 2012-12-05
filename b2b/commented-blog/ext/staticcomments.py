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

# TODO:
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

		def metaData(r, *args) :
			for attribute in args :
				try: return r.meta.to_dict()[attribute]
				except KeyError, e :
					if e.args[0] != attribute : raise
			raise AttributeError(
				"Comment %s should define any metadata attributes of %s"%(
					r, ", ".join(args)))

		def contentWithoutMeta(r) :
			text = r.source_file.read_all()
			match = re.match(self._stripMetaRE, text)
			return text[match.end():]

		def appendComment(c) :
			thread = metaData(c, "thread", "inreplyto")
			c.meta.thread = thread
			inreplyto = metaData(c, "inreplyto", "thread")
			c.meta.inreplyto = inreplyto

			if thread not in comments : comments[thread] = []
			comments[thread].append(c)

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

		comments = {}
		for r in self.site.content.walk_resources() :
			if r.source_file.kind != 'comment' : continue
			if 'id' not in r.meta.to_dict() :
				self.logger.debug("Not id for %s"%r)
				continue
			if r.meta.id in comments :
				raise ValueError(
					"Repeated comment id '%s' in comments %s and %s" %(
						r.meta.id, r, comments[r.meta.id],))
			r.is_processable = False
			r.meta.listable=False
			r.uses_template=False
			r.thread_children = []
			r.thread_parent = None
			r.text = contentWithoutMeta(r)
			r.meta.avataruri = commentAvatar(r)
			appendComment(r)
			self.logger.debug("Comment found: %s of thread %s, replying %s"%(r.slug,r.meta.thread,r.meta.inreplyto))
		for thread in comments.values() :
			thread.sort(key=lambda x : x.meta.published)
			def debug(*args): print args; return args
			id_to_comment = dict(( (c.meta.id, c) for c in thread ))
			for comment in thread :
				if comment.meta.inreplyto in id_to_comment :
					self.logger.debug("Children found: %s of %s"%(comment.meta.id, comment.meta.inreplyto))
					parent = id_to_comment[comment.meta.inreplyto]
					parent.thread_children.append(comment)
					thread.remove(comment)
					
		self.site.comments = comments


	def begin_text_resource(self, resource, text) :
		def recursiveCount(comments) :
			return sum((recursiveCount(c.thread_children) for c in comments), len(comments))
		if resource.source_file.kind == 'comment': return
		if 'id' not in resource.meta.to_dict() :
			resource.ncomments = 0
			resource.comments = []
			return
		comments = self.site.comments.get(resource.meta.id,[])
		resource.ncomments = recursiveCount(comments)
		resource.comments = comments




