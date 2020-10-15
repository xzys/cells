import { Nutrient, Cell } from '../sprites/sprites'

const playerScript = `print('cell pos', cell.position)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        break`

class MainScene extends Phaser.Scene {
  constructor(test) {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor('#e5f1e3')

    const codeInput = document.getElementById('code')
    // preload this script
    codeInput.value = playerScript
    // TODO allow user to run their own code
    
    const runSingleplayer = pyodide.pyimport('run_singleplayer')

    this.world = runSingleplayer(
      this.sys.game.config.width,
      this.sys.game.config.height,
      codeInput.value,
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
    for (const n of this.nutrients.children.entries) {
      n.sync()
    }
    for (const c of this.cells.children.entries) {
      c.sync()
    }
  }
}

export default MainScene
