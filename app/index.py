#!/usr/bin/env python
# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options
# Base System
import os
import logging
from sunlightapi import sunlight, SunlightApiError

sunlight.apikey = '1cb6ab912ecd4b08bfdefe5c16a549d0'
define("port", default=8000, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self,url):
        self.render('templates/index.html')
    

class LocationHandler(tornado.web.RequestHandler):
    def post(self):
        if not self.get_argument('lat',False) or not self.get_argument('lon',False):
            raise tornado.web.HTTPError(400)
            return
        try:
            sunlightLegs = sunlight.legislators.allForLatLong(self.get_argument('lat'),self.get_argument('lon'))
        except SunlightApiError, e:
            if e.message == 'Point not within a congressional district.':
                self.write({'status':'e','error':'Your Location places you outside any known congressional district.'})
            elif e.message == 'Latitude & Longitude must be floating-point values':
                self.write({'status':'e','error':'Your client sent an invalid location'})
            else:
                self.write({'status':'e','error':'Unknown error recieved from Sunlight'})
                logging.error(e.message)
            self.finish()
            return
        legislators = self.parseLegislators(sunlightLegs)
        self.write({'status':'s','data':legislators})
        self.finish()
    
    def parseLegislators(self,sunlightLegs):
        # Parse the full return list from Sunlight
        legs = {}
        legs['house'] = map(self.parseLegislator,filter(lambda x: x.chamber == u'house', sunlightLegs))
        legs['senate'] = map(self.parseLegislator,filter(lambda x: x.chamber == u'senate', sunlightLegs))
        legs['district'] = u"%(state)s District %(district)s" % filter(lambda x: x.chamber==u'house',sunlightLegs)[0].__dict__
        return legs
    
    def parseLegislator(self,sleg):
        # Parse an individual Legislator
        sleg.title = u'%s.'%sleg.title
        leg = {}
        leg['name'] = ' '.join(filter(lambda x: x != '', [sleg.title,sleg.firstname,sleg.middlename,sleg.lastname,sleg.name_suffix]))
        leg['phone'] = sleg.phone
        return leg
    

def main():
    tornado.options.parse_command_line()
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "TmV2ZXJHZXRNZUx1Y2t5Q2hhcm1z",
        "debug": "true",
    }
    application = tornado.web.Application([
        (r"/loc", LocationHandler),
        (r"/(.*?)", MainHandler),
    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
