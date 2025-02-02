import Phaser from 'phaser';

const es = {
  bus: new Phaser.Events.EventEmitter(),
  events: {
    ON_READY: 'ON_READY',
    MODIFY_SCRIPT: 'MODIFY_SCRIPT',
    PAUSE_WORLD: 'PAUSE_WORLD',
    PLAY_WORLD: 'PLAY_WORLD',
    SET_DEST: 'SET_DEST',
    SELECT_CELL: 'SELECT_CELL',
    PRINT: 'PRINT',
    ERROR: 'ERROR',
  }
}

// expose to window for easy access from python
window.event_service = {
  emit: (...args) => es.bus.emit(...args),
  events: es.events
}

export default es
