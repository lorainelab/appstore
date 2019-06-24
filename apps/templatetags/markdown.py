from django import template
import markdown
register = template.Library()


def markdown_parser(value):
    html_body = markdown.markdown(value, safe_mode=True)
    html_body = html_body.replace('[HTML_REMOVED]', '')
    return html_body


register.filter('markdown_parser', markdown_parser)
