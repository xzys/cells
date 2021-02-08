import Phaser from 'phaser'
import C from '../services/constantsService'

const radiusFromArea = area => Math.sqrt(area/Math.PI)

// class SyncedSprite extends Phaser.GameObjects.Sprite {
class SyncedSprite extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, pyobj, name, color) {
    super(scene, pyobj.position.x, pyobj.position.y)
    this.pyobj = pyobj

    this.radius = radiusFromArea(this.pyobj.size)
    this.displayCircle = scene.add.circle(
      pyobj.position.x, pyobj.position.y,
      this.radius,
      color,
    )
  }

  // initialize after body is created
  init() {
    this.setCircle(this.radius, -this.radius, -this.radius)
    this.sync()
  }

  sync() {
    const center = this.body.center
    this.displayCircle.x = center.x
    this.displayCircle.y = center.y
    this.pyobj.position.set(center.x, center.y)
  }
  
  destroy() {
    this.displayCircle.destroy()
    super.destroy()
  }
}

class Nutrient extends SyncedSprite {
  constructor(scene, pyobj) {
    super(scene, pyobj, 'nutrient', C.colors.NUTRIENTS)
  }
}

class Cell extends SyncedSprite {
  constructor(scene, pyobj) {
    super(scene, pyobj, 'cell', C.colors.CELLS)

    this.setInteractive({
      hitArea: this.displayCircle,
      hitAreaCallback: Cell.GetContains(5), // 
      useHandCursor: true,
    })
    this.selected = false
  }

  // arc don't have a native contains method, also build in a buffer area
  static GetContains(buffer) {
    return (arc, x, y) => {
      return (x**2 + y**2) <= (arc.radius + buffer)**2
    }
  }

  sync() {
    this.radius = radiusFromArea(this.pyobj.size)
    this.setCircle(this.radius, -this.radius, -this.radius)
    this.displayCircle.radius = this.radius
    super.sync()
  }

  processDest(scene) {
    if (this.pyobj.cell.dest) {
      const mass = this.pyobj.size * this.pyobj.size_coeff
      const speed = this.body.velocity.length()
      const decelDist = speed * mass / (this.pyobj.max_accel / mass)

      const target = new Phaser.Math.Vector2(this.pyobj.cell.dest.x, this.pyobj.cell.dest.y)
        .subtract(this.body.center)
        .subtract(this.body.velocity.clone().scale(decelDist))

      /*
      scene.glayer.lineStyle(1, 0x000000)
      scene.glayer.beginPath()
      scene.glayer.moveTo(this.body.center.x, this.body.center.y)
      scene.glayer.lineTo(this.body.center.x + target.x, this.body.center.y + target.y)
      scene.glayer.closePath()
      scene.glayer.strokePath()
      */

      const dist = target.length()
      const force = target.normalize().scale(Math.min(this.pyobj.max_accel, dist * mass))

      this.setAcceleration(force.x / mass, force.y / mass)
    } else {
      this.setAcceleration(0, 0)
    }
  }

  render(t, graphics) {
    // draw destination
    if (this.pyobj.cell.dest) {
      graphics.lineStyle(0.5, C.colors.BLACK)
      graphics.beginPath()
      graphics.moveTo(this.body.center.x, this.body.center.y)
      graphics.lineTo(this.pyobj.cell.dest.x, this.pyobj.cell.dest.y)
      graphics.closePath()
      graphics.strokePath()
    }

    // console.log('ts', t % period);
    // draw circle around this if selected
    if (this.selected) {
      const period = 1000,
            minRadius = 4,
            fxRadius = 10

      const fx = ((t % period) / period) * fxRadius,
            alpha = (1 - (fx/fxRadius))**2

      graphics.lineStyle(1, C.colors.SELECTION, alpha)
      graphics.beginPath()
      graphics.arc(
        this.body.center.x, this.body.center.y,
        this.radius + minRadius + fx,
        0,
        Math.PI * 2,
      )
      graphics.strokePath()
    }
  }
}

export {
  Nutrient,
  Cell,
}
