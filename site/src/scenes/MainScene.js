class MainScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor('#e5f1e3')

    const runSingleplayer = pyodide.pyimport('run_singleplayer')

    this.world = runSingleplayer(
      this.sys.game.config.width,
      this.sys.game.config.height,
      playerScript
    )

    // link world to sprites
    this.nutrients = this.add.group()
    this.cells = this.add.group()
    for (const n of this.world.nutrients) {
      this.nutrients.add(new Nutrient(this, n))
    }
    for (const c of this.world.players) {
      this.cells.add(new Cell(this, c))
    }
  }

  update(time, delta) {
    this.world.update(time, delta / 50)
    for (const c of this.cells.children.entries) {
      c.sync()
    }
  }
}

const playerScript = `
print('cell pos', cell.position)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        break`

const radiusFromArea = area => Math.sqrt(area/Math.PI)

class Nutrient extends Phaser.GameObjects.Sprite {
  constructor(scene, pyobj) {
    super(scene, pyobj.position.x, pyobj.position.y, 'nutrient')
    this.pyobj = pyobj
    this.circle = scene.add.circle(
      pyobj.position.x,
      pyobj.position.y,
      radiusFromArea(pyobj.size),
      0xa3cd9e
    )
  }

  sync() {
    this.circle.radius = radiusFromArea(this.pyobj.size)
  }
}

class Cell extends Phaser.GameObjects.Sprite {
  constructor(scene, pyobj) {
    super(scene, pyobj.position.x, pyobj.position.y, 'cell')
    this.pyobj = pyobj
    this.circle = scene.add.circle(
      pyobj.position.x,
      pyobj.position.y,
      radiusFromArea(pyobj.size),
      0x35635b
    )
  }

  sync() {
    this.circle.radius = radiusFromArea(this.pyobj.size)
    this.circle.x = this.pyobj.position.x
    this.circle.y = this.pyobj.position.y
  }
}

export default MainScene
