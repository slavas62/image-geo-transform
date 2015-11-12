# README #

**image-geo-transform** is server for georeferencing raster images and transforming them to mercator-projected PNG with alpha-channel for display within web maps applications.

## Running ##
Simplest way to run image-geo-transform is run via Docker:

```docker run -e SERVER_URL=http://localhost:8000 -it -p 8000:80 unknownlighter/image-geo-transform```