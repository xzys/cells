class TestScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor('#ffffff')
    this.ball = this.physics.add.sprite(100, 100)
    this.ball.setCircle(25)
    this.bc = this.add.circle(100, 100, 25, 0x000000) 
  }

  update(time, delta) {
    const radius = (Math.sin(time/1000) + 1) * 12.5
    this.ball.setCircle(radius, -radius, -radius)

    this.bc.x = this.ball.body.center.x
    this.bc.y = this.ball.body.center.y
    this.bc.radius = radius
  }
}

export default TestScene
