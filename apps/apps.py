from django.apps import AppConfig
import requests
import appstore.settings as settings

class AppsConfig(AppConfig):
    name = 'apps'

    def ready(self):

        req_css = requests.get(settings.BIOVIZ_REPOSITORY + 'raw/' + settings.BIOVIZ_BRANCH + '/htdocs/css/menu.css')
        req_html = requests.get(settings.BIOVIZ_REPOSITORY + 'raw/' + settings.BIOVIZ_BRANCH + '/htdocs/menu.html')

        css_file = open('static/apps/css/menu.css', 'w')
        html_file = open('templates/menu.html', 'w')

        css_file.writelines(req_css.content.decode("utf-8"))
        css_file.close()

        html_file.writelines(req_html.content.decode("utf-8"))
        html_file.write('<span id="bioviz-url" style="visibility:hidden;">' + settings.BIOVIZ_URL + '</span>')
        html_file.close()
