const libFiles = [
  'lib/__init__.py',
  'lib/cell.py',
  'lib/types.py',
]

class BootScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'BootScene' })
  }

  preload() {
    for (const fn of libFiles) {
      this.load.text(fn, `simulation/${fn}`)
    }
    this.load.text('main.py', 'simulation/main.py')
    window.boot = this
  }

  create() {
    this.loadPyodide().then(() => {
      this.loadSimulation()
      this.scene.start('MainScene');
    })
  }

  loadPyodide() {
    return new Promise((resolve, reject) => {
      const scriptUrl = 'pyodide/pyodide.js'
      window.languagePluginUrl = 'pyodide/'
      const script = self.document.createElement('script');
      script.src = scriptUrl;
      script.onerror = reject
      script.onload = () => {
        languagePluginLoader.then(resolve)
      }
      document.head.appendChild(script);
    })
  }

  loadSimulation() {
    console.log('loading files');
    pyodide.runPython(`
def write_file(fn, contents):
  with open(fn, 'w') as f:
    f.write(contents)`)

    const writeFile = pyodide.pyimport('write_file')
    for (const fn of libFiles) {
      const contents = this.sys.cache.text.get(fn)
      writeFile(fn, contents)
    }
    writeFile.destroy()
    pyodide.runPython(`
import sys
sys.path.append('.')`)
    pyodide.runPython(this.sys.cache.text.get('main.py'))
  }
}


export default BootScene
