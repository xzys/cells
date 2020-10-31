<template>
  <div class="game-container fixed top-0 left-0">
    <div id="game"></div>
    <div class="fixed top-0 right-0 mr-8 mt-8 font-mono text-xs"
      id="debug-text">Loading...</div>
  </div>
</template>

<script>
import Phaser from 'phaser';
import BootScene from './scenes/BootScene'
import MainScene from './scenes/MainScene'

import eventService from './services/eventService'

export default {
  data() {
    return {
      game: null
    }
  },
  created() {
    const config = {
      type: Phaser.AUTO,
      parent: 'game',
      width: 800,
      height: 600,
      physics: {
        default: 'arcade',
        arcade: {
          // debug: true
          isPaused: true,
        }
      },
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.NO_CENTER,
      },
      scene: [
        BootScene,
        MainScene
      ],
      events: {
        bus: eventService.bus
      },
    }
    // dont bind to vue to avoid performance hit
    window.game = new Phaser.Game(config)
  }
}
</script>

<style lang="sass">

.game-container
  width: 100% !important
  height: 100% !important
  background: #e5f1e3

</style>
