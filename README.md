```
# install git lfs if needed
sudo apt install git-lfs
git lfs install

# clone the model repo
git clone https://huggingface.co/spaces/patriotyk/styletts2-ukrainian

# run the image, mounting the repo in its /data folder, opening port 8000
# --gpus=all and --runtime=nvidia binds your NVidia GPU to the container
# replace them with --device=/dev/dri for Intel GPUs
docker run \
  -d \
  --name='styletts2-ukrainian-openai-tts-api' \
  --net='bridge' \
  -p '8000:8000/tcp' \
  -v './styletts2-ukrainian/':'/data':'ro' \
  -e 'NVIDIA_VISIBLE_DEVICES'='all' \
  -e 'NVIDIA_DRIVER_CAPABILITIES'='all' \
  --gpus=all \
  --runtime=nvidia \
  'ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest'
```

then in Home Assistant
https://github.com/sfortis/openai_tts
and use the 8000 port endpoint with any api key, any voice, any model
