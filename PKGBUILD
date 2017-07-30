# Work in progress arch linux package build file

# Maintainer: Your Name <youremail@domain.com>
pkgname=python-gcode_gen
pkgver=43b9fff
pkgrel=1
pkgdesc=""
arch=(x86_64)
url=""
license=('GPL')
groups=()
depends=('python', 'python-numpy')
makedepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=(!emptydirs)
install=
source=('git+https://github.com/tulth/gcode_gen.git')
md5sums=('SKIP')

package() {
  cd "$srcdir/gcode_gen"
  python setup.py install --root="$pkgdir/" --optimize=1
}

