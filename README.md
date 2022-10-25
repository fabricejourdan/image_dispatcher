# Image Dispatcher

The images to dispatch must be copied in `to_dispatch/`

You must modify the list of LABELS in `app.py` file 

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
python app.py
```

Once the app is running, point your browser to `localhost:5000` or `l127.0.0.1:5000`. This will show images to dispatch.
`Reload` is used to reload images from the `to_dispatch/` directory.
`Dispatch` is used to create all the `ClassI` or `Incorrect` folder and move files in the corresponding folder.


Use Dockerfile to build the application image

docker build . -t image_dispatcher:latest

And run it

docker run --rm -it -p 5000:5000 --user=42420:42420 image_dispatcher:latest









Miscellaneous :

app.run() --> flask run --host 0.0.0.0 --port 5000 

Dockerfile
EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]

sudo docker run -it -p 5000:5000 -d flask-app

docker containers ls


