from hyde.plugin import Plugin
import re


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
		self._stripMeta = re.compile(
			r"^\s*(?:---|===)\s*\n((?:.|\n)+?)\n\s*(?:---|===)\s*\n*",
			re.MULTILINE)

	def begin_site(self) :
		comments = {}
		def appendComment(c) :
			thread = metaData(c, "thread", "inreplyto")
			if thread not in comments : comments[thread] = []
			comments[thread].append(c)
		for r in self.site.content.walk_resources() :
			if r.source_file.kind != 'comment' : continue
			if r.meta.id in comments :
				raise ValueError(
					"Repeated comment id '%s' in comments %s and %s" %(
						r.meta.id, r, comments[r.meta.id],))
			r.is_processable = False
			r.meta.listable=False
			r.uses_template=False
			text = r.source_file.read_all()
			match = re.match(self._stripMeta, text)
			r.text = text[match.end():]
			appendComment(r)
		self.site.comments = comments

	def begin_text_resource(self, resource, text) :
		if resource.source_file.kind == 'comment': return
		if 'id' not in resource.meta.to_dict() : return
		comments = self.site.comments.get(resource.meta.id,[])
		resource.ncomments = len(comments)
		resource.comments = comments




