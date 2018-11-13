import dash_html_components as html
import base64
import requests


def date_to_str_pretty(x):
    if x and x!='presente':
        return '{0}/{1}/{2}'.format(*str(x).split('-'))
    else:
        return x


def html_img(image_path, local=True, style={}):
    """
    Insert a image based on the path of file (with filename included).

    :param image_path: str -- image path
    :param local: bool -- True if image_path refers a local image
    :param style: dict -- HTML style
    :return: html.Img object
    """
    if local:
        encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode()
        src = 'data:image/png;base64,{}'.format(encoded_image)
    else:
        src = image_path
    return html.Img(src=src, style=style)
