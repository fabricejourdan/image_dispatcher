import argparse
import os
import shutil

from PIL import Image
from flask import Flask, render_template, redirect, current_app, send_file

from pager import Pager


# -f C:\Users\Fabrice\PycharmProjects\xchatchien -p 5001 -l chat,chien -u sarah
# -f C:\Users\Fabrice\PycharmProjects\xvachecochon -p 5002 -l vache,cochon -u fabrice
def getImageProperties(image_path):
    img = Image.open(image_path)
    # print('img:', img.filename)
    image_name = os.path.basename(image_path)
    extension = os.path.splitext(image_path)[-1][1:].lower()
    image_width, image_height = img.size
    image_size = os.path.getsize(image_path)
    # print('image_path:', image_path)
    image_size = str(round(image_size / 1024)) + ' Ko'

    image_properties = dict(
        name=image_name,
        path=image_path,
        extension=extension,
        width=image_width,
        height=image_height,
        size=image_size,
        label=''
    )
    print('getImageProperties:', image_properties)
    return image_properties


def load_images(directory):
    print('load_images - directory:', directory)
    image_list = []
    files = os.listdir(directory)
    for file in files:
        if file.endswith(('.jpg', '.png', 'jpeg')):
            print('load_images - image file :', file)
            properties = getImageProperties(directory + '/' + file)
            image_list.append(properties)
        else:
            print('load_images - not image file :', file)
    print('load_images - image_list:', image_list)
    return image_list


def create_app(args):
    STATIC_FOLDER = '.'

    folder = args.folder
    string_labels = args.labels

    LABELS = [x.strip().capitalize() for x in string_labels.split(',')]
    LABELS.append('Incorrect')

    app = Flask(__name__, static_folder=STATIC_FOLDER)
    app.config['APPNAME'] = "Image Dispatcher"
    if args.user:
        app.config['APPNAME'] += ' (user: ' + args.user.upper() + ')'
    app.config['FOLDER'] = folder
    app.config['table'] = load_images(folder)
    app.config['pager'] = Pager(len(app.config['table']))

    # first create the route
    @app.route('/display_image/<path:filepath>')
    def display_image(filepath):
        return send_file(filepath, as_attachment=True)

    @app.route('/')
    def index():
        return redirect('/0')

    @app.route('/<int:ind>/')
    def view(ind=None):
        print('view - ind :', ind)
        if current_app.config['pager'].count == 0:
            print('view - No images to dispatch')
            message1 = "No images to dispatch"
            message2 = "Copy images on the 'to_dispatch' directory and click on Reload"
            return render_template("error.html",
                                   message1=message1,
                                   message2=message2)
        elif ind >= current_app.config['pager'].count:
            print('view - Image not found')
            message1 = "Image not found"
            message2 = "Click on Home"
            return render_template("error.html",
                                   message1=message1,
                                   message2=message2), 404
        else:
            print('view - current data 2:', current_app.config['table'][ind])
            current_app.config['pager'].current = ind
            return render_template(
                'imageview.html',
                index=ind,
                pager=current_app.config['pager'],
                data=current_app.config['table'][ind],
                labels=LABELS)

    @app.route('/<int:ind>/<int:cla>/')
    def label(ind=None, cla=None):
        print('label - ind :', ind, ' - cla :', cla)
        print('label - current data 1:', current_app.config['table'][ind])
        label = ''
        if cla > 0 and cla <= len(LABELS):
            label = LABELS[cla - 1]
        current_app.config['table'][ind]['label'] = label
        print('label - current data 2:', current_app.config['table'][ind])
        if ind < current_app.config['pager'].count - 1:
            ind += 1
        current_app.config['pager'].current = ind
        if current_app.config['pager'].count == 0:
            message1 = "No images to dispatch"
            message2 = "Copy images on the 'to_dispatch' directory and click on Reload"
            return render_template("error.html",
                                   message1=message1,
                                   message2=message2)
        print('label - new ind :', ind)
        print('label - new data :', current_app.config['table'][ind])
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            labels=LABELS)

    @app.route('/dispatch/')
    def dispatch():
        print('dispatch')
        for label in LABELS:
            sub_folder = app.config['FOLDER'] + '/' + label
            if not os.path.exists(sub_folder):
                os.makedirs(sub_folder)
                print('dispatch - create directory ', sub_folder)
        for tab in current_app.config['table']:
            if tab['label'] != '':
                original = app.config['FOLDER'] + '/' + tab['name']
                target = app.config['FOLDER'] + '/' + tab['label'] + '/' + tab['name']
                shutil.move(original, target)
                print('dispatch - move file ', original, '->', target)
        current_app.config['table'] = load_images(app.config['FOLDER'])
        print('label - new table :', current_app.config['table'])
        current_app.config['pager'] = Pager(len(current_app.config['table']))
        ind = 0
        current_app.config['pager'].current = ind
        if current_app.config['pager'].count == 0:
            message1 = "No images to dispatch"
            message2 = "Copy images on the 'to_dispatch' directory and click on Reload"
            return render_template("error.html",
                                   message1=message1,
                                   message2=message2)
        print('label - new ind :', ind)
        print('label - new data :', current_app.config['table'][ind])
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            labels=LABELS)

    @app.route('/reload/')
    def reload():
        print('reload')
        tmp_table = current_app.config['table']
        current_app.config['table'] = load_images(app.config['FOLDER'])
        reload_table = []
        for tab in current_app.config['table']:
            name = tab['name']
            for sub_tab in tmp_table:
                sub_name = sub_tab['name']
                if name == sub_name:
                    tab['label'] = sub_tab['label']
            reload_table.append(tab)
        current_app.config['table'] = reload_table
        print('label - new table :', current_app.config['table'])
        current_app.config['pager'] = Pager(len(current_app.config['table']))
        ind = 0
        current_app.config['pager'].current = ind
        if current_app.config['pager'].count == 0:
            message1 = "No images to dispatch"
            message2 = "Copy images on the 'to_dispatch' directory and click on Reload"
            return render_template("error.html",
                                   message1=message1,
                                   message2=message2)
        print('label - new ind :', ind)
        print('label - new data :', current_app.config['table'][ind])
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            labels=LABELS)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Dispatcher')
    parser.add_argument("-f", "--folder", help="folder whre images has to be dispatch", required=True,
                        default='/home/onyxia/work/to_dispatch')
    parser.add_argument("-p", "--port", help="folder whre images has to be dispatch", required=True, default=5000)
    parser.add_argument("-l", "--labels", help="labels for dispatching", required=True, default='classe1,classe2')
    parser.add_argument("-u", "--user", help="user of the application instance")
    args = parser.parse_args()
    # print('args:', args)
    app = create_app(args)
    port = int(args.port)
    if port < 5000 or port > 5010:
        port = 5000
    # print('port:', port)
    app.run(debug=True, host='0.0.0.0', port=port)
