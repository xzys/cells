<template>
  <div id="game"></div>
</template>

<script>
import Phaser from 'phaser';
import BootScene from './scenes/BootScene'
import MainScene from './scenes/MainScene'

export default {

  mounted() {
    const config = {
      type: Phaser.AUTO,
      parent: 'game',
      width: 800,
      height: 600,
      physics: {
        default: 'arcade',
        arcade: {
          // debug: true
        }
      },
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.NO_CENTER,
      },
      scene: [
        BootScene,
        MainScene
      ]
    }

    const game = new Phaser.Game(config)
  }
}
</script>
