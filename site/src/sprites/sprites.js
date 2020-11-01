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

  sync() {
    if (this.pyobj.size <= 0) {
      this.displayCircle.destroy()
      this.destroy()
      return
    }

    this.radius = radiusFromArea(this.pyobj.size)
    this.setCircle(this.radius, -this.radius, -this.radius)

    const center = this.body.center
    this.displayCircle.x = center.x
    this.displayCircle.y = center.y
    this.displayCircle.radius = this.radius

    this.pyobj.position.set(center.x, center.y)
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
  }

  processDest() {
    if (this.pyobj.cell.dest) {
      const mass = this.pyobj.size * this.pyobj.size_coeff
      const speed = this.body.velocity.length()
      const decelDist = speed / (this.pyobj.max_accel / mass)

      const target = new Phaser.Math.Vector2(this.pyobj.cell.dest.x, this.pyobj.cell.dest.y)
        .subtract(this.body.center)
        .subtract(this.body.velocity.clone().scale(decelDist))

      const dist = target.length()
      const force = target.normalize().scale(Math.min(this.pyobj.max_accel, dist * mass))

      this.setAcceleration(force.x / mass, force.y / mass)
    } else {
      this.setAcceleration(0, 0)
    }
  }
}

export {
  Nutrient,
  Cell,
}
