import { Nutrient, Cell } from '../sprites/sprites'

const playerScript = `
# print('cell pos', cell.position)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        print(found.position)
        break

if cell.size > 60:
    cell.divide()
`

class MainScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor('#e5f1e3')

    // camera controls
    const cursors = this.input.keyboard.createCursorKeys()
    this.cameraControls = new Phaser.Cameras.Controls.FixedKeyControl({
        camera: this.cameras.main,
        left: cursors.left,
        right: cursors.right,
        up: cursors.up,
        down: cursors.down,
        zoomIn: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.Q),
        zoomOut: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E),
        speed: 0.5
    })

    const codeInput = document.getElementById('code')
    // TODO allow user to run their own code
    // preload this script
    codeInput.value = playerScript
    
    const runSingleplayer = pyodide.pyimport('run_singleplayer')

    this.nutrients = this.physics.add.group()
    this.cells = this.physics.add.group({
        bounceX: 1,
        bounceY: 1,
    })

    this.world = runSingleplayer(
      this.sys.game.config.width,
      this.sys.game.config.height,
      codeInput.value,
      this,
    )

    this.physics.add.collider(this.cells, this.cells)
    this.physics.add.collider(this.cells, this.nutrients)
  }

  addCell(c) {
    this.cells.add(new Cell(this, c))
  }

  addNutrient(n) {
    this.nutrients.add(new Nutrient(this, n))
  }

  update(time, delta) {
    this.cameraControls.update(delta)
    this.world.update(time, delta / 50)
    for (const c of this.cells.children.entries) {
      c.processDest()
      c.sync()
    }
    for (const n of this.nutrients.children.entries) {
      n.sync()
    }
  }

  destory() {
    for (const n of this.nutrients.children.entries) {
      n.pyobj.destory()
    }
    for (const c of this.cells.children.entries) {
      c.pyobj.destory()
    }
    super.destroy()
  }
}

export default MainScene
