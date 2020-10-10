class MainScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor('#e5f1e3')
  }

  update(time, delta) {
    // 
  }

  syncWorld() {
    // this.nutrients = this.add.group()
  }
}

export default MainScene
