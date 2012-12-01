from hyde.plugin import Plugin

class CommentsPlugin(Plugin) :
	def __init__(self, site) :
		super(CommentsPlugin, self).__init__(site)
		print "= initializing", self.__class__.__name__

	def begin_site(self) :
		for r in self.site.content.walk_resources() :
			if r.source_file.kind != 'comment' : continue
			r.is_processable = False

