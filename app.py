import argparse
import os
import shutil
from sys import platform

import yaml
from PIL import Image
from flask import Flask, render_template, redirect, current_app, send_file

from pager import Pager


def getImageProperties(image_path):
    # print('getImageProperties image_path:', image_path)
    img = Image.open(image_path)
    image_name = os.path.basename(image_path)
    extension = os.path.splitext(image_path)[-1][1:].lower()
    image_width, image_height = img.size
    image_size = os.path.getsize(image_path)
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
    # print('getImageProperties image_properties:', image_properties)
    return image_properties


def load_images(directory):
    # print('load_images - directory:', directory)
    image_list = []
    files = os.listdir(directory)
    for file in files:
        if file.lower().endswith(('.jpg', '.png', 'jpeg')):
            print('load_images - image file :', file)
            properties = getImageProperties(directory + '/' + file)
            image_list.append(properties)
        # else:
        #     print('load_images - not image file :', file)
    # print('load_images - image_list:', image_list)
    return image_list


def load_conf_file(config_file):
    # print('load_conf_file - config_file:', config_file)
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    application_conf = config[0]["application"]
    # print('load_conf_file - application_conf:', application_conf)

    port = 5000
    if "port" in application_conf:
        port = int(application_conf['port'])
    if port < 5000 or port > 5010:
        port = 5000
    application_conf['port'] = port
    if "folder" not in application_conf:
        print("'folder' must be defined in the configuration file :", config_file)
    if "user" not in application_conf:
        print("'user' must be defined in the configuration file :", config_file)
    if "labels" not in application_conf:
        print("'labels' must be defined in the configuration file :", config_file)
    labels = application_conf['labels']
    if len(labels) == 0:
        print("'labels' must be list at least 1 category, check your configuration ile :", config_file)
    return application_conf


def generate_counters(images, labels):
    counters = {}
    counters['nb_images_restant_a_trier'] = 0
    counters['nb_images_a_trier'] = 0
    for i, label in enumerate(labels):
        counters[label[0]] = 0
    for image in images:
        counters['nb_images_a_trier'] += 1
        label_string = image['label'].strip()
        if label_string == '':
            counters['nb_images_restant_a_trier'] += 1
        else:
            counters[label_string] += 1
    print("counters:", counters)
    return counters


def create_app(config):
    STATIC_FOLDER = '.'

    folder = config['folder']
    string_labels = config['labels']

    LABELS = [[x.strip().capitalize(), 0] for x in string_labels]
    LABELS.append(['Incorrect', 0])

    app = Flask(__name__, static_folder=STATIC_FOLDER)
    app.config['APPNAME'] = "Image Dispatcher"
    if config['user']:
        app.config['APPNAME'] += ' (user: ' + config['user'].upper() + ')'
    app.config['folder'] = folder
    app.config['table'] = load_images(folder)
    app.config['pager'] = Pager(len(app.config['table']))

    # first create the route
    @app.route('/display_image/<path:filepath>')
    def display_image(filepath):
        print('xxx:', filepath)
        if 'win' not in platform.lower():
            if filepath[0] != '/':
                filepath = '/' + filepath
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
            counters = generate_counters(current_app.config['table'], LABELS)
            for i, label in enumerate(LABELS):
                label_string = label[0]
                LABELS[i][1] = counters[label_string]
            return render_template(
                'imageview.html',
                index=ind,
                pager=current_app.config['pager'],
                data=current_app.config['table'][ind],
                counters=counters,
                labels=LABELS)

    @app.route('/<int:ind>/<int:cla>/')
    def label(ind=None, cla=None):
        print('label - ind :', ind, ' - cla :', cla)
        print('label - current data 1:', current_app.config['table'][ind])
        label = ''
        if cla > 0 and cla <= len(LABELS):
            label = LABELS[cla - 1][0]
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
        counters = generate_counters(current_app.config['table'], LABELS)
        for i, label in enumerate(LABELS):
            label_string = label[0]
            LABELS[i][1] = counters[label_string]
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            counters=counters,
            labels=LABELS)

    @app.route('/dispatch/')
    def dispatch():
        print('dispatch')
        for i, label in enumerate(LABELS):
            sub_folder = app.config['folder'] + '/' + label[0]
            if not os.path.exists(sub_folder):
                os.makedirs(sub_folder)
                print('dispatch - create directory ', sub_folder)
        for tab in current_app.config['table']:
            if tab['label'] != '':
                original = app.config['folder'] + '/' + tab['name']
                target = app.config['folder'] + '/' + tab['label'] + '/' + tab['name']
                shutil.move(original, target)
                print('dispatch - move file ', original, '->', target)
        current_app.config['table'] = load_images(app.config['folder'])
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
        counters = generate_counters(current_app.config['table'], LABELS)
        for i, label in enumerate(LABELS):
            label_string = label[0]
            LABELS[i][1] = counters[label_string]
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            counters=counters,
            labels=LABELS)

    @app.route('/reload/')
    def reload():
        print('reload')
        tmp_table = current_app.config['table']
        current_app.config['table'] = load_images(app.config['folder'])
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
        counters = generate_counters(current_app.config['table'], LABELS)
        for i, label in enumerate(LABELS):
            label_string = label[0]
            LABELS[i][1] = counters[label_string]
        return render_template(
            'imageview.html',
            index=ind,
            pager=current_app.config['pager'],
            data=current_app.config['table'][ind],
            counters=counters,
            labels=LABELS)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Dispatcher')
    parser.add_argument("-c", "--config", help="config file to instanciate the dispatcher", default='./config.yaml')
    args = parser.parse_args()
    print('args:', args)

    application_conf = load_conf_file(args.config)
    app = create_app(application_conf)

    port = int(application_conf["port"])
    # print('port:', port)
    app.run(debug=True, host='0.0.0.0', port=port)
