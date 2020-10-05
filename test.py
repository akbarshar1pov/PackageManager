import io
import tarfile
from main import load


def open_tar_gz_package(url):
    data = load(url)
    obj = io.BytesIO(data)
    tar = tarfile.open(fileobj=obj)
    return tar


if __name__ == '__main__':
    meta_url = open_tar_gz_package('https://files.pythonhosted.org/packages/4d/70/fd441df751ba8b620e03fd2d2d9ca902103119616f0f6cc42e6405035062/pyrsistent-0.17.3.tar.gz#sha256=2e636185d9eb976a18a8a8e96efce62f2905fea90041958d8cc2a189756ebf3e')
    print(meta_url)
