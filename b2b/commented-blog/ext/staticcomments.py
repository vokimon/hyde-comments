from hyde.plugin import Plugin


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
		except AttributeError, e :
			if e.args[0] != attribute : raise
	raise AttributeError(
		"Comment %s should define any metadata attributes of %s"%(
			r, ", ".join(args)))

class CommentsPlugin(Plugin) :
	def __init__(self, site) :
		super(CommentsPlugin, self).__init__(site)

	def begin_site(self) :
		comments = []
		for r in self.site.content.walk_resources() :
			if r.source_file.kind != 'comment' : continue
			r.is_processable = False
			r.meta.listable=False
			r.uses_template=False
			if r.meta.id in comments :
				raise ValueError(
					"Repeated comment id '%s' in comments %s and %s" %(
						r.meta.id,
						r,
						comments[r.meta.id],
						))
			comments.append(r)
		self.site.comments = comments

	def begin_text_resource(self, resource, text) :
		if resource.source_file.kind == 'comment': return
		if 'id' not in resource.meta.to_dict() : return
		comments = []
		for comment in self.site.comments :
			if comment.meta.thread == resource.meta.id : 
				comments.append(comment)
		resource.ncomments = len(comments)




