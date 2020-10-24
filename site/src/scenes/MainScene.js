import Phaser from 'phaser'
import { Nutrient, Cell } from '../sprites/sprites'
import C from '../constants'

const playerScript = `
# print('cell pos', cell.position)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        break

if cell.size > 100:
   cell.divide()
`

class MainScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor(C.colors.BACKGROUND)

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

    this.debugText = document.getElementById('debug-text')
    this.codeInput = document.getElementById('code')

    // TODO allow user to run their own code
    // preload this script
    this.codeInput.value = playerScript
    
    const runSingleplayer = window.pyodide.pyimport('run_singleplayer')

    this.nutrients = this.physics.add.group()
    this.cells = this.physics.add.group({
      bounceX: 1,
      bounceY: 1,
    })

    this.world = runSingleplayer(
      this.sys.game.config.width,
      this.sys.game.config.height,
      this.codeInput.value,
      this,
    )

    this.physics.add.collider(this.cells, this.nutrients)
    this.physics.add.collider(this.cells, this.cells) 
  }

  update(time, delta) {
    this.world.update(time, delta)
    for (const n of this.nutrients.children.entries) {
      n.sync()
    }
    for (const c of this.cells.children.entries) {
      c.processDest()
      c.sync()
    }
    this.repelCells(delta)

    this.cameraControls.update(delta)

    this.debugText.textContent = (
      `FPS: ${(1000/delta).toFixed(3)}\n` +
      `${this.cells.children.entries.length} cells`)
  }

  // a repelling force between cells that helps ease the buggy collisions
  repelCells(delta) {
    // replace with efficient code
    for (let i = 0; i < this.cells.children.entries.length; i++) {
      for (let j = i+1; j < this.cells.children.entries.length; j++) {
        const c1 = this.cells.children.entries[i]
        const c2 = this.cells.children.entries[j]

        const dist = Math.sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2)
        if (dist < c1.radius + c2.radius + C.repelCellDist) {
          const angle = Math.atan2(c1.y - c2.y, c1.x - c2.x)
          const speed = C.repelCellForce / (dist - c1.radius - c2.radius)

          const dx = Math.cos(angle) * speed * delta,
                dy = Math.sin(angle) * speed * delta

          c1.setPosition(c1.x + dx, c1.y + dy)
          c2.setPosition(c2.x - dx, c2.y - dy)
        }
      }
    }
  }

  /* called by python world to sync state*/
  addCell(c) {
    this.cells.add(new Cell(this, c))
  }
  addNutrient(n) {
    this.nutrients.add(new Nutrient(this, n))
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
