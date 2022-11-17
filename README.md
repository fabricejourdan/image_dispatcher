# Image Dispatcher

The Image Dispatcher is a flask application which can be instanciate for several users in order to dispatch images in different folder corresponding to images classes 

Once the app is running, point your browser to `localhost:{port}` or `127.0.0.1:{port}`. This will show images to dispatch.
`Reload` is used to reload images from the `{foldercontainingimagestodispatch}` directory.
`Dispatch` is used to create all the `ClassI` or `Incorrect` folder and move files in the corresponding folder.

## Instal & Running

You can install the dependencies in a conda environment.

```sh
cd image_dispatcher
conda create -n image_dispatcher python==3.9
activate image_dispatcher
conda install --file requirements.txt
```
and run the application 

```sh
cd image_dispatcher
python app.py --config .\config.yaml
```

## Configuration

The config.yaml as follow must contain the folder containing the images to dispatch, 
the port on which the flask application instance will be available (http://localhost:{port} ,
the user name and all the classes/folders where the images will be moved

- application:
    folder: {foldercontainingimagestodispatch}
    port: {port}  
    user: {username}
    labels:
      - Classe1
      - Classe2
      - .........
      - Incorrect
	  
	  
