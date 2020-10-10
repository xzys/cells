class BootScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'BootScene' })
  }

  preload() {
    this.loadPyodide().then(() => {
      console.log('finished');
      this.scene.start('MainScene');
    })
  }

  loadPyodide() {
    return new Promise((resolve, reject) => {
      const scriptUrl = 'pyodide/pyodide.js'
      window.languagePluginUrl = 'pyodide/'
      const script = self.document.createElement('script');
      script.src = scriptUrl;
      script.onload = () => {
        languagePluginLoader.then(resolve)
      }
      script.onerror = reject
      document.head.appendChild(script);
    })
  }
}

export default BootScene
