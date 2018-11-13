s_section_title = {
    'font-family': 'Lato, sans-serif',
    'font-size': 30,
    'color': '#007592',
    'font-weight': 'bold',
    'background': 'radial-gradient(circle at left, #FFFFFF 25%, #007592 100%)',
    'margin-top': 40,
    'margin-bottom': 20,
    'padding': 10
}


def s_subsection_title(l=25):
    return {
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

def s_table(*args):
    s = {
        'width': '100%',
        'table-layout': 'fixed'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s


def s_td(*args):
    s = {
        'font-size': '12px',
        'color': '#515151',
        'text-align': 'center',
        'border': 'none',
        'padding': 0,
        'border-right': 'solid 1px #E0E0E0'
    }

    for arg in args:
        s[arg[0]] = arg[1]

    return s
