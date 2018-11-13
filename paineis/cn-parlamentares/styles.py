def header(*args):
    s = {
        'background': '#2eb2ff',
        'background-size': '100% auto',
        'height': 220,
        'margin-top': -10,
        'margin-left': -10,
        'margin-right': -10,
        'padding-left': '5%',
        'padding-right': '5%',
        # 'background-image': "url('http://gitlab.cts.fgv.cloud:3031/visualizations/internal/cn-congresso-em-temas/raw/master/images/header-image.png') "
        'background-image': "url('https://raw.githubusercontent.com/AliferSales/viz-parallel/master/images/header-image-temas.png') "
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def title1(*args):
    s = {
        'color': 'white',
        'font-family': 'Lato, sans-serif',
        'font-size': '50px',
        'padding-top': 40,
        'margin': '0px'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def text1(*args):
    s = {
        'text-align': 'justify',
        'font-size': '15px',
        'font-family': 'Lato, sans-serif',
        'color': '#007592',
        'padding-left': '12',
        'padding-right': '12'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def table(*args):
    s = {
        'width': '100%',
        'table-layout': 'fixed'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def td(*args):
    s = {
        'border': 'none',
        'padding': 0
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def td_filter(*args):
    s = {
        'width': 60,
        'border': 'none',
        'font-size': '15px',
        'color': '#007592'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def td_big_number(*args):
    s = {
        'border': 'none',
        'text-align': 'right',
        'font-family': 'Lato, sans-serif',
        'font-weight': 'bold',
        'color': '#007592',
        'font-size': '60px'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def td_text_big_number(*args):
    s = {
        'border': 'none',
        'text-align': 'left',
        'font-family': 'Lato, sans-serif',
        'font-weight': 'bold',
        'color': '#515151',
        'font-size': '18'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def td_body(*args):
    s = {
        'border': 'none',
        'vertical-align': 'top'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def filter(*args):
    s = {
        'padding-left': '15%',
        'padding-right': '15%'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def body(*args):
    s = {
        'padding-left': '5%',
        'padding-right': '5%'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def section_title(l=25, *args):
    s = {
        'font-family': 'Lato, sans-serif',
        'font-size': 30,
        'color': '#007592',
        'font-weight': 'bold',
        'background': 'radial-gradient(circle at left, #FFFFFF {}%, #007592 100%)'.format(l),
        'margin-top': 40,
        'margin-bottom': 20,
        'padding': 10
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def subsection_title(l=25, *args):
    s = {
        'font-family': 'Lato, sans-serif',
        'font-size': 18,
        'color': '#00B3E0',
        'font-weight': 'bold',
        'text-align': 'left',
        'background': 'radial-gradient(circle at left, #FFFFFF {}%, #00B3E0 100%)'.format(l),
        'margin-top': 40,
        'margin-bottom': 20,
        'padding': 5,
        'padding-left': 10,
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def profile_name(*args):
    s = {
        'font-size': '24px',
        'color': '#007592',
        # 'margin-bottom': 10,
        'font-weight': 'bold'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s
