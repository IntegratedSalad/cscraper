import tornado.ioloop
import tornado.web
import scraper


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("home.html")

	def post(self):

		search = f"{self.get_body_arguments('query')} kraków"
		num_links = int(self.get_body_arguments("numresults"))


def make_app():

	return tornado.web.Application([(r"/", MainHandler)], debug=True)


if __name__ == '__main__':
	app = make_app()
	app.listen(8888)

	tornado.ioloop.IOLoop.current().start()
