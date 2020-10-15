const radiusFromArea = area => Math.sqrt(area/Math.PI)

class SyncedSprite extends Phaser.GameObjects.Sprite {
  constructor(scene, pyobj, name, color) {
    super(scene, pyobj.position.x, pyobj.position.y, name)
    this.pyobj = pyobj
    this.circle = scene.add.circle(
      pyobj.position.x,
      pyobj.position.y,
      radiusFromArea(pyobj.size),
      color,
    )
  }

  sync() {
    if (this.pyobj.size <= 0) {
      this.destroy()
      return
    }
    this.circle.radius = radiusFromArea(this.pyobj.size)
    this.circle.x = this.pyobj.position.x
    this.circle.y = this.pyobj.position.y
  }
}

class Nutrient extends SyncedSprite {
  constructor(scene, pyobj) {
    super(scene, pyobj, 'nutrient', 0xa3cd9e)
  }
}

class Cell extends SyncedSprite {
  constructor(scene, pyobj) {
    super(scene, pyobj, 'cell', 0x35635b)
  }
}

module.exports = {
  Nutrient,
  Cell,
}
