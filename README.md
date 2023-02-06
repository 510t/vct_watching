# vct_watching

vct観戦のためのツール

## docker
```sh
docker compose up -d --build
docker compose exec python3 bash
# python -m pip install <package>
docker compose down
```

### jupyter-lab server
```sh
docker run -v $PWD/app:/root/opt -w /root/opt -it --rm -p 7777:8888 vct_watching-python3 jupyter-lab --no-browser --ip 0.0.0.0 --allow-root -b localhost
```
http://127.0.0.1:7777
