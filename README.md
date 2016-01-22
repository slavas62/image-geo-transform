# README #

**image-geo-transform** is server for georeferencing raster images and transforming them to mercator-projected PNG with alpha-channel for display within web maps applications.

## Running ##
Simplest way to run image-geo-transform is run via Docker:

```
docker run -it -p 8000:80 unknownlighter/image-geo-transform
```

## Usage ##
For getting georeferenced image you should make POST-request with few parameters (source image url and geographic coordinates (must be in WGS 84 coordinate system) for each image corner).

Request:

```
curl -X POST -d 'image_url=http://www.gptl.ru/previews/Kanopus-V1/2015/10/10021349_4.jpg&upper_left_x=-121.6593&upper_left_y=36.1411&upper_right_x=-121.3969&upper_right_y=36.1848&lower_right_x=-121.3457&lower_right_y=35.9818&lower_left_x=-121.6084&lower_left_y=35.9384' http://localhost:8000
```

Response:

```
{
   "result":{
      "web_image":"http://localhost:8000/files/e0c882c950e6176708859c2946e0ba0bb99fb6c6.png",
      "georeferenced_image":"http://localhost:8000/files/e0c882c950e6176708859c2946e0ba0bb99fb6c6.tif"
   },
   "success":true
}
```
Where "georeferenced_image" is GeoTiff-file (without warping), and "web_image" is transformed to EPSG:3857 PNG-file.