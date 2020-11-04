import Phaser from 'phaser'
import { Nutrient, Cell } from '../sprites/sprites'
import C from '../services/constantsService'
import eventService from '../services/eventService'

class MainScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MainScene' })
  }

  preload() {}

  create() {
    this.cameras.main.setBackgroundColor(C.colors.BACKGROUND)
    this.cameras.main.setBounds(0, 0, C.worldSize, C.worldSize)
    this.cameras.main.centerOn(C.worldSize/2, C.worldSize/2)

    // camera controls
    const cursors = this.input.keyboard.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.UP,
      down: Phaser.Input.Keyboard.KeyCodes.DOWN,
      left: Phaser.Input.Keyboard.KeyCodes.LEFT,
      right: Phaser.Input.Keyboard.KeyCodes.RIGHT,
    })
    this.cameraControls = new Phaser.Cameras.Controls.FixedKeyControl({
      camera: this.cameras.main,
      left: cursors.left,
      right: cursors.right,
      up: cursors.up,
      down: cursors.down,
      // zoomIn: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.Q),
      // zoomOut: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E),
      speed: 0.5
    })

    this.debugText = document.getElementById('debug-text')
    this.debugTextUpdated = Date.now()

    // setup world
    const runSingleplayer = window.pyodide.pyimport('run_singleplayer')
    this.nutrients = this.physics.add.group()
    this.cells = this.physics.add.group({
      bounceX: 1,
      bounceY: 1,
    })

    this.world = runSingleplayer(C.worldSize, this)

    this.physics.add.collider(this.cells, this.nutrients)
    this.physics.add.collider(this.cells, this.cells) 

    // setup event handlers
    eventService.bus.on(eventService.events.MODIFY_SCRIPT, this.onCodeChange, this)
    eventService.bus.on(eventService.events.PLAY_WORLD, this.onPlay, this)
    eventService.bus.on(eventService.events.PAUSE_WORLD, this.onPause, this)
    eventService.bus.emit(eventService.events.ON_READY, true)
    this.physicsInitialized = false
  }

  /* event handlers */
  onPause() {
    this.physics.world.isPaused = true
  }
  onPlay() {
    this.physics.world.isPaused = false
  }
  onCodeChange(script) {
    this.world.update_script(script)
  }

  /* called from python world to sync state */
  addCell(c) {
    this.cells.add(new Cell(this, c))
  }
  addNutrient(n) {
    this.nutrients.add(new Nutrient(this, n))
  }
  delNutrient(n) {
    this.nutrients.children.entries.forEach(n2 => {
      if (n2.pyobj === n) {
        n2.destroy()
      }
    })
  }

  /* game loop */
  update(time, delta) {
    // TODO for some reason, sprites are moving some after init
    if (!this.physicsInitialized) {
      this.cells.children.entries.forEach(c => c.init())
      this.nutrients.children.entries.forEach(n => n.init())
      this.physicsInitialized = true
    }

    if (!this.physics.world.isPaused) {
      this.world.update(time, delta)
      for (const c of this.cells.children.entries) {
        c.processDest()
        c.sync()
      }
      this.repelCells(delta)
    }

    this.cameraControls.update(delta)
    if (Date.now() - this.debugTextUpdated > 250) {
      this.debugText.textContent = (
        `FPS: ${(1000/delta).toFixed(3)}\n` +
        `${this.cells.children.entries.length} cells`)
      this.debugTextUpdated = Date.now()
    }
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
          const speed = C.repelCellForce / Math.max(dist - c1.radius - c2.radius, 0.01)

          const dx = Math.cos(angle) * speed * delta,
                dy = Math.sin(angle) * speed * delta

          c1.setPosition(c1.x + dx, c1.y + dy)
          c2.setPosition(c2.x - dx, c2.y - dy)
        }
      }
    }
  }

  destroy() {
    for (const n of this.nutrients.children.entries) {
      n.pyobj.destroy()
    }
    for (const c of this.cells.children.entries) {
      c.pyobj.destroy()
    }
    this.world.destory()
    super.destroy()
  }
}

export default MainScene
