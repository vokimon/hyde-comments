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


def metaData(r, *args) :
	for attribute in args :
		try: return r.meta.to_dict()[attribute]
		except KeyError, e :
			if e.args[0] != attribute : raise
	raise AttributeError(
		"Comment %s should define any metadata attributes of %s"%(
			r, ", ".join(args)))


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

		def appendComment(c) :
			thread = metaData(c, "thread", "inreplyto")
			if thread not in comments : comments[thread] = []
			comments[thread].append(c)

		def commentAvatar(c) :
			if hasattr(c.meta, 'avataruri') and c.meta.avataruri :
				return c.meta.avataruri
			if hasattr(c.meta, 'image') and c.meta.image :
				return c.meta.avataruri
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
			if r.meta.id in comments :
				raise ValueError(
					"Repeated comment id '%s' in comments %s and %s" %(
						r.meta.id, r, comments[r.meta.id],))
			r.is_processable = False
			r.meta.listable=False
			r.uses_template=False
			r.text = contentWithoutMeta(r)
			r.meta.avataruri = commentAvatar(r)
			appendComment(r)
		self.site.comments = comments

	def begin_text_resource(self, resource, text) :
		if resource.source_file.kind == 'comment': return
		if 'id' not in resource.meta.to_dict() : return
		comments = self.site.comments.get(resource.meta.id,[])
		resource.ncomments = len(comments)
		resource.comments = comments




