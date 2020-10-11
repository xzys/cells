import Phaser from 'phaser';
import BootScene from './scenes/BootScene'
import MainScene from './scenes/MainScene'
import './assets/main.sass'

const config = {
  type: Phaser.AUTO,
  parent: 'game',
  width: 800,
  height: 600,
  scene: [
    BootScene,
    MainScene
  ]
};

const game = new Phaser.Game(config)
