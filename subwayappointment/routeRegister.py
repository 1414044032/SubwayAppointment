# -*- coding: utf-8 -*-
from subwayappointment.api.controller import api
from subwayappointment import app
app.register_blueprint(blueprint=api, url_prefix="/")